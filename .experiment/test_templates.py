#!/usr/bin/env python3
"""
템플릿 구조 테스트 — 외부 의존성 없음 (표준 라이브러리만 사용)

방지 대상:
  1. 플레이스홀더 미치환 (__PLACEHOLDER__ 문자열 렌더링 노출)
  2. f-string 브레이스 누락 ({변수명} 또는 {v["key"]} 잔류)
  3. guide 탭/섹션 DOM 인덱스 불일치
  4. 스냅샷 뷰어 파일 내용 인라인 삽입 (지연 로드 원칙 위반)
  5. HTML 기본 구조 파손 (</html> 누락 등)
  6. 서버 라우트 HTTP 200 확인
"""
import re
import sys
import json
import unittest
import subprocess
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent / "templates"
SERVER_PY = Path(__file__).parent / "server.py"
PORT = 7788


# ─────────────────────────────────────────────────────────────
# 헬퍼
# ─────────────────────────────────────────────────────────────
def load(name: str) -> str:
    return (TEMPLATES_DIR / name).read_text(encoding="utf-8")


class TagCounter(HTMLParser):
    """html/head/body 태그 개수를 센다."""
    def __init__(self):
        super().__init__()
        self.open: dict[str, int] = {}
        self.close: dict[str, int] = {}

    def handle_starttag(self, tag, attrs):
        self.open[tag] = self.open.get(tag, 0) + 1

    def handle_endtag(self, tag):
        self.close[tag] = self.close.get(tag, 0) + 1


# ─────────────────────────────────────────────────────────────
# 1. 플레이스홀더 — snapshot_viewer.html (렌더 전)
# ─────────────────────────────────────────────────────────────
class TestSnapshotViewerTemplate(unittest.TestCase):

    def setUp(self):
        self.html = load("snapshot_viewer.html")

    def test_required_placeholders_present(self):
        """렌더 전 템플릿에 4개 플레이스홀더가 모두 존재해야 한다."""
        for ph in ("__FILES_JSON__", "__MANIFEST_JSON__",
                   "__ROOT_HASH_SHORT__", "__ROOT_HASH__"):
            self.assertIn(ph, self.html, f"플레이스홀더 누락: {ph}")

    def test_no_python_fstring_leakage(self):
        """Python f-string 표현식이 템플릿에 남아있으면 안 된다."""
        # {v["root_hash"]}, {files_json}, {manifest_json} 형태
        bad = re.findall(r'\{(v\[|files_json|manifest_json|root_hash)[^}]*\}', self.html)
        self.assertEqual(bad, [], f"Python f-string 잔류: {bad}")

    def test_render_no_unreplaced_placeholders(self):
        """가짜 데이터로 렌더링한 결과에 __XXX__ 가 남으면 안 된다."""
        fake_files = json.dumps([{"path": "test.md", "hash": "abc123", "content": None}])
        fake_manifest = json.dumps({"test.md": "abc123456789"})
        rendered = (self.html
                    .replace("__FILES_JSON__", fake_files)
                    .replace("__MANIFEST_JSON__", fake_manifest)
                    .replace("__ROOT_HASH_SHORT__", "abc123456789")
                    .replace("__ROOT_HASH__", "abc123456789abcdef"))
        found = re.findall(r'__[A-Z_]+__', rendered)
        self.assertEqual(found, [], f"렌더 후 미치환 플레이스홀더: {found}")

    def test_render_contains_files_data(self):
        """렌더링 결과에 const FILES 선언이 포함되어야 한다."""
        fake_files = json.dumps([])
        fake_manifest = json.dumps({})
        rendered = (self.html
                    .replace("__FILES_JSON__", fake_files)
                    .replace("__MANIFEST_JSON__", fake_manifest)
                    .replace("__ROOT_HASH_SHORT__", "aaa")
                    .replace("__ROOT_HASH__", "aaabbbccc"))
        self.assertIn("const FILES", rendered)

    def test_no_inline_file_contents(self):
        """템플릿에 파일 내용을 직접 삽입하는 패턴이 없어야 한다 (lazy-load 원칙)."""
        # content 필드에 실제 값이 채워진 채 인라인되면 안 됨
        # 허용: "content": null  /  금지: "content": "긴 텍스트..."
        inline = re.findall(r'"content"\s*:\s*"[^"]{20,}', self.html)
        self.assertEqual(inline, [], f"파일 내용 인라인 삽입 의심: {inline[:2]}")

    def test_html_basic_structure(self):
        """최소 HTML 구조 (html/head/body 쌍) 이상이 없어야 한다."""
        p = TagCounter()
        p.feed(self.html)
        for tag in ("html", "head", "body"):
            self.assertEqual(p.open.get(tag, 0), 1, f"<{tag}> 열림 태그 수 이상")
            self.assertEqual(p.close.get(tag, 0), 1, f"</{tag}> 닫힘 태그 수 이상")


