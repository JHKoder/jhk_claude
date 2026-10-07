#!/usr/bin/env python3
"""실시간 갱신 리포트 서버 (SSE + HTTP, 표준 라이브러리만 사용)"""
import json
import sys
import time
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent / "collectors"))
from store import (all_runs, all_runs_multi, repo_labels,
                   get_claude_md_snapshots, get_config_versions, get_config_version, rate_run,
                   DB_PATH)
from analyzer import get_latest_analysis, run_analysis, get_analysis_history, get_analysis_by_id
from version import check_update, local_version

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 7788
EXP_DIR = Path(__file__).parent


def build_data() -> dict:
    runs = all_runs_multi()
    snapshots = get_claude_md_snapshots()
    groups: dict[str, list] = {}
    for r in reversed(runs):
        h = r.get("claude_md_hash") or "unknown"
        groups.setdefault(h, []).append(r)
    config_vers = get_config_versions()
    for v in config_vers:
        try:
            v["manifest"] = json.loads(v.get("manifest_json") or "{}")
        except Exception:
            v["manifest"] = {}
    return {
        "runs": runs,
        "groups": {k: [r["id"] for r in v] for k, v in groups.items()},
        "snapshots": snapshots,
        "config_versions": config_vers,
        "projects": repo_labels(),
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "latest_analysis": get_latest_analysis(),
    }


def data_hash(data: dict) -> str:
    return hashlib.md5(
        json.dumps(data["runs"], default=str, sort_keys=True).encode()
    ).hexdigest()


HTML_TEMPLATE = (Path(__file__).parent / "report_template.html").read_text(encoding="utf-8") \
    if (Path(__file__).parent / "report_template.html").exists() else None

TEMPLATES_DIR = Path(__file__).parent / "templates"


