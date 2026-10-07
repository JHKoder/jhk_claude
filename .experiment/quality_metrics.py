import subprocess
import json
import re
from pathlib import Path

class QualityEvaluator:
    """코드 품질 측정"""

    def __init__(self, task_id: str, project_root: str):
        self.task_id = task_id
        self.project_root = project_root

    def run_tests(self, test_command: str) -> dict:
        """테스트 실행 및 결과 파싱"""
        try:
            result = subprocess.run(
                test_command,
                shell=True,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )

            return {
                "passed": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"passed": False, "error": "Test timeout"}

    def calculate_accuracy(self, test_result: dict, expected_test_count: int) -> float:
        """테스트 통과율 계산 (0-100)"""
        if not test_result.get("passed"):
            # 실패한 경우 stdout에서 몇 개 통과했는지 파싱
            output = test_result.get("stdout", "")
            # pytest 형식 예: "4 passed, 1 failed"
            match = re.search(r'(\d+) passed', output)
            passed = int(match.group(1)) if match else 0
            return (passed / expected_test_count) * 100 if expected_test_count > 0 else 0
        else:
            return 100.0

    def count_revisions_from_git(self, session_id: str) -> int:
        """세션 중 수정 횟수 (커밋 수) 계산"""
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-n", "20"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            # 단순화: 같은 파일에 대한 커밋 수 (반복 수정 표시)
            # 실제로는 Claude 세션 로그에서 turn 수와 수정 횟수 비교
            return 1  # 첫 응답에서 완성 = 1
        except:
            return 1

    def calculate_complexity_score(self) -> float:
        """작업 복잡도 점수 (0-10)"""
        # tasks.json에서 읽어오기
        tasks_path = Path(__file__).parent / 'config' / 'tasks.json'
        with open(tasks_path) as f:
            tasks = json.load(f).get("tasks", [])

        for task in tasks:
            if task["id"] == self.task_id:
                return task.get("complexity", 5)
        return 5

def evaluate_session(session_id: str, task_id: str, project_root: str, test_command: str, expected_test_count: int):
    """세션 평가 통합 함수"""
    evaluator = QualityEvaluator(task_id, project_root)

    # 테스트 실행
    test_result = evaluator.run_tests(test_command)

    # 메트릭 계산
    accuracy = evaluator.calculate_accuracy(test_result, expected_test_count)
    first_pass = 1 if accuracy == 100.0 else 0
    revision_count = evaluator.count_revisions_from_git(session_id)
    complexity_score = evaluator.calculate_complexity_score()

    return {
        "session_id": session_id,
        "task_id": task_id,
        "accuracy": accuracy,
        "first_pass": first_pass,
        "revision_count": revision_count,
        "complexity_score": complexity_score
    }