# ─────────────────────────────────────────────────────────────
# 2. dashboard.html — 가이드 탭/섹션 DOM 인덱스 일치
# ─────────────────────────────────────────────────────────────
class TestDashboardTemplate(unittest.TestCase):

    def setUp(self):
        self.html = load("dashboard.html")

    def test_guide_tab_section_count_match(self):
        """guide-tab 버튼 수 == guide-section 수 이어야 한다."""
        tabs = re.findall(r'<button[^>]+class="guide-tab[^"]*"', self.html)
        sections = re.findall(r'<div[^>]+class="guide-section[^"]*"', self.html)
        self.assertEqual(len(tabs), len(sections),
                         f"탭 {len(tabs)}개 vs 섹션 {len(sections)}개 불일치")

    def test_guide_tab_onclick_indices_sequential(self):
        """switchGuideTab(n,…) 호출 인덱스가 0부터 순차적이어야 한다."""
        indices = [int(m) for m in re.findall(r'switchGuideTab\((\d+),', self.html)]
        expected = list(range(len(indices)))
        self.assertEqual(indices, expected,
                         f"onclick 인덱스 비순차: {indices}")

    def test_guide_section_ids_match_indices(self):
        """guideTabN id가 탭 순서(N=0,1,…)와 일치해야 한다."""
        ids = re.findall(r'id="guideTab(\d+)"', self.html)
        expected = [str(i) for i in range(len(ids))]
        self.assertEqual(ids, expected,
                         f"guideTab id 순서 이상: {ids}")

    def test_switchGuideTab_function_exists(self):
        """switchGuideTab 함수 정의가 있어야 한다."""
        self.assertIn("function switchGuideTab", self.html)

    def test_project_filter_select_exists(self):
        """레포 필터 셀렉터(projectFilter)가 존재해야 한다."""
        self.assertIn('id="projectFilter"', self.html)

    def test_populate_project_select_function_exists(self):
        """_populateProjectSelect 함수 정의가 있어야 한다."""
        self.assertIn("function _populateProjectSelect", self.html)

    def test_project_charts_canvas_exist(self):
        """레포별 차트 canvas 2개가 있어야 한다."""
        self.assertIn('id="projectCostChart"', self.html)
        self.assertIn('id="projectTurnsChart"', self.html)

    def test_update_badge_exists(self):
        """업데이트 배지 요소가 존재해야 한다."""
        self.assertIn('id="updateBadge"', self.html)

    def test_check_version_function_exists(self):
        """_checkVersion 함수 정의가 있어야 한다."""
        self.assertIn("function _checkVersion", self.html)

    def test_check_version_called_on_init(self):
        """_checkVersion이 페이지 로드 시점에 호출되어야 한다."""
        self.assertIn("_checkVersion()", self.html)

    def test_no_unreplaced_placeholders(self):
        """dashboard.html에는 플레이스홀더가 없어야 한다 (정적 HTML)."""
        found = re.findall(r'__[A-Z_]+__', self.html)
        self.assertEqual(found, [], f"플레이스홀더 잔류: {found}")

    def test_html_basic_structure(self):
        p = TagCounter()
        p.feed(self.html)
        for tag in ("html", "head", "body"):
            self.assertEqual(p.open.get(tag, 0), 1, f"<{tag}> 열림 태그 수 이상")
            self.assertEqual(p.close.get(tag, 0), 1, f"</{tag}> 닫힘 태그 수 이상")


# ─────────────────────────────────────────────────────────────
# 3. harness.html — 기본 구조
# ─────────────────────────────────────────────────────────────
class TestHarnessTemplate(unittest.TestCase):

    def setUp(self):
        self.html = load("harness.html")

    def test_no_unreplaced_placeholders(self):
        # __NULL__ 은 harness.html 에서 jq fallback 값으로 의도적으로 사용됨
        KNOWN_LITERALS = {"__NULL__"}
        found = [p for p in re.findall(r'__[A-Z_]+__', self.html)
                 if p not in KNOWN_LITERALS]
        self.assertEqual(found, [], f"플레이스홀더 잔류: {found}")

    def test_html_basic_structure(self):
        p = TagCounter()
        p.feed(self.html)
        for tag in ("html", "head", "body"):
            self.assertEqual(p.open.get(tag, 0), 1, f"<{tag}> 열림 태그 수 이상")
            self.assertEqual(p.close.get(tag, 0), 1, f"</{tag}> 닫힘 태그 수 이상")


