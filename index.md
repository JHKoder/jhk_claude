---
layout: default
title: "홈"
---

<div style="margin-bottom: 40px;">
    <h1 style="font-size: 32px; margin-bottom: 12px;">🧪 Claude Code 실험 연구소</h1>
    <p style="font-size: 16px; color: var(--text-secondary); line-height: 1.8; max-width: 600px;">
        Claude Code 세션의 성능 분석, 토큰 효율성, 품질 지표를 추적하고 최적화하는 연구 블로그입니다.
        매일 자동으로 생성되는 분석 리포트와 인사이트를 공유합니다.
    </p>
</div>

<!-- 검색 및 정렬 -->
<div style="margin-bottom: 30px;">
    <div class="search-box">
        <input type="text" id="searchInput" placeholder="연구 검색..." onkeyup="filterResearch(this.value)">
    </div>

    <div class="sort-menu">
        <button class="sort-btn active" onclick="sortResearch('latest'); updateActive(this)">📅 최신순</button>
        <button class="sort-btn" onclick="sortResearch('oldest'); updateActive(this)">📅 오래된순</button>
        <button class="sort-btn" onclick="sortResearch('title'); updateActive(this)">📝 제목순</button>
    </div>
</div>

<!-- 카테고리 필터 -->
<div class="category-filter">
    <button class="category-tag active" onclick="filterByCategory('all'); updateCategoryActive(this)">전체</button>
    <button class="category-tag" onclick="filterByCategory('performance'); updateCategoryActive(this)">성능 분석</button>
    <button class="category-tag" onclick="filterByCategory('efficiency'); updateCategoryActive(this)">효율성</button>
    <button class="category-tag" onclick="filterByCategory('quality'); updateCategoryActive(this)">품질 지표</button>
    <button class="category-tag" onclick="filterByCategory('trends'); updateCategoryActive(this)">추세 분석</button>
    <button class="category-tag" onclick="filterByCategory('models'); updateCategoryActive(this)">모델 비교</button>
</div>

<!-- 최신 통계 -->
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 30px 0;">
    <div style="background: var(--bg-light); padding: 15px; border-radius: 6px; border-left: 4px solid var(--primary-color);">
        <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 4px;">총 연구</div>
        <div style="font-size: 24px; font-weight: 600;">{{ site.research | size }}</div>
    </div>
    <div style="background: var(--bg-light); padding: 15px; border-radius: 6px; border-left: 4px solid #28a745;">
        <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 4px;">총 분석</div>
        <div style="font-size: 24px; font-weight: 600;">{{ site.collections.research | size }}</div>
    </div>
    <div style="background: var(--bg-light); padding: 15px; border-radius: 6px; border-left: 4px solid #fd7e14;">
        <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 4px;">업데이트</div>
        <div style="font-size: 24px; font-weight: 600;">매일</div>
    </div>
</div>

<hr style="margin: 40px 0; border: none; border-top: 1px solid var(--border-color);">

<!-- 연구 목록 -->
<div>
    <h2 style="margin-bottom: 20px; font-size: 24px;">📚 최근 연구</h2>

    <div class="research-grid">
        {% for research in site.research | sort: 'date' | reverse %}
        <a href="{{ research.url | relative_url }}" 
           class="research-card" 
           data-date="{{ research.date | date: '%Y-%m-%d' }}"
           data-category="{{ research.category | default: 'uncategorized' }}"
           style="display: {% if forloop.index > 6 %}none{% endif %};">
            <div class="research-card-title">{{ research.title }}</div>
            <div class="research-card-meta">
                <span>{{ research.date | date: '%Y-%m-%d' }}</span>
                {% if research.category %}
                <span class="tag">{{ research.category }}</span>
                {% endif %}
            </div>
            <div class="research-card-excerpt">
                {{ research.excerpt | default: research.content | strip_html | truncatewords: 20 }}
            </div>
            <div class="research-card-tags">
                {% for tag in research.tags | limit: 3 %}
                <span class="tag">#{{ tag }}</span>
                {% endfor %}
            </div>
        </a>
        {% endfor %}
    </div>

    {% if site.research.size > 6 %}
    <div style="text-align: center; margin-top: 30px;">
        <a href="{{ '/research/' | relative_url }}" style="color: var(--primary-color); text-decoration: none; font-weight: 600;">
            전체 연구 보기 →
        </a>
    </div>
    {% endif %}
</div>

<script>
    function updateActive(btn) {
        document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
    }

    function updateCategoryActive(btn) {
        document.querySelectorAll('.category-tag').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
    }

    function filterByCategory(category) {
        const cards = document.querySelectorAll('.research-card');
        cards.forEach(card => {
            if (category === 'all' || card.dataset.category === category) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    }

    function filterResearch(query) {
        const cards = document.querySelectorAll('.research-card');
        const lowerQuery = query.toLowerCase();
        cards.forEach(card => {
            const text = card.innerText.toLowerCase();
            if (text.includes(lowerQuery)) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    }

    function sortResearch(order) {
        const grid = document.querySelector('.research-grid');
        const cards = Array.from(document.querySelectorAll('.research-card'));
        
        if (order === 'oldest') {
            cards.sort((a, b) => new Date(a.dataset.date) - new Date(b.dataset.date));
        } else if (order === 'title') {
            cards.sort((a, b) => a.innerText.localeCompare(b.innerText));
        } else {
            cards.sort((a, b) => new Date(b.dataset.date) - new Date(a.dataset.date));
        }
        
        cards.forEach(card => grid.appendChild(card));
    }

    // Load dynamic blog metadata
    async function loadBlogMetadata() {
        try {
            const response = await fetch('{{ "/jhk_claude/assets/data/blog-metadata.json" | relative_url }}');
            const metadata = await response.json();
            updateStatsFromMetadata(metadata);
        } catch (error) {
            console.log('Blog metadata not yet available');
        }
    }

    function updateStatsFromMetadata(metadata) {
        // Update research count
        const statCards = document.querySelectorAll('[style*="grid"]');
        if (statCards.length > 0) {
            const firstCard = statCards[0].querySelector('div:nth-child(1) div:nth-child(2)');
            if (firstCard) {
                firstCard.innerText = (metadata.research || []).length;
            }
        }
    }

    // Load on page load
    document.addEventListener('DOMContentLoaded', loadBlogMetadata);
</script>
