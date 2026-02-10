"""
유튜브 트랜스크립트 추출 모듈
youtube-transcript-api를 사용하여 영상 자막을 추출합니다.
"""
import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Windows UTF-8 설정
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TRANSCRIPT_LANGUAGES, TRANSCRIPTS_DIR, ensure_dirs


def extract_transcript(video_id: str, languages: List[str] = None) -> Tuple[Optional[str], Optional[str]]:
    """
    유튜브 영상에서 트랜스크립트를 추출합니다.

    Args:
        video_id: 유튜브 영상 ID
        languages: 우선순위 언어 코드 리스트

    Returns:
        (transcript_text, language_code) 튜플. 실패 시 (None, None)
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        print("❌ youtube-transcript-api가 설치되지 않았습니다.", file=sys.stderr)
        print("   pip install youtube-transcript-api", file=sys.stderr)
        return None, None

    if languages is None:
        languages = TRANSCRIPT_LANGUAGES

    try:
        # 사용 가능한 트랜스크립트 확인
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # 수동 자막 우선 시도
        transcript = None
        lang_used = None

        for lang in languages:
            try:
                transcript = transcript_list.find_manually_created_transcript([lang])
                lang_used = lang
                break
            except Exception:
                pass

        # 수동 자막 없으면 자동 생성 자막 시도
        if transcript is None:
            for lang in languages:
                try:
                    transcript = transcript_list.find_generated_transcript([lang])
                    lang_used = lang
                    break
                except Exception:
                    pass

        # 어떤 언어도 못 찾으면 첫 번째 사용 가능한 것 사용
        if transcript is None:
            try:
                for t in transcript_list:
                    transcript = t
                    lang_used = t.language_code
                    break
            except Exception:
                pass

        if transcript is None:
            print(f"  ⚠️ [{video_id}] 사용 가능한 트랜스크립트 없음", file=sys.stderr)
            return None, None

        # 트랜스크립트 가져오기
        entries = transcript.fetch()
        full_text = " ".join([entry.text for entry in entries])

        return full_text, lang_used

    except Exception as e:
        error_msg = str(e)
        if "disabled" in error_msg.lower():
            print(f"  ⚠️ [{video_id}] 자막이 비활성화되어 있습니다", file=sys.stderr)
        elif "not found" in error_msg.lower():
            print(f"  ⚠️ [{video_id}] 트랜스크립트를 찾을 수 없습니다", file=sys.stderr)
        else:
            print(f"  ❌ [{video_id}] 트랜스크립트 추출 오류: {e}", file=sys.stderr)
        return None, None


def save_transcript(video_id: str, text: str, metadata: Dict) -> Path:
    """
    트랜스크립트를 파일로 저장합니다.

    Args:
        video_id: 유튜브 영상 ID
        text: 트랜스크립트 텍스트
        metadata: 영상 메타데이터 (제목, 채널 등)

    Returns:
        저장된 파일 경로
    """
    ensure_dirs()
    filepath = TRANSCRIPTS_DIR / f"{video_id}.txt"

    content = f"# {metadata.get('title', 'Unknown')}\n"
    content += f"채널: {metadata.get('channel_name', 'Unknown')}\n"
    content += f"URL: {metadata.get('url', '')}\n"
    content += f"게시일: {metadata.get('published', 'Unknown')}\n"
    content += f"언어: {metadata.get('language', 'Unknown')}\n"
    content += f"---\n\n"
    content += text

    filepath.write_text(content, encoding="utf-8")
    return filepath


def extract_all_transcripts(videos: List[Dict]) -> List[Dict]:
    """
    여러 영상의 트랜스크립트를 일괄 추출합니다.

    Args:
        videos: 영상 메타데이터 리스트 (collect_videos의 결과)

    Returns:
        트랜스크립트가 추가된 영상 리스트 (성공한 것만)
    """
    results = []
    total = len(videos)
    print(f"\n📝 트랜스크립트 추출 시작... (총 {total}개 영상)\n")

    for i, video in enumerate(videos, 1):
        vid = video["video_id"]
        title = video.get("title", "Unknown")
        channel = video.get("channel_name", "Unknown")
        print(f"  [{i}/{total}] [{channel}] {title}")

        text, lang = extract_transcript(vid)

        if text:
            video["transcript"] = text
            video["transcript_language"] = lang
            video["transcript_length"] = len(text)

            # 파일로 저장
            metadata = {**video, "language": lang}
            filepath = save_transcript(vid, text, metadata)
            video["transcript_file"] = str(filepath)

            print(f"     ✅ 추출 완료 ({lang}, {len(text):,}자)")
            results.append(video)
        else:
            print(f"     ⚠️ 건너뜀")

        print()

    print(f"✅ 트랜스크립트 추출 완료: {len(results)}/{total}개 성공\n")
    return results


if __name__ == "__main__":
    # 테스트: 단일 영상 ID로 트랜스크립트 추출
    if len(sys.argv) < 2:
        print("사용법: python transcript_extractor.py <VIDEO_ID> [LANGUAGE]")
        sys.exit(1)

    video_id = sys.argv[1]
    lang = sys.argv[2] if len(sys.argv) > 2 else None
    langs = [lang, "en"] if lang else TRANSCRIPT_LANGUAGES

    print(f"🔍 영상 ID: {video_id}")
    print(f"   언어 우선순위: {langs}\n")

    text, used_lang = extract_transcript(video_id, langs)
    if text:
        print(f"✅ 추출 완료 (언어: {used_lang})")
        print(f"📊 길이: {len(text):,}자\n")
        print("--- 트랜스크립트 미리보기 (처음 500자) ---")
        print(text[:500])
    else:
        print("❌ 트랜스크립트를 추출할 수 없습니다.")
