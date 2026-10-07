"""심층 분석: 성능, 효율성, 추세"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

class ExperimentAnalyzer:
    def __init__(self, db_path: str = ".experiment/experiment.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def get_runs_by_period(self, days: int = 30) -> list:
        """지난 N일간의 세션 조회"""
        cursor = self.conn.execute("""
            SELECT * FROM runs
            WHERE recorded_at >= datetime('now', '-' || ? || ' days')
            ORDER BY recorded_at DESC
        """, (days,))
        return [dict(row) for row in cursor.fetchall()]

    def analyze_token_efficiency(self) -> dict:
        """토큰 효율 분석"""
        cursor = self.conn.execute("""
            SELECT
                input_tokens,
                output_tokens,
                cache_read,
                cache_write,
                billing_usd,
                test_pass_rate,
                turn_count
            FROM runs
            WHERE input_tokens > 0
            ORDER BY recorded_at DESC
            LIMIT 100
        """)

        runs = [dict(row) for row in cursor.fetchall()]
        if not runs:
            return {"status": "no_data"}

        total_input = sum(r['input_tokens'] for r in runs)
        total_output = sum(r['output_tokens'] for r in runs)
        total_cost = sum(r['billing_usd'] for r in runs)
        avg_quality = statistics.mean([r['test_pass_rate'] or 0 for r in runs])

        # 캐시 효율
        cache_hit_rate = 0
        total_cache_attempts = sum(r['cache_read'] + r['cache_write'] for r in runs)
        if total_cache_attempts > 0:
            total_cache_read = sum(r['cache_read'] for r in runs)
            cache_hit_rate = (total_cache_read / total_cache_attempts) * 100

        # 토큰당 품질 점수
        quality_per_token = avg_quality / ((total_input + total_output) / 1000) if (total_input + total_output) > 0 else 0

        return {
            "total_runs": len(runs),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "input_output_ratio": (total_input / total_output) if total_output > 0 else 0,
            "total_cost_usd": round(total_cost, 4),
            "avg_quality": round(avg_quality, 2),
            "cache_hit_rate": round(cache_hit_rate, 2),
            "quality_per_token": round(quality_per_token, 2),
            "avg_turn_count": round(statistics.mean([r['turn_count'] for r in runs]), 1),
        }

    def analyze_quality_metrics(self) -> dict:
        """품질 지표 분석"""
        cursor = self.conn.execute("""
            SELECT
                test_pass_rate,
                compile_ok,
                turn_count,
                changed_files_cnt,
                added_lines,
                deleted_lines,
                wall_clock_sec,
                runner
            FROM runs
            WHERE test_pass_rate IS NOT NULL
            ORDER BY recorded_at DESC
            LIMIT 100
        """)

        runs = [dict(row) for row in cursor.fetchall()]
        if not runs:
            return {"status": "no_data"}

        pass_rates = [r['test_pass_rate'] for r in runs if r['test_pass_rate'] is not None]
        compile_success = sum(1 for r in runs if r['compile_ok'] == 1)

        runners = defaultdict(lambda: {"count": 0, "avg_quality": 0})
        for r in runs:
            runner = r['runner'] or 'unknown'
            runners[runner]['count'] += 1
            runners[runner]['avg_quality'] += r['test_pass_rate'] or 0

        for runner in runners:
            runners[runner]['avg_quality'] = round(
                runners[runner]['avg_quality'] / runners[runner]['count'], 2
            )

        return {
            "total_runs": len(runs),
            "avg_pass_rate": round(statistics.mean(pass_rates) if pass_rates else 0, 2),
            "median_pass_rate": round(statistics.median(pass_rates) if pass_rates else 0, 2),
            "compile_success_rate": round((compile_success / len(runs) * 100) if runs else 0, 2),
            "avg_turn_count": round(statistics.mean([r['turn_count'] for r in runs]), 1),
            "avg_files_changed": round(statistics.mean([r['changed_files_cnt'] or 0 for r in runs]), 1),
            "avg_lines_added": round(statistics.mean([r['added_lines'] or 0 for r in runs]), 1),
            "by_runner": dict(runners),
        }

    def analyze_trends(self, days: int = 30) -> dict:
        """시간별 추세 분석"""
        cursor = self.conn.execute("""
            SELECT
                DATE(recorded_at) as date,
                COUNT(*) as run_count,
                AVG(test_pass_rate) as avg_quality,
                SUM(input_tokens + output_tokens) as total_tokens,
                SUM(billing_usd) as daily_cost
            FROM runs
            WHERE recorded_at >= datetime('now', '-' || ? || ' days')
            GROUP BY DATE(recorded_at)
            ORDER BY date DESC
        """, (days,))

        rows = [dict(row) for row in cursor.fetchall()]

        return {
            "period_days": days,
            "daily_data": [
                {
                    "date": r['date'],
                    "runs": r['run_count'],
                    "avg_quality": round(r['avg_quality'] or 0, 2),
                    "total_tokens": r['total_tokens'] or 0,
                    "daily_cost": round(r['daily_cost'] or 0, 4),
                }
                for r in rows
            ],
            "summary": {
                "total_runs": sum(r['run_count'] for r in rows),
                "avg_daily_runs": round(statistics.mean([r['run_count'] for r in rows]), 1) if rows else 0,
                "total_tokens": sum(r['total_tokens'] or 0 for r in rows),
                "total_cost": round(sum(r['daily_cost'] or 0 for r in rows), 4),
            }
        }

    def analyze_model_performance(self) -> dict:
        """모델별 성능 비교"""
        cursor = self.conn.execute("""
            SELECT
                model,
                COUNT(*) as count,
                AVG(test_pass_rate) as avg_quality,
                AVG(turn_count) as avg_turns,
                AVG(wall_clock_sec) as avg_time,
                SUM(billing_usd) as total_cost
            FROM runs
            WHERE model IS NOT NULL AND test_pass_rate IS NOT NULL
            GROUP BY model
            ORDER BY avg_quality DESC
        """)

        rows = [dict(row) for row in cursor.fetchall()]

        return {
            "models": [
                {
                    "name": r['model'],
                    "run_count": r['count'],
                    "avg_quality": round(r['avg_quality'], 2),
                    "avg_turns": round(r['avg_turns'] or 0, 1),
                    "avg_time_sec": round(r['avg_time'] or 0, 1),
                    "total_cost": round(r['total_cost'] or 0, 4),
                }
                for r in rows
            ]
        }

    def generate_summary_report(self) -> dict:
        """전체 요약 리포트"""
        return {
            "generated_at": datetime.now().isoformat(),
            "token_efficiency": self.analyze_token_efficiency(),
            "quality_metrics": self.analyze_quality_metrics(),
            "trends": self.analyze_trends(days=30),
            "model_performance": self.analyze_model_performance(),
        }

    def close(self):
        self.conn.close()

def generate_analysis(db_path: str = ".experiment/experiment.db") -> dict:
    """분석 생성 진입점"""
    analyzer = ExperimentAnalyzer(db_path)
    try:
        return analyzer.generate_summary_report()
    finally:
        analyzer.close()

if __name__ == "__main__":
    import json
    analysis = generate_analysis()
    print(json.dumps(analysis, indent=2, ensure_ascii=False))