# ─────────────────────────────────────────────────────────────
# 4. 서버 라우트 스모크 테스트 (서버가 실행 중일 때만)
# ─────────────────────────────────────────────────────────────
def _server_running() -> bool:
    try:
        urllib.request.urlopen(f"http://localhost:{PORT}/", timeout=1)
        return True
    except Exception:
        return False


class TestServerRoutes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.running = _server_running()

    def _skip_if_offline(self):
        if not self.running:
            self.skipTest(f"서버가 localhost:{PORT} 에서 실행 중이지 않음 — 스킵")

    def _get(self, path: str, read_all: bool = False) -> tuple[int, bytes]:
        url = f"http://localhost:{PORT}{path}"
        try:
            with urllib.request.urlopen(url, timeout=3) as resp:
                body = resp.read() if read_all else resp.read(8192)
                return resp.status, body
        except urllib.error.HTTPError as e:
            return e.code, b""

    def test_root_200(self):
        self._skip_if_offline()
        status, body = self._get("/", read_all=True)
        self.assertEqual(status, 200)
        self.assertIn(b"</html>", body.lower())

    def test_harness_200(self):
        self._skip_if_offline()
        status, body = self._get("/harness", read_all=True)
        self.assertEqual(status, 200)
        self.assertIn(b"</html>", body.lower())

    def test_snapshots_json(self):
        self._skip_if_offline()
        status, body = self._get("/snapshots", read_all=True)
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertIsInstance(data, list)

    def test_snapshot_nonexist_404(self):
        self._skip_if_offline()
        status, _ = self._get("/snapshot/nonexistent_hash")
        self.assertEqual(status, 404)

    def test_data_endpoint(self):
        self._skip_if_offline()
        status, body = self._get("/data", read_all=True)
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertIn("runs", data)
        self.assertIn("generated", data)


# ─────────────────────────────────────────────────────────────
# 5. version.py — 24h 캐시 TTL 로직 검증
# ─────────────────────────────────────────────────────────────
class TestVersionModule(unittest.TestCase):

    VERSION_PY = Path(__file__).parent / "collectors" / "version.py"

    def setUp(self):
        self.src = self.VERSION_PY.read_text(encoding="utf-8")

    def test_cache_ttl_constant_exists(self):
        """CACHE_TTL 상수가 정의되어 있어야 한다 (throttle 회귀 방지)."""
        self.assertIn("CACHE_TTL", self.src)

    def test_cache_ttl_is_daily(self):
        """CACHE_TTL 값이 86400 (24h) 이어야 한다."""
        m = re.search(r'CACHE_TTL\s*=\s*(\d+)', self.src)
        self.assertIsNotNone(m, "CACHE_TTL 상수를 찾을 수 없음")
        self.assertEqual(int(m.group(1)), 86400, "CACHE_TTL은 86400(24h)여야 함")

    def test_cache_file_path_defined(self):
        """캐시 파일 경로 상수(_CACHE_FILE)가 정의되어 있어야 한다."""
        self.assertIn("_CACHE_FILE", self.src)

    def test_cache_load_and_save_functions_exist(self):
        """_load_cache, _save_cache 함수가 모두 존재해야 한다."""
        self.assertIn("def _load_cache", self.src)
        self.assertIn("def _save_cache", self.src)

    def test_fallback_last_known_exists(self):
        """네트워크 실패 시 폴백(_last_known) 함수가 존재해야 한다."""
        self.assertIn("def _last_known", self.src)

    def test_network_failure_is_silent(self):
        """네트워크 실패 시 예외를 삼키고 조용히 처리해야 한다."""
        # except 블록이 pass 또는 fallback 처리로 끝나야 함 (re-raise 금지)
        self.assertNotIn("raise ", self.src.split("def check_update")[1].split("def ")[0],
                         "check_update 내부에서 예외를 re-raise하면 안 됨")


if __name__ == "__main__":
    unittest.main(verbosity=2)
