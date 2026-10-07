"""분석 결과를 Markdown 리포트로 변환"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from .analyzer import ExperimentAnalyzer

class MarkdownReportGenerator:
    def __init__(self, analyzer: ExperimentAnalyzer):
        self.analyzer = analyzer

    def generate_daily_report(self) -> str:
        """일일 세션 리포트"""
        cursor = self.analyzer.conn.execute("""
            SELECT * FROM runs
            WHERE DATE(recorded_at) = DATE('now')
            ORDER BY recorded_at DESC
        """)

        runs = [dict(row) for row in cursor.fetchall()]
        if not runs:
            return "# 금일 실험\n\n데이터 없음\n"

        md = f"# 금일 실험 {datetime.now().strftime('%Y-%m-%d')}\n\n"
        md += f"**총 세션**: {len(runs)}개\n\n"

        md += "## 세션 목록\n\n"
        md += "| 세션 ID | 러너 | Input | Output | 품질 | Turn | 컴파일 | 실행시간 |\n"
        md += "|---------|------|-------|--------|------|------|--------|----------|\n"

        for r in runs:
            session_id = (r['session_id'] or '')[:8]
            runner = r['runner'] or '-'
            quality = f"{r['test_pass_rate']:.1f}%" if r['test_pass_rate'] else 'N/A'
            compile_ok = "✓" if r['compile_ok'] else "✗"
            time_sec = f"{r['wall_clock_sec']}s" if r['wall_clock_sec'] else 'N/A'

            md += f"| {session_id} | {runner} | {r['input_tokens']:,} | {r['output_tokens']:,} | {quality} | {r['turn_count']} | {compile_ok} | {time_sec} |\n"

        return md

    def generate_efficiency_report(self) -> str:
        """효율성 분석 리포트"""
        analysis = self.analyzer.analyze_token_efficiency()

        if analysis.get("status") == "no_data":
            return "# 토큰 효율 분석\n\n데이터 없음\n"

        md = "# 토큰 효율 분석\n\n"
        md += f"**분석 대상**: 최근 100개 세션\n\n"

        md += "## 핵심 지표\n\n"
        md += f"- **총 Run 수**: {analysis['total_runs']}\n"
        md += f"- **총 Input Token**: {analysis['total_input_tokens']:,}\n"
        md += f"- **총 Output Token**: {analysis['total_output_tokens']:,}\n"
        md += f"- **Input/Output 비율**: {analysis['input_output_ratio']:.2f}\n"
        md += f"- **총 비용**: ${analysis['total_cost_usd']:.4f}\n\n"

        md += "## 품질 지표\n\n"
        md += f"- **평균 품질 점수**: {analysis['avg_quality']:.2f}%\n"
        md += f"- **캐시 히트율**: {analysis['cache_hit_rate']:.2f}%\n"
        md += f"- **토큰당 품질**: {analysis['quality_per_token']:.2f}\n"
        md += f"- **평균 Turn 수**: {analysis['avg_turn_count']}\n\n"

        return md

    def generate_quality_report(self) -> str:
        """품질 지표 리포트"""
        analysis = self.analyzer.analyze_quality_metrics()

        if analysis.get("status") == "no_data":
            return "# 품질 지표\n\n데이터 없음\n"

        md = "# 품질 지표 분석\n\n"
        md += f"**분석 대상**: 최근 100개 세션\n\n"

        md += "## 통계\n\n"
        md += f"- **총 Run 수**: {analysis['total_runs']}\n"
        md += f"- **평균 통과율**: {analysis['avg_pass_rate']:.2f}%\n"
        md += f"- **중앙값 통과율**: {analysis['median_pass_rate']:.2f}%\n"
        md += f"- **컴파일 성공율**: {analysis['compile_success_rate']:.2f}%\n"
        md += f"- **평균 Turn**: {analysis['avg_turn_count']}\n"
        md += f"- **평균 변경 파일**: {analysis['avg_files_changed']}\n"
        md += f"- **평균 추가 라인**: {analysis['avg_lines_added']}\n\n"

        if analysis.get('by_runner'):
            md += "## 러너별 성능\n\n"
            md += "| 러너 | 실행 횟수 | 평균 품질 |\n"
            md += "|------|----------|----------|\n"

            for runner, stats in sorted(analysis['by_runner'].items()):
                md += f"| {runner} | {stats['count']} | {stats['avg_quality']:.2f}% |\n"
            md += "\n"

        return md

    def generate_trend_report(self) -> str:
        """추세 분석 리포트"""
        analysis = self.analyzer.analyze_trends(days=30)

        md = "# 30일 추세 분석\n\n"
        md += f"**생성일**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        summary = analysis['summary']
        md += "## 요약\n\n"
        md += f"- **총 Run**: {summary['total_runs']}\n"
        md += f"- **일평균 Run**: {summary['avg_daily_runs']}\n"
        md += f"- **총 Token**: {summary['total_tokens']:,}\n"
        md += f"- **총 비용**: ${summary['total_cost']:.4f}\n\n"

        md += "## 일일 데이터\n\n"
        md += "| 날짜 | Run 수 | 평균 품질 | 총 Token | 비용 |\n"
        md += "|------|--------|----------|----------|------|\n"

        for day in analysis['daily_data']:
            md += f"| {day['date']} | {day['runs']} | {day['avg_quality']:.2f}% | {day['total_tokens']:,} | ${day['daily_cost']:.4f} |\n"
        md += "\n"

        return md

    def generate_model_report(self) -> str:
        """모델 성능 비교 리포트"""
        analysis = self.analyzer.analyze_model_performance()

        md = "# 모델 성능 비교\n\n"

        if not analysis.get('models'):
            return md + "데이터 없음\n"

        md += "| 모델 | 실행 | 평균 품질 | Avg Turn | 평균 시간 | 비용 |\n"
        md += "|------|------|----------|----------|----------|------|\n"

        for model in analysis['models']:
            md += f"| {model['name']} | {model['run_count']} | {model['avg_quality']:.2f}% | {model['avg_turns']} | {model['avg_time_sec']:.1f}s | ${model['total_cost']:.4f} |\n"
        md += "\n"

        return md

    def generate_full_report(self) -> str:
        """전체 리포트 생성"""
        md = f"# 실험 분석 리포트\n\n"
        md += f"**생성일**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        md += "---\n\n"
        md += self.generate_daily_report()
        md += "\n---\n\n"
        md += self.generate_efficiency_report()
        md += "\n---\n\n"
        md += self.generate_quality_report()
        md += "\n---\n\n"
        md += self.generate_trend_report()
        md += "\n---\n\n"
        md += self.generate_model_report()

        return md


def export_reports(output_dir: str = "docs/experiments"):
    """리포트 생성 및 저장"""
    db_path = Path(__file__).parent.parent / "experiment.db"
    analyzer = ExperimentAnalyzer(str(db_path))
    generator = MarkdownReportGenerator(analyzer)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 전체 리포트
    full_report = generator.generate_full_report()
    today = datetime.now().strftime('%Y-%m-%d')
    report_file = output_path / f"{today}-full-report.md"
    report_file.write_text(full_report, encoding="utf-8")

    # 개별 리포트
    reports = {
        f"{today}-daily.md": generator.generate_daily_report(),
        f"{today}-efficiency.md": generator.generate_efficiency_report(),
        f"{today}-quality.md": generator.generate_quality_report(),
        f"{today}-trends.md": generator.generate_trend_report(),
        f"{today}-models.md": generator.generate_model_report(),
    }

    for filename, content in reports.items():
        (output_path / filename).write_text(content, encoding="utf-8")

    # JSON 분석 결과
    analysis = analyzer.generate_summary_report()
    json_file = output_path / f"{today}-analysis.json"
    json_file.write_text(
        json.dumps(analysis, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8"
    )

    analyzer.close()

    return {
        "full_report": str(report_file),
        "individual_reports": {k: str(output_path / k) for k in reports.keys()},
        "json_analysis": str(json_file),
    }


if __name__ == "__main__":
    result = export_reports()
    print("리포트 생성 완료:")
    for key, value in result.items():
        if isinstance(value, dict):
            for k, v in value.items():
                print(f"  - {k}: {v}")
        else:
            print(f"  - {key}: {value}")
