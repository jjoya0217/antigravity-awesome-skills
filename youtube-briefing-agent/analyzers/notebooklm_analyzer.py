"""
NotebookLM 분석 모듈
브라우저 자동화로 NotebookLM에 트랜스크립트를 업로드하고 분석합니다.
"""
import sys
import os
import json
import re
import time
from pathlib import Path
from typing import List, Dict, Optional

# Windows UTF-8 설정
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import NOTEBOOKLM_NOTEBOOK_URL, NOTEBOOKLM_SKILL_DIR


def _get_auth_state_path() -> Path:
    """NotebookLM 스킬의 인증 상태 파일 경로를 반환합니다."""
    data_dir = NOTEBOOKLM_SKILL_DIR / "data"
    return data_dir / "browser_state.json"


def _get_chrome_profile_dir() -> Path:
    """NotebookLM 스킬의 Chrome 프로필 디렉토리를 반환합니다."""
    data_dir = NOTEBOOKLM_SKILL_DIR / "data"
    return data_dir / "chrome_profile"


def add_source_to_notebook(
    notebook_url: str,
    source_text: str,
    source_title: str = "YouTube Transcript",
    headless: bool = True,
) -> bool:
    """
    브라우저 자동화로 NotebookLM에 텍스트 소스를 추가합니다.

    Args:
        notebook_url: NotebookLM 노트북 URL
        source_text: 추가할 텍스트 내용
        source_title: 소스 제목
        headless: 브라우저 표시 여부

    Returns:
        성공 여부
    """
    try:
        from patchright.sync_api import sync_playwright
    except ImportError:
        print("❌ patchright가 설치되지 않았습니다.", file=sys.stderr)
        return False

    auth_state = _get_auth_state_path()
    chrome_profile = _get_chrome_profile_dir()

    if not auth_state.exists():
        print("❌ NotebookLM 인증이 필요합니다.", file=sys.stderr)
        print("   notebooklm 스킬의 setup_auth를 먼저 실행하세요.", file=sys.stderr)
        return False

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(chrome_profile),
                headless=headless,
                storage_state=str(auth_state),
                viewport={"width": 1920, "height": 1080},
                args=["--disable-blink-features=AutomationControlled"],
            )

            page = browser.pages[0] if browser.pages else browser.new_page()

            # NotebookLM 노트북 페이지로 이동
            print(f"  🌐 NotebookLM 노트북 접속 중...")
            page.goto(notebook_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)

            # "소스 추가" 버튼 찾기
            print(f"  📎 소스 추가 시도 중... ({source_title})")

            # "Add source" 또는 "소스 추가" 버튼 클릭
            add_btn_selectors = [
                'button:has-text("Add source")',
                'button:has-text("소스 추가")',
                'button:has-text("Add")',
                '[aria-label="Add source"]',
                '[aria-label="소스 추가"]',
                'button.add-source',
            ]

            clicked = False
            for selector in add_btn_selectors:
                try:
                    btn = page.locator(selector).first
                    if btn.is_visible(timeout=2000):
                        btn.click()
                        clicked = True
                        print(f"     ✅ 소스 추가 버튼 클릭")
                        break
                except Exception:
                    continue

            if not clicked:
                # 이미 소스 추가 UI가 보이는지 그냥 진행 시도
                print(f"     ⚠️ 소스 추가 버튼을 찾지 못함, 대체 방법 시도")

            page.wait_for_timeout(2000)

            # "Copied text" 또는 "복사된 텍스트" 옵션 찾기
            text_source_selectors = [
                'button:has-text("Copied text")',
                'button:has-text("복사된 텍스트")',
                ':text("Copied text")',
                ':text("복사된 텍스트")',
                ':text("Paste text")',
                ':text("텍스트 붙여넣기")',
            ]

            for selector in text_source_selectors:
                try:
                    el = page.locator(selector).first
                    if el.is_visible(timeout=2000):
                        el.click()
                        print(f"     ✅ 텍스트 소스 옵션 선택")
                        break
                except Exception:
                    continue

            page.wait_for_timeout(2000)

            # 텍스트 입력 영역에 내용 입력
            # 소스 이름 입력
            name_selectors = [
                'input[placeholder*="name"]',
                'input[placeholder*="이름"]',
                'input[placeholder*="Source name"]',
                'input[aria-label*="name"]',
                'input[aria-label*="이름"]',
            ]

            for selector in name_selectors:
                try:
                    name_input = page.locator(selector).first
                    if name_input.is_visible(timeout=2000):
                        name_input.fill(source_title)
                        print(f"     ✅ 소스 이름 입력: {source_title}")
                        break
                except Exception:
                    continue

            # 텍스트 입력
            text_selectors = [
                'textarea',
                '[contenteditable="true"]',
                'div[role="textbox"]',
                '.text-input',
            ]

            for selector in text_selectors:
                try:
                    text_input = page.locator(selector).first
                    if text_input.is_visible(timeout=2000):
                        # 긴 텍스트는 클립보드를 통해 붙여넣기
                        page.evaluate(
                            f"navigator.clipboard.writeText({json.dumps(source_text)})"
                        )
                        text_input.click()
                        page.keyboard.press("Control+a")
                        page.keyboard.press("Control+v")
                        print(f"     ✅ 트랜스크립트 입력 ({len(source_text):,}자)")
                        break
                except Exception:
                    continue

            page.wait_for_timeout(1000)

            # 삽입/확인 버튼 클릭
            submit_selectors = [
                'button:has-text("Insert")',
                'button:has-text("삽입")',
                'button:has-text("Add")',
                'button:has-text("추가")',
                'button:has-text("Submit")',
                'button[type="submit"]',
            ]

            for selector in submit_selectors:
                try:
                    submit_btn = page.locator(selector).first
                    if submit_btn.is_visible(timeout=2000):
                        submit_btn.click()
                        print(f"     ✅ 소스 추가 제출")
                        break
                except Exception:
                    continue

            page.wait_for_timeout(3000)
            browser.close()
            print(f"  ✅ NotebookLM 소스 추가 완료: {source_title}")
            return True

    except Exception as e:
        print(f"  ❌ NotebookLM 소스 추가 실패: {e}", file=sys.stderr)
        return False