def _load_template(name: str) -> str:
    return (TEMPLATES_DIR / name).read_text(encoding="utf-8")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # 로그 억제

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/":
            self._serve_dashboard()
        elif path == "/harness":
            self._serve_harness()
        elif path == "/data":
            self._serve_data()
        elif path == "/events":
            self._serve_sse()
        elif path == "/snapshots":
            self._json(get_config_versions())
        elif path.startswith("/snapshot/") and path.endswith("/files"):
            h = path[len("/snapshot/"):-len("/files")]
            self._serve_snapshot_files(h)
        elif path.startswith("/snapshot/") and path.endswith("/export"):
            h = path[len("/snapshot/"):-len("/export")]
            self._serve_snapshot_export(h)
        elif path.startswith("/snapshot/"):
            h = path[len("/snapshot/"):]
            v = get_config_version(h)
            if not v:
                self.send_response(404)
                self.end_headers()
                return
            import zlib as _zlib
            try:
                content = _zlib.decompress(v["compressed"]).decode("utf-8", errors="replace")
            except Exception:
                content = "(압축 해제 실패)"
            self._serve_snapshot_viewer(v, content)
        elif path == "/version":
            self._json(check_update())
        elif path == "/analyze":
            self._serve_analyze(force=False)
        elif path == "/analyze/force":
            self._serve_analyze(force=True)
        elif path == "/analyze/history":
            self._json(get_analysis_history())
        elif path.startswith("/analyze/"):
            try:
                aid = int(path[len("/analyze/"):])
                result = get_analysis_by_id(aid)
                self._json(result if result else {"error": "not found"})
            except ValueError:
                self._json({"error": "invalid id"})
        elif path.startswith("/turns/"):
            sid = path[len("/turns/"):]
            self._serve_turns(sid)
        elif path == "/api/quality-metrics":
            self._serve_quality_metrics()
        elif path == "/quality-comparison":
            self._serve_quality_comparison()
        elif path.startswith("/rate/"):
            parts = path.strip("/").split("/")
            if len(parts) == 3:
                try:
                    rate_run(int(parts[1]), int(parts[2]))
                    self._json({"ok": True})
                except Exception as e:
                    self._json({"ok": False, "error": str(e)})
            else:
                self._json({"ok": False, "error": "invalid path"})
        else:
            self.send_response(404)
            self.end_headers()

    def _json(self, obj):
        body = json.dumps(obj, ensure_ascii=False, default=str).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_data(self):
        self._json(build_data())

    def _serve_snapshot_files(self, root_hash: str):
        import re as _re, zlib as _zlib
        v = get_config_version(root_hash)
        if not v:
            self.send_response(404)
            self.end_headers()
            return
        try:
            content = _zlib.decompress(v["compressed"]).decode("utf-8", errors="replace")
        except Exception:
            self._json({"error": "decompress failed"})
            return
        manifest = v.get("manifest") or json.loads(v.get("manifest_json") or "{}")
        file_contents: dict[str, str] = {}
        current_path = None
        current_lines: list[str] = []
        for line in content.splitlines():
            m = _re.match(r'^=== (.+?) ===$', line)
            if m:
                if current_path is not None:
                    file_contents[current_path] = "\n".join(current_lines).strip()
                current_path = m.group(1)
                current_lines = []
            else:
                current_lines.append(line)
        if current_path is not None:
            file_contents[current_path] = "\n".join(current_lines).strip()
        files = {p: {"content": file_contents[p], "parse_failed": False}
                    if p in file_contents
                    else {"content": "", "parse_failed": True}
                 for p in manifest}
        self._json(files)

    def _serve_snapshot_export(self, root_hash: str):
        import base64 as _b64
        v = get_config_version(root_hash)
        if not v:
            self.send_response(404)
            self.end_headers()
            return
        payload = {
            "exp_snapshot": "1",
            "root_hash":     v["root_hash"],
            "recorded_at":   v.get("recorded_at", ""),
            "manifest_json": v.get("manifest_json", "{}"),
            "compressed_b64": _b64.b64encode(v["compressed"]).decode(),
            "size_before":   v.get("size_before", 0),
            "size_after":    v.get("size_after", 0),
            "file_count":    v.get("file_count", 0),
        }
        body = json.dumps(payload, ensure_ascii=False).encode()
        filename = f"snapshot-{root_hash[:12]}.snap"
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/snapshot/import":
            self._handle_snapshot_import()
        else:
            self.send_response(404)
            self.end_headers()

    def _handle_snapshot_import(self):
        import base64 as _b64
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            payload = json.loads(body)
            if payload.get("exp_snapshot") != "1":
                self._json({"ok": False, "error": "유효한 .snap 파일이 아닙니다"})
                return
            root_hash    = payload["root_hash"]
            manifest_json = payload["manifest_json"]
            compressed   = _b64.b64decode(payload["compressed_b64"])
            size_before  = int(payload.get("size_before", 0))
            size_after   = int(payload.get("size_after", 0))
            file_count   = int(payload.get("file_count", 0))
        except Exception as e:
            self._json({"ok": False, "error": f"파싱 실패: {e}"})
            return

        from collectors.store import save_config_version
        is_new = save_config_version(
            root_hash=root_hash,
            manifest_json=manifest_json,
            compressed=compressed,
            size_before=size_before,
            size_after=size_after,
            file_count=file_count,
        )
        self._json({"ok": True, "root_hash": root_hash, "is_new": is_new})

    def _serve_turns(self, session_id: str):
        import glob as _glob
        projects_dir = Path.home() / ".claude" / "projects"
        pattern = str(projects_dir / "**" / f"{session_id}.jsonl")
        matches = _glob.glob(pattern, recursive=True)
        if not matches:
            self.send_response(404)
            body = json.dumps({"error": "session jsonl not found"}).encode()
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        turns = []
        try:
            with open(matches[0], encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if obj.get("type") != "assistant":
                        continue
                    msg = obj.get("message", {})
                    usage = msg.get("usage", {})
                    turns.append({
                        "turn": len(turns) + 1,
                        "timestamp": obj.get("timestamp", ""),
                        "model": msg.get("model", ""),
                        "input_tokens": usage.get("input_tokens", 0),
                        "output_tokens": usage.get("output_tokens", 0),
                        "cache_read": usage.get("cache_read_input_tokens", 0),
                        "cache_write": usage.get("cache_creation_input_tokens", 0),
                    })
        except Exception as e:
            self._json({"error": str(e)})
            return
        self._json({"session_id": session_id, "turns": turns})

    def _serve_analyze(self, force: bool = False):
        result = run_analysis(force=force)
        self._json(result)

    def _serve_sse(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Accel-Buffering", "no")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        last_hash = ""
        try:
            while True:
                data = build_data()
                h = data_hash(data)
                if h != last_hash:
                    last_hash = h
                    payload = json.dumps(data, ensure_ascii=False, default=str)
                    msg = f"data: {payload}\n\n".encode()
                    self.wfile.write(msg)
                    self.wfile.flush()
                    # 변경 직후 1초 뒤 한 번 더 확인 (연쇄 변경 빠른 반영)
                    time.sleep(1)
                else:
                    time.sleep(2)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _serve_snapshot_viewer(self, v: dict, content: str):
        import json as _json

        manifest = v.get("manifest") or json.loads(v.get("manifest_json") or "{}")
        # manifest만 인라인 — 파일 내용은 JS에서 /snapshot/<hash>/files 로 lazy fetch
        files_json = _json.dumps(
            [{"path": p, "hash": h[:12], "content": None, "parse_failed": False}
             for p, h in manifest.items()],
            ensure_ascii=False
        )
        manifest_json = _json.dumps(manifest, ensure_ascii=False)
        root_hash_short = v["root_hash"][:12]
        root_hash = v["root_hash"]

        template = _load_template("snapshot_viewer.html")
        body = (template
                .replace("__FILES_JSON__", files_json)
                .replace("__MANIFEST_JSON__", manifest_json)
                .replace("__ROOT_HASH_SHORT__", root_hash_short)
                .replace("__ROOT_HASH__", root_hash))

        b = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _serve_dashboard(self):
        html = _load_template("dashboard.html").encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html)))
        self.end_headers()
        self.wfile.write(html)

    def _serve_harness(self):
        html = _load_template("harness.html").encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html)))
        self.end_headers()
        self.wfile.write(html)

    def _serve_quality_metrics(self):
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                qm.task_id, qm.accuracy, qm.first_pass, qm.revision_count,
                qm.complexity_score, s.output_tokens
            FROM quality_metrics qm
            LEFT JOIN runs s ON qm.session_id = s.session_id
            ORDER BY qm.created_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        metrics = []
        for row in rows:
            metrics.append({
                "task_id": row[0],
                "accuracy": row[1],
                "first_pass": row[2],
                "revision_count": row[3],
                "complexity_score": row[4],
                "tokens_used": row[5],
            })
        self._json({"metrics": metrics})

    def _serve_quality_comparison(self):
        html = _load_template("quality_comparison.html").encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html)))
        self.end_headers()
        self.wfile.write(html)


