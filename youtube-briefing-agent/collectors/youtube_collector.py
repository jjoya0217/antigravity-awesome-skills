"""
YouTube 영상 수집 모듈
RSS 피드를 사용하여 채널별 최신 영상 목록을 수집합니다.
"""
import sys
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from typing import List, Dict, Optional

# Windows UTF-8 설정
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import YOUTUBE_CHANNELS, HOURS_LOOKBACK


def get_channel_id_from_handle(handle: str) -> Optional[str]:
    """
    유튜브 채널 핸들(@handle)로부터 채널 ID를 추출합니다.
    채널 페이지의 HTML에서 channel_id를 파싱합니다.
    """
    # handle에서 @ 제거
    clean_handle = handle.lstrip("@")
    url = f"https://www.youtube.com/@{clean_handle}"

    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        # channel_id 추출 (여러 패턴 시도)
        patterns = [
            r'"channelId"\s*:\s*"(UC[a-zA-Z0-9_-]{22})"',
            r'<meta\s+itemprop="channelId"\s+content="(UC[a-zA-Z0-9_-]{22})"',
            r'"externalId"\s*:\s*"(UC[a-zA-Z0-9_-]{22})"',
            r'/channel/(UC[a-zA-Z0-9_-]{22})',
        ]
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                return match.group(1)

        print(f"  ⚠️ 채널 ID를 찾을 수 없습니다: {handle}", file=sys.stderr)
        return None
    except (URLError, HTTPError) as e:
        print(f"  ❌ 채널 페이지 접근 실패 ({handle}): {e}", file=sys.stderr)
        return None


def fetch_rss_feed(channel_id: str) -> List[Dict]:
    """
    YouTube RSS 피드에서 영상 목록을 가져옵니다.
    """
    rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

    try:
        req = Request(rss_url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=15) as resp:
            xml_data = resp.read().decode("utf-8", errors="replace")

        # XML 파싱
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "yt": "http://www.youtube.com/xml/schemas/2015",
            "media": "http://search.yahoo.com/mrss/",
        }

        root = ET.fromstring(xml_data)
        entries = root.findall("atom:entry", ns)

        videos = []
        for entry in entries:
            video_id_el = entry.find("yt:videoId", ns)
            title_el = entry.find("atom:title", ns)
            published_el = entry.find("atom:published", ns)
            link_el = entry.find("atom:link", ns)

            if video_id_el is None or title_el is None:
                continue

            video = {
                "video_id": video_id_el.text,
                "title": title_el.text,
                "published": published_el.text if published_el is not None else "",
                "url": f"https://www.youtube.com/watch?v={video_id_el.text}",
            }

            # media:group에서 설명 추출
            media_group = entry.find("media:group", ns)
            if media_group is not None:
                desc_el = media_group.find("media:description", ns)
                video["description"] = desc_el.text if desc_el is not None else ""
                thumb_el = media_group.find("media:thumbnail", ns)
                if thumb_el is not None:
                    video["thumbnail"] = thumb_el.get("url", "")

            videos.append(video)

        return videos
    except (URLError, HTTPError) as e:
        print(f"  ❌ RSS 피드 가져오기 실패 ({channel_id}): {e}", file=sys.stderr)
        return []
    except ET.ParseError as e:
        print(f"  ❌ RSS XML 파싱 실패 ({channel_id}): {e}", file=sys.stderr)
        return []


def filter_recent_videos(videos: List[Dict], hours: int = 24) -> List[Dict]:
    """
    지정된 시간 이내에 게시된 영상만 필터링합니다.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    recent = []

    for video in videos:
        pub_str = video.get("published", "")
        if not pub_str:
            continue
        try:
            # ISO 8601 형식 파싱: 2026-02-10T12:00:00+00:00
            pub_date = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
            if pub_date >= cutoff:
                video["published_dt"] = pub_date
                recent.append(video)
        except ValueError:
            continue

    return recent


def collect_videos(hours_lookback: int = None) -> List[Dict]:
    """
    전체 채널에서 최근 영상을 수집합니다.

    Returns:
        채널 정보가 포함된 영상 리스트
    """
    if hours_lookback is None:
        hours_lookback = HOURS_LOOKBACK

    all_videos = []
    print(f"\n📡 유튜브 영상 수집 시작... (최근 {hours_lookback}시간)")
    print(f"   대상 채널: {len(YOUTUBE_CHANNELS)}개\n")

    for channel in YOUTUBE_CHANNELS:
        handle = channel["handle"]
        name = channel["name"]
        print(f"  🔍 [{name}] 채널 검색 중...")

        # 채널 ID 가져오기
        channel_id = get_channel_id_from_handle(handle)
        if not channel_id:
            print(f"     ⚠️ 건너뜀\n")
            continue

        print(f"     채널 ID: {channel_id}")

        # RSS 피드 가져오기
        all_feed_videos = fetch_rss_feed(channel_id)
        print(f"     피드 영상 수: {len(all_feed_videos)}")

        # 최근 영상 필터링
        recent = filter_recent_videos(all_feed_videos, hours_lookback)
        print(f"     최근 {hours_lookback}시간 영상: {len(recent)}개")

        for v in recent:
            v["channel_name"] = name
            v["channel_handle"] = handle
            v["channel_id"] = channel_id
            all_videos.append(v)

        print()

    print(f"✅ 총 수집된 영상: {len(all_videos)}개\n")
    return all_videos


if __name__ == "__main__":
    # 테스트 실행 - 기본 24시간 또는 인자로 지정
    import json

    hours = int(sys.argv[1]) if len(sys.argv) > 1 else HOURS_LOOKBACK
    videos = collect_videos(hours)

    if videos:
        print("\n📋 수집된 영상 목록:")
        for i, v in enumerate(videos, 1):
            print(f"\n  {i}. [{v['channel_name']}] {v['title']}")
            print(f"     URL: {v['url']}")
            print(f"     게시일: {v.get('published', 'N/A')}")
    else:
        print("\n⚠️ 최근에 게시된 영상이 없습니다.")
        # 최근 영상 없어도 피드 전체 확인
        print("\n📋 최근 피드 확인 (시간 제한 없이):")
        all_vids = collect_videos(hours_lookback=999999)
        for i, v in enumerate(all_vids[:5], 1):
            print(f"  {i}. [{v['channel_name']}] {v['title']}")
            print(f"     게시일: {v.get('published', 'N/A')}")