def ask_notebook(
    question: str,
    notebook_url: str = None,
    headless: bool = True,
) -> Optional[str]:
    """
    NotebookLM에 질문하고 답변을 받습니다.

    Args:
        question: 질문 내용
        notebook_url: 노트북 URL (기본: config의 URL)
        headless: 브라우저 표시 여부

    Returns:
        답변 텍스트. 실패 시 None
    """
    if notebook_url is None:
        notebook_url = NOTEBOOKLM_NOTEBOOK_URL

    try:
        from patchright.sync_api import sync_playwright
    except ImportError:
        print("❌ patchright가 설치되지 않았습니다.", file=sys.stderr)
        return None

    auth_state = _get_auth_state_path()
    chrome_profile = _get_chrome_profile_dir()

    if not auth_state.exists():
        print("❌ NotebookLM 인증 필요", file=sys.stderr)
        return None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(chrome_profile),
                headless=headless,
                storage_state=str(auth_state),
                viewport={"width": 1920, "height": 1080},
                args=["--disable-blink-features=AutomationControlled"],
            )

            page = browser.pages[0] if browser.pages else browser.new_page()

            print(f"  🌐 NotebookLM 접속 중...")
            page.goto(notebook_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)

            # 질문 입력
            input_selectors = [
                'textarea[placeholder*="질문"]',
                'textarea[placeholder*="Ask"]',
                'textarea[placeholder*="question"]',
                'textarea',
                '[contenteditable="true"]',
                'div[role="textbox"]',
            ]

            input_found = False
            for selector in input_selectors:
                try:
                    input_el = page.locator(selector).last
                    if input_el.is_visible(timeout=3000):
                        input_el.click()
                        input_el.fill(question)
                        input_found = True
                        print(f"  📨 질문 입력 완료")
                        break
                except Exception:
                    continue

            if not input_found:
                print("  ❌ 질문 입력 필드를 찾을 수 없음", file=sys.stderr)
                browser.close()
                return None

            # Enter로 전송
            page.keyboard.press("Enter")
            print(f"  ⏳ 응답 대기 중...")

            # 응답 대기 (최대 60초)
            page.wait_for_timeout(5000)

            # 응답 텍스트 추출
            response_selectors = [
                '.response-content',
                '.message-content',
                '[data-message-type="response"]',
                '.chat-message:last-child',
            ]

            answer = None
            for _ in range(12):  # 최대 60초 대기
                for selector in response_selectors:
                    try:
                        resp_el = page.locator(selector).last
                        if resp_el.is_visible(timeout=1000):
                            text = resp_el.inner_text()
                            if text and len(text) > 10:
                                answer = text
                                break
                    except Exception:
                        continue

                if answer:
                    break
                page.wait_for_timeout(5000)

            browser.close()

            if answer:
                print(f"  ✅ 응답 수신 ({len(answer):,}자)")
            else:
                print(f"  ⚠️ 응답을 추출하지 못함")

            return answer

    except Exception as e:
        print(f"  ❌ NotebookLM 질문 실패: {e}", file=sys.stderr)
        return None