if __name__ == "__main__":
    import os as _os
    import signal as _signal
    import socket as _socket
    import subprocess as _subprocess
    import time as _time
    from socketserver import ThreadingMixIn

    class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
        daemon_threads = True
        allow_reuse_address = True

    def _kill_port(port: int) -> bool:
        """포트를 점유한 프로세스를 찾아 SIGTERM → SIGKILL 순으로 종료. 성공 여부 반환."""
        try:
            result = _subprocess.run(
                ["lsof", "-ti", f"tcp:{port}"],
                capture_output=True, text=True
            )
            pids = [int(p) for p in result.stdout.split() if p.strip().isdigit()]
        except FileNotFoundError:
            # lsof 없으면 fuser 시도 (Linux)
            try:
                result = _subprocess.run(
                    ["fuser", f"{port}/tcp"],
                    capture_output=True, text=True
                )
                pids = [int(p) for p in result.stdout.split() if p.strip().lstrip('-').isdigit()]
            except FileNotFoundError:
                return False
        if not pids:
            return False
        for pid in pids:
            if pid == _os.getpid():
                continue
            try:
                _os.kill(pid, _signal.SIGTERM)
            except ProcessLookupError:
                pass
        _time.sleep(0.6)
        for pid in pids:
            if pid == _os.getpid():
                continue
            try:
                _os.kill(pid, 0)          # 아직 살아있으면
                _os.kill(pid, _signal.SIGKILL)
            except ProcessLookupError:
                pass
        _time.sleep(0.3)
        print(f"[serve] 기존 프로세스 종료: PID {pids}", flush=True)
        return True

    try:
        server = ThreadedHTTPServer(("localhost", PORT), Handler)
    except OSError:
        print(f"[serve] 포트 {PORT} 사용 중 — 기존 프로세스 재시작…", flush=True)
        _kill_port(PORT)
        server = ThreadedHTTPServer(("localhost", PORT), Handler)

    import webbrowser, threading
    threading.Timer(0.5, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
    print(f"http://localhost:{PORT}  (Ctrl+C 종료)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n종료")
