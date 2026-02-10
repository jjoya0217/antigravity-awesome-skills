"""
YouTube Daily Briefing Agent - Configuration
"""
import os
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────
# 프로젝트 경로
# ─────────────────────────────────────────────
PROJECT_DIR = Path(__file__).parent
SKILLS_DIR = PROJECT_DIR.parent / "skills"
NOTEBOOKLM_SKILL_DIR = SKILLS_DIR / "notebooklm"
YOUTUBE_SUMMARIZER_DIR = SKILLS_DIR / "youtube-summarizer"

OUTPUT_DIR = PROJECT_DIR / "output"
TEMPLATES_DIR = PROJECT_DIR / "templates"
TRANSCRIPTS_DIR = PROJECT_DIR / "transcripts"

# ─────────────────────────────────────────────
# NotebookLM 설정
# ─────────────────────────────────────────────
NOTEBOOKLM_NOTEBOOK_URL = "https://notebooklm.google.com/notebook/11cecca0-e395-4669-b44d-36d1b107a0b1"

# ─────────────────────────────────────────────
# 유튜브 채널 리스트
# ─────────────────────────────────────────────
YOUTUBE_CHANNELS = [
    {
        "name": "AI 투솔",
        "handle": "@ai_tusol",
        "url": "https://www.youtube.com/@ai_tusol",
    },
    {
        "name": "에듀타임즈",
        "handle": "@eduttime",
        "url": "https://www.youtube.com/@eduttime",
    },
    {
        "name": "어센딩인사이트",
        "handle": "@어센딩인사이트",
        "url": "https://www.youtube.com/@%EC%96%B4%EC%84%BC%EB%94%A9%EC%9D%B8%EC%82%AC%EC%9D%B4%ED%8A%B8",
    },
    {
        "name": "Justin Sung",
        "handle": "@JustinSung",
        "url": "https://www.youtube.com/@JustinSung",
    },
    {
        "name": "조코딩",
        "handle": "@jocoding",
        "url": "https://www.youtube.com/@jocoding",
    },
    {
        "name": "스탠리 스튜디오",
        "handle": "@stanleestudio",
        "url": "https://www.youtube.com/@stanleestudio",
    },
]

# ─────────────────────────────────────────────
# 수집 설정
# ─────────────────────────────────────────────
# 최근 N시간 이내 영상만 수집
HOURS_LOOKBACK = 24

# 트랜스크립트 언어 우선순위
TRANSCRIPT_LANGUAGES = ["ko", "en"]

# ─────────────────────────────────────────────
# 보고서 설정
# ─────────────────────────────────────────────
REPORT_TITLE = "유튜브 데일리 브리핑"

def get_today_output_dir():
    """오늘 날짜의 출력 디렉토리 반환"""
    today = datetime.now().strftime("%Y-%m-%d")
    d = OUTPUT_DIR / today
    d.mkdir(parents=True, exist_ok=True)
    return d

def ensure_dirs():
    """필요한 디렉토리 생성"""
    for d in [OUTPUT_DIR, TEMPLATES_DIR, TRANSCRIPTS_DIR]:
        d.mkdir(parents=True, exist_ok=True)
