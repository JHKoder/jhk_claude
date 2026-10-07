"""분석 결과를 Jekyll 연구 게시물로 변환"""
import json
from pathlib import Path
from datetime import datetime
from .analyzer import ExperimentAnalyzer

class BlogPostGenerator:
    """Jekyll 형식의 블로그 게시물 생성"""

    @staticmethod
    def generate_daily_post(date_str: str) -> str:
        """일일 분석을 블로그 게시물로 변환"""
        analyzer = ExperimentAnalyzer()

        # 해당 날짜의 세션 조회
        cursor = analyzer.conn.execute("""
            SELECT * FROM runs
            WHERE DATE(recorded_at) = ?
            ORDER BY recorded_at DESC
        """, (date_str,))

        runs = [dict(row) for row in cursor.fetchall()]
        if not runs:
            analyzer.close()
            return None

        # 프론트매터
        post = f"""---
layout: research
title: "일일 분석 - {date_str}"
date: {date_str}T09:00:00+09:00
author: "Experiment Bot"
category: "일일 분석"
tags: ["daily", "session", "analysis"]
excerpt: "Claude Code 세션 {len(runs)}개 분석"
---

## 📊 오늘의 실험 결과

**분석 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**총 세션**: {len(runs)}개

"""
        # 세션 테이블
        post += """### 세션 목록

| 세션 ID | 러너 | Input | Output | 품질 | Turn | 컴파일 | 시간 |
|---------|------|-------|--------|------|------|--------|------|
"""
        for r in runs:
            session_id = (r['session_id'] or '')[:8]
            quality = f"{r['test_pass_rate']:.1f}%" if r['test_pass_rate'] else 'N/A'
            compile_ok = "✓" if r['compile_ok'] else "✗"
            time_sec = f"{r['wall_clock_sec']}s" if r['wall_clock_sec'] else '-'

            post += f"| {session_id} | {r['runner'] or '-'} | {r['input_tokens']:,} | {r['output_tokens']:,} | {quality} | {r['turn_count']} | {compile_ok} | {time_sec} |\n"

        # 통계
        post += "\n### 📈 통계\n\n"
        total_input = sum(r['input_tokens'] for r in runs)
        total_output = sum(r['output_tokens'] for r in runs)
        total_cost = sum(r['billing_usd'] for r in runs)
        avg_quality = sum(r['test_pass_rate'] or 0 for r in runs) / len(runs) if runs else 0

        post += f"- **총 Input Token**: {total_input:,}\n"
        post += f"- **총 Output Token**: {total_output:,}\n"
        post += f"- **총 비용**: ${total_cost:.4f}\n"
        post += f"- **평균 품질**: {avg_quality:.2f}%\n"

        analyzer.close()
        return post

    @staticmethod
    def generate_trend_post() -> str:
        """30일 추세 분석 게시물"""
        analyzer = ExperimentAnalyzer()
        analysis = analyzer.analyze_trends(days=30)
        analyzer.close()

        post = f"""---
layout: research
title: "30일 추세 분석 리포트"
date: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S+09:00')}
author: "Experiment Bot"
category: "추세 분석"
tags: ["trends", "analysis", "monthly"]
excerpt: "지난 30일간의 성능 추이 분석"
---

## 📈 30일 추세 분석

**분석 기간**: 지난 30일
**생성일**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### 📊 요약 통계

"""
        summary = analysis['summary']
        post += f"""- **총 실행**: {summary['total_runs']}회
- **일평균 실행**: {summary['avg_daily_runs']:.1f}회
- **총 토큰**: {summary['total_tokens']:,}
- **총 비용**: ${summary['total_cost']:.4f}

### 📅 일일 데이터

| 날짜 | Run 수 | 평균 품질 | 총 Token | 비용 |
|------|--------|----------|----------|------|
"""
        for day in analysis['daily_data']:
            post += f"| {day['date']} | {day['runs']} | {day['avg_quality']:.2f}% | {day['total_tokens']:,} | ${day['daily_cost']:.4f} |\n"

        post += "\n### 💡 인사이트\n\n"
        post += "- 지난 30일간의 성능 추이를 분석합니다.\n"
        post += "- 일일 토큰 사용량과 비용을 추적합니다.\n"
        post += "- 평균 품질 점수의 변화를 모니터링합니다.\n"

        return post

    @staticmethod
    def generate_efficiency_post() -> str:
        """효율성 분석 게시물"""
        analyzer = ExperimentAnalyzer()
        analysis = analyzer.analyze_token_efficiency()
        analyzer.close()

        if analysis.get("status") == "no_data":
            return None

        post = f"""---
layout: research
title: "토큰 효율성 분석"
date: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S+09:00')}
author: "Experiment Bot"
category: "효율성"
tags: ["efficiency", "tokens", "cache"]
excerpt: "토큰 사용량과 캐시 효율성 분석"
---

## ⚡ 토큰 효율성 분석

**분석 기간**: 최근 100개 세션
**생성일**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### 🎯 핵심 지표

"""
        post += f"""- **총 실행**: {analysis['total_runs']}회
- **총 Input Token**: {analysis['total_input_tokens']:,}
- **총 Output Token**: {analysis['total_output_tokens']:,}
- **Input/Output 비율**: {analysis['input_output_ratio']:.2f}
- **총 비용**: ${analysis['total_cost_usd']:.4f}

### 📊 품질 지표

- **평균 품질**: {analysis['avg_quality']:.2f}%
- **캐시 히트율**: {analysis['cache_hit_rate']:.2f}%
- **토큰당 품질**: {analysis['quality_per_token']:.2f}
- **평균 Turn 수**: {analysis['avg_turn_count']}

### 💡 분석

캐시 히트율이 {analysis['cache_hit_rate']:.2f}%로 매우 높습니다.
이는 Prompt 캐시 기능이 효과적으로 작동하고 있음을 의미합니다.

토큰당 품질 점수는 {analysis['quality_per_token']:.2f}점으로,
효율적인 토큰 사용을 나타냅니다.

"""
        return post

    @staticmethod
    def generate_quality_post() -> str:
        """품질 지표 게시물"""
        analyzer = ExperimentAnalyzer()
        analysis = analyzer.analyze_quality_metrics()
        analyzer.close()

        if analysis.get("status") == "no_data":
            return None

        post = f"""---
layout: research
title: "품질 지표 분석"
date: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S+09:00')}
author: "Experiment Bot"
category: "품질"
tags: ["quality", "metrics", "testing"]
excerpt: "코드 품질 및 테스트 통과율 분석"
---

## ✅ 품질 지표 분석

**분석 기간**: 최근 100개 세션
**생성일**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### 📊 통계

- **총 실행**: {analysis['total_runs']}회
- **평균 통과율**: {analysis['avg_pass_rate']:.2f}%
- **중앙값 통과율**: {analysis['median_pass_rate']:.2f}%
- **컴파일 성공율**: {analysis['compile_success_rate']:.2f}%

### 📈 코드 변경량

- **평균 변경 파일**: {analysis['avg_files_changed']:.1f}개
- **평균 추가 라인**: {analysis['avg_lines_added']:.1f}줄

"""
        if analysis.get('by_runner'):
            post += "### 🏃 러너별 성능\n\n"
            post += "| 러너 | 실행 횟수 | 평균 품질 |\n"
            post += "|------|----------|----------|\n"
            for runner, stats in sorted(analysis['by_runner'].items()):
                post += f"| {runner} | {stats['count']} | {stats['avg_quality']:.2f}% |\n"
            post += "\n"

        return post

    @staticmethod
    def generate_model_post() -> str:
        """모델 성능 비교 게시물"""
        analyzer = ExperimentAnalyzer()
        analysis = analyzer.analyze_model_performance()
        analyzer.close()

        if not analysis.get('models'):
            return None

        post = f"""---
layout: research
title: "모델 성능 비교"
date: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S+09:00')}
author: "Experiment Bot"
category: "모델 비교"
tags: ["models", "performance", "comparison"]
excerpt: "Claude 모델별 효율성 및 성능 비교"
---

## 🤖 모델 성능 비교

**분석 기간**: 최근 데이터
**생성일**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### 📊 모델별 성능

| 모델 | 실행 | 평균 품질 | Avg Turn | 평균 시간 | 비용 |
|------|------|----------|----------|----------|------|
"""
        for model in analysis['models']:
            post += f"| {model['name']} | {model['run_count']} | {model['avg_quality']:.2f}% | {model['avg_turns']:.1f} | {model['avg_time_sec']:.1f}s | ${model['total_cost']:.4f} |\n"

        post += "\n### 💡 분석\n\n"
        post += "- 모델별 테스트 통과율을 비교합니다.\n"
        post += "- 실행 시간과 비용 효율성을 분석합니다.\n"

        return post


def generate_blog_posts(output_dir: str = "_research"):
    """모든 블로그 게시물 생성"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    generator = BlogPostGenerator()
    today = datetime.now().strftime('%Y-%m-%d')

    # 각 분석별로 게시물 생성
    posts = {
        f"{today}-daily-analysis.md": generator.generate_daily_post(today),
        f"{today}-efficiency-analysis.md": generator.generate_efficiency_post(),
        f"{today}-quality-analysis.md": generator.generate_quality_post(),
        f"{today}-model-comparison.md": generator.generate_model_post(),
    }

    # 추세 분석은 매주 생성
    if datetime.now().weekday() == 0:  # 월요일
        posts[f"{today}-trend-analysis.md"] = generator.generate_trend_post()

    created_files = []
    for filename, content in posts.items():
        if content:
            file_path = output_path / filename
            file_path.write_text(content, encoding="utf-8")
            created_files.append(str(file_path))

    return created_files


if __name__ == "__main__":
    files = generate_blog_posts()
    print("🚀 블로그 게시물 생성 완료:")
    for f in files:
        print(f"  - {f}")