def upload_transcripts_and_analyze(
    videos_with_transcripts: List[Dict],
    notebook_url: str = None,
    headless: bool = True,
) -> Optional[str]:
    """
    트랜스크립트를 NotebookLM에 업로드하고 브리핑을 생성합니다.

    Args:
        videos_with_transcripts: 트랜스크립트가 포함된 영상 리스트
        notebook_url: NotebookLM 노트북 URL
        headless: 브라우저 표시 여부

    Returns:
        NotebookLM의 분석 결과 텍스트
    """
    if notebook_url is None:
        notebook_url = NOTEBOOKLM_NOTEBOOK_URL

    if not videos_with_transcripts:
        print("⚠️ 업로드할 트랜스크립트가 없습니다.")
        return None

    print(f"\n🤖 NotebookLM 분석 시작...\n")

    # 1. 각 트랜스크립트를 소스로 추가
    uploaded = 0
    for video in videos_with_transcripts:
        title = f"[{video['channel_name']}] {video['title']}"
        transcript = video.get("transcript", "")

        if not transcript:
            continue

        # 트랜스크립트가 너무 길면 앞부분만 사용 (NotebookLM 제한)
        if len(transcript) > 200000:
            transcript = transcript[:200000] + "\n\n... (이후 내용 생략)"

        success = add_source_to_notebook(
            notebook_url=notebook_url,
            source_text=transcript,
            source_title=title,
            headless=headless,
        )

        if success:
            uploaded += 1

    print(f"\n📊 소스 업로드 결과: {uploaded}/{len(videos_with_transcripts)}개 성공\n")

    if uploaded == 0:
        print("⚠️ 업로드된 소스가 없어 분석을 건너뜁니다.")
        return None

    # 2. 브리핑 질문 전송
    briefing_question = """오늘 업로드된 유튜브 영상들을 분석하여 다음 형식으로 데일리 브리핑을 작성해주세요:

1. **종합 요약** (3-5문장): 오늘의 핵심 내용을 요약
2. **채널별 핵심 인사이트**: 각 영상의 핵심 포인트 3개씩
3. **주요 트렌드**: 영상들에서 공통적으로 나타나는 트렌드나 주제
4. **실행 가능한 인사이트**: 바로 활용할 수 있는 실질적인 팁이나 정보
5. **추천 시청 순서**: 시간이 부족한 경우 우선 시청할 영상 순위

한국어로 작성해주세요."""

    print(f"  📨 브리핑 질문 전송 중...")
    answer = ask_notebook(
        question=briefing_question,
        notebook_url=notebook_url,
        headless=headless,
    )

    return answer


if __name__ == "__main__":
    # 테스트: NotebookLM에 간단한 질문
    url = NOTEBOOKLM_NOTEBOOK_URL
    question = sys.argv[1] if len(sys.argv) > 1 else "이 노트북에 어떤 내용이 있나요?"

    print(f"📝 질문: {question}")
    print(f"🔗 노트북: {url}\n")

    answer = ask_notebook(question, url, headless=False)
    if answer:
        print(f"\n📋 답변:\n{answer}")
