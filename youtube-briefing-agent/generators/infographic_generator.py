"""
인포그래픽 생성 모듈
HTML/CSS 기반 인포그래픽과 AI 이미지 생성용 프롬프트를 생성합니다.
"""
import sys
import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Windows UTF-8 설정
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import REPORT_TITLE, get_today_output_dir


def generate_html_infographic(
    videos: List[Dict],
    notebooklm_analysis: Optional[str] = None,
) -> Path:
    """
    HTML/CSS 기반 인포그래픽을 생성합니다.

    Args:
        videos: 영상 데이터 리스트
        notebooklm_analysis: NotebookLM 분석 결과

    Returns:
        생성된 HTML 파일 경로
    """
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    output_dir = get_today_output_dir()
    html_path = output_dir / f"{date_str}-infographic.html"

    # 채널별 그룹핑
    channels = {}
    for v in videos:
        ch = v.get("channel_name", "Unknown")
        if ch not in channels:
            channels[ch] = []
        channels[ch].append(v)

    # 채널별 카드 HTML 생성
    channel_cards = ""
    colors = ["#6366f1", "#ec4899", "#14b8a6", "#f59e0b", "#8b5cf6", "#ef4444"]

    for i, (ch_name, ch_videos) in enumerate(channels.items()):
        color = colors[i % len(colors)]
        video_items = ""
        for v in ch_videos:
            title = v.get("title", "제목 없음")
            url = v.get("url", "#")
            lang = v.get("transcript_language", "?")
            chars = len(v.get("transcript", ""))
            video_items += f'''
            <div class="video-item">
                <a href="{url}" target="_blank" class="video-link">{title}</a>
                <span class="video-meta">자막: {chars:,}자 ({lang})</span>
            </div>'''

        channel_cards += f'''
        <div class="channel-card" style="border-left: 4px solid {color};">
            <div class="channel-header">
                <span class="channel-dot" style="background: {color};"></span>
                <h3>{ch_name}</h3>
                <span class="video-count">{len(ch_videos)}개 영상</span>
            </div>
            {video_items}
        </div>'''

    # NotebookLM 분석 섹션
    analysis_section = ""
    if notebooklm_analysis:
        # 간단한 마크다운 → HTML 변환
        analysis_html = notebooklm_analysis.replace("\n", "<br>")
        analysis_section = f'''
        <div class="analysis-box">
            <h2>🤖 AI 종합 분석</h2>
            <div class="analysis-content">{analysis_html}</div>
        </div>'''

    total_chars = sum(len(v.get("transcript", "")) for v in videos)
    total_videos = len(videos)

    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{REPORT_TITLE} - {date_str}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            color: #e2e8f0;
            min-height: 100vh;
            padding: 2rem;
        }}

        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}

        /* Header */
        .header {{
            text-align: center;
            margin-bottom: 2.5rem;
            padding: 2.5rem 2rem;
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }}

        .header h1 {{
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
            letter-spacing: -0.5px;
        }}

        .header .date {{
            font-size: 1.1rem;
            color: #94a3b8;
            font-weight: 300;
        }}

        /* Stats Grid */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin-bottom: 2rem;
        }}

        .stat-card {{
            background: rgba(255,255,255,0.06);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.08);
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(99, 102, 241, 0.15);
        }}

        .stat-number {{
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .stat-label {{
            font-size: 0.85rem;
            color: #94a3b8;
            margin-top: 0.3rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 500;
        }}

        /* Analysis Box */
        .analysis-box {{
            background: rgba(99, 102, 241, 0.08);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
            border: 1px solid rgba(99, 102, 241, 0.2);
        }}

        .analysis-box h2 {{
            font-size: 1.3rem;
            margin-bottom: 1rem;
            color: #a5b4fc;
        }}

        .analysis-content {{
            line-height: 1.8;
            color: #cbd5e1;
            font-size: 0.95rem;
        }}

        /* Channel Cards */
        .channels-section h2 {{
            font-size: 1.4rem;
            margin-bottom: 1.2rem;
            color: #e2e8f0;
            font-weight: 700;
        }}

        .channel-card {{
            background: rgba(255,255,255,0.04);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border: 1px solid rgba(255,255,255,0.06);
            transition: transform 0.2s;
        }}

        .channel-card:hover {{
            transform: translateX(4px);
            background: rgba(255,255,255,0.06);
        }}

        .channel-header {{
            display: flex;
            align-items: center;
            gap: 0.7rem;
            margin-bottom: 1rem;
        }}

        .channel-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            flex-shrink: 0;
        }}

        .channel-header h3 {{
            font-size: 1.1rem;
            font-weight: 600;
            flex: 1;
        }}

        .video-count {{
            font-size: 0.8rem;
            background: rgba(255,255,255,0.1);
            padding: 0.2rem 0.7rem;
            border-radius: 20px;
            color: #94a3b8;
        }}

        .video-item {{
            padding: 0.6rem 0;
            border-bottom: 1px solid rgba(255,255,255,0.04);
        }}

        .video-item:last-child {{
            border-bottom: none;
        }}

        .video-link {{
            color: #a5b4fc;
            text-decoration: none;
            font-weight: 500;
            font-size: 0.95rem;
            transition: color 0.2s;
        }}

        .video-link:hover {{
            color: #c4b5fd;
            text-decoration: underline;
        }}

        .video-meta {{
            display: block;
            font-size: 0.8rem;
            color: #64748b;
            margin-top: 0.2rem;
        }}

        /* Footer */
        .footer {{
            text-align: center;
            padding: 2rem;
            color: #475569;
            font-size: 0.8rem;
            margin-top: 2rem;
        }}

        @media (max-width: 768px) {{
            body {{ padding: 1rem; }}
            .stats-grid {{ grid-template-columns: 1fr; }}
            .header h1 {{ font-size: 1.6rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 {REPORT_TITLE}</h1>
            <div class="date">{date_str}</div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{len(channels)}</div>
                <div class="stat-label">채널</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_videos}</div>
                <div class="stat-label">영상</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_chars:,}</div>
                <div class="stat-label">자막 글자수</div>
            </div>
        </div>

        {analysis_section}

        <div class="channels-section">
            <h2>📺 채널별 영상</h2>
            {channel_cards}
        </div>

        <div class="footer">
            Generated by YouTube Daily Briefing Agent &middot; {now.strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>'''

    html_path.write_text(html, encoding="utf-8")
    print(f"🎨 HTML 인포그래픽 생성 완료: {html_path}")
    return html_path


def generate_ai_image_prompt(
    videos: List[Dict],
    notebooklm_analysis: Optional[str] = None,
) -> Dict:
    """
    AI 이미지 생성용 프롬프트와 데이터를 생성합니다.

    Args:
        videos: 영상 데이터 리스트
        notebooklm_analysis: NotebookLM 분석 결과

    Returns:
        AI 이미지 생성에 필요한 데이터 dict
    """
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    output_dir = get_today_output_dir()

    # 채널별 정보
    channels = {}
    for v in videos:
        ch = v.get("channel_name", "Unknown")
        if ch not in channels:
            channels[ch] = []
        channels[ch].append(v.get("title", ""))

    # 프롬프트 생성
    channel_list = ", ".join(channels.keys())
    video_count = len(videos)
    topics = []
    for v in videos:
        title = v.get("title", "")
        if title:
            topics.append(title)

    topic_str = "; ".join(topics[:8])  # 최대 8개

    prompt = (
        f"Create a modern, sleek infographic poster for a 'YouTube Daily Briefing' dated {date_str}. "
        f"Dark gradient background (deep purple to navy). "
        f"Header: '{REPORT_TITLE}' in large gradient text (purple to pink). "
        f"Show {video_count} videos from {len(channels)} channels: {channel_list}. "
        f"Include colorful stat cards showing channel count, video count. "
        f"Topics covered: {topic_str}. "
        f"Style: glassmorphism cards, modern sans-serif typography, vibrant accent colors "
        f"(indigo, pink, teal, amber). No text overlap. Clean layout. "
        f"Korean text labels. Professional data visualization aesthetic."
    )

    data = {
        "prompt": prompt,
        "date": date_str,
        "output_dir": str(output_dir),
        "image_name": f"{date_str}-infographic",
        "channels": channels,
        "video_count": video_count,
        "analysis_summary": (notebooklm_analysis[:200] if notebooklm_analysis else ""),
    }

    # 프롬프트 파일로도 저장
    prompt_path = output_dir / f"{date_str}-ai-prompt.json"
    prompt_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"🖼️ AI 이미지 프롬프트 생성 완료: {prompt_path}")
    return data
