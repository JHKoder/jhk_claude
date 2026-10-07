#!/bin/bash
# 로컬에서 리포트 생성 및 분석

set -e

# 프로젝트 루트 디렉토리 찾기
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_DIR="${1:-docs/experiments}"

echo "📊 실험 분석 리포트 생성 중..."
echo "  Project Root: $PROJECT_ROOT"
echo "  Output: $OUTPUT_DIR"
echo ""

cd "$PROJECT_ROOT"

# Python 분석 실행
python3 << 'PYTHON_EOF'
import sys
import os
from pathlib import Path

# .experiment 디렉토리를 모듈 경로에 추가
exp_dir = Path.cwd() / ".experiment"
sys.path.insert(0, str(exp_dir))

from export.reports import export_reports

result = export_reports('docs/experiments')

print("\n✅ 리포트 생성 완료!")
print("\n생성된 파일:")
for report_type, path in result['individual_reports'].items():
    print(f"  - {report_type}")
print(f"  - analysis.json")
print(f"  - full-report.md (통합)")

PYTHON_EOF

echo ""
echo "📖 리포트 위치: $OUTPUT_DIR"
echo "🔍 전체 리포트 확인:"
echo "   cat $OUTPUT_DIR/$(date +%Y-%m-%d)-full-report.md"
