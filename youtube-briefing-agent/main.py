"""
YouTube Daily Briefing Agent - 메인 오케스트레이터
매일 유튜브 영상을 수집, 분석, 보고서를 생성하는 자동화 에이전트
"""
import sys
import os
import argparse
import traceback
from datetime import datetime
from pathlib import Path

# Windows UTF-8 설정
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# 프로젝트 루트를 path에 추가
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

from config import (
    NOTEBOOKLM_NOTEBOOK_URL,
    HOURS_LOOKBACK,
    REPORT_TITLE,
    ensure_dirs,
    get_today_output_dir,
)


def run_pipeline(
    hours_lookback: int = None,
    skip_notebooklm: bool = False,
    headless: bool = True,
    verbose: bool = False,
):
    """
    전체 브리핑 파이프라인을 실행합니다.

    Args:
        hours_lookback: 몇 시간 이내 영상을 수집할지
        skip_notebooklm: NotebookLM 단계를 건너뛸지
        headless: 브라우저 표시 여부
        verbose: 상세 로그 출력 여부
    """
    if hours_lookback is None:
        hours_lookback = HOURS_LOOKBACK

    ensure_dirs()
    start_time = datetime.now()

    print("=" * 60)
    print(f"  📋 {REPORT_TITLE}")
    print(f"  📅 {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  ⏱️  수집 범위: 최근 {hours_lookback}시간")
    print("=" * 60)

    # ──────────────────────────────────────
    # Phase 1: 영상 수집
    # ──────────────────────────────────────
    print(f"\n{'─'*50}")
    print(f"  Phase 1/4: 📡 유튜브 영상 수집")
    print(f"{'─'*50}")

    try:
        from collectors.youtube_collector import collect_videos
        videos = collect_videos(hours_lookback)
    except Exception as e:
        print(f"\n❌ Phase 1 실패: {e}")
        if verbose:
            traceback.print_exc()
        videos = []

    if not videos:
        print("\n⚠️ 수집된 영상이 없습니다.")
        print("   더 넓은 시간 범위로 재시도하세요:")
        print(f"   python main.py --hours 72")

        # 영상 없어도 빈 보고서는 생성
        from generators.report_generator import generate_briefing_report
        report_path = generate_briefing_report([], None)
        print(f"\n📄 빈 보고서 생성: {report_path}")
        return

    # ──────────────────────────────────────
    # Phase 2: 트랜스크립트 추출
    # ──────────────────────────────────────
    print(f"\n{'─'*50}")
    print(f"  Phase 2/4: 📝 트랜스크립트 추출")
    print(f"{'─'*50}")

    try:
        from extractors.transcript_extractor import extract_all_transcripts
        videos_with_transcripts = extract_all_transcripts(videos)
    except Exception as e:
        print(f"\n❌ Phase 2 실패: {e}")
        if verbose:
            traceback.print_exc()
        videos_with_transcripts = videos  # 트랜스크립트 없이 진행

    # ──────────────────────────────────────
    # Phase 3: NotebookLM 분석
    # ──────────────────────────────────────
    notebooklm_analysis = None

    if not skip_notebooklm and videos_with_transcripts:
        print(f"\n{'─'*50}")
        print(f"  Phase 3/4: 🤖 NotebookLM 분석")
        print(f"{'─'*50}")

        try:
            from analyzers.notebooklm_analyzer import upload_transcripts_and_analyze
            notebooklm_analysis = upload_transcripts_and_analyze(
                videos_with_transcripts,
                headless=headless,
            )
        except Exception as e:
            print(f"\n⚠️ Phase 3 실패 (계속 진행): {e}")
            if verbose:
                traceback.print_exc()
    else:
        if skip_notebooklm:
            print(f"\n⏭️ Phase 3: NotebookLM 분석 건너뜀 (--skip-notebooklm)")

    # ──────────────────────────────────────
    # Phase 4: 보고서 & 인포그래픽 생성
    # ──────────────────────────────────────
    print(f"\n{'─'*50}")
    print(f"  Phase 4/4: 📊 보고서 & 인포그래픽 생성")
    print(f"{'─'*50}")

    # 4a. Markdown 보고서
    try:
        from generators.report_generator import generate_briefing_report
        report_path = generate_briefing_report(
            videos_with_transcripts,
            notebooklm_analysis,
        )
    except Exception as e:
        print(f"\n❌ 보고서 생성 실패: {e}")
        if verbose:
            traceback.print_exc()
        report_path = None

    # 4b. HTML/CSS 인포그래픽
    try:
        from generators.infographic_generator import generate_html_infographic
        html_path = generate_html_infographic(
            videos_with_transcripts,
            notebooklm_analysis,
        )
    except Exception as e:
        print(f"\n❌ HTML 인포그래픽 생성 실패: {e}")
        if verbose:
            traceback.print_exc()
        html_path = None

    # 4c. AI 이미지 프롬프트
    try:
        from generators.infographic_generator import generate_ai_image_prompt
        ai_data = generate_ai_image_prompt(
            videos_with_transcripts,
            notebooklm_analysis,
        )
    except Exception as e:
        print(f"\n❌ AI 이미지 프롬프트 생성 실패: {e}")
        if verbose:
            traceback.print_exc()
        ai_data = None

    # ──────────────────────────────────────
    # 완료 요약
    # ──────────────────────────────────────
    elapsed = (datetime.now() - start_time).total_seconds()
    output_dir = get_today_output_dir()

    print(f"\n{'='*60}")
    print(f"  ✅ 브리핑 생성 완료!")
    print(f"{'='*60}")
    print(f"  ⏱️  소요 시간: {elapsed:.1f}초")
    print(f"  📹 수집 영상: {len(videos)}개")
    print(f"  📝 트랜스크립트: {len(videos_with_transcripts)}개")
    print(f"  🤖 NotebookLM: {'✅ 완료' if notebooklm_analysis else '⏭️ 건너뜀'}")
    print(f"  📁 출력 디렉토리: {output_dir}")
    if report_path:
        print(f"  📄 보고서: {report_path.name}")
    if html_path:
        print(f"  🎨 인포그래픽: {html_path.name}")
    if ai_data:
        print(f"  🖼️ AI 프롬프트: {ai_data.get('image_name', 'N/A')}")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description=f"{REPORT_TITLE} - YouTube Daily Briefing Agent"
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=HOURS_LOOKBACK,
        help=f"수집 시간 범위 (기본: {HOURS_LOOKBACK}시간)",
    )
    parser.add_argument(
        "--skip-notebooklm",
        action="store_true",
        help="NotebookLM 분석 단계를 건너뜁니다",
    )
    parser.add_argument(
        "--show-browser",
        action="store_true",
        help="브라우저를 화면에 표시합니다",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="상세 로그 출력",
    )

    args = parser.parse_args()

    run_pipeline(
        hours_lookback=args.hours,
        skip_notebooklm=args.skip_notebooklm,
        headless=not args.show_browser,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
