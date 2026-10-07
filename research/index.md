---
layout: default
title: "연구"
permalink: /research/
---

<h1 style="margin-bottom: 12px;">📚 연구 목록</h1>
<p style="color: var(--text-secondary); margin-bottom: 30px;">총 {{ site.research | size }}개의 연구 논문 및 분석 리포트</p>

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
    {% assign categories = '' | split: '' %}
    {% for research in site.research %}
        {% if research.category %}
            {% unless categories contains research.category %}
                {% assign categories = categories | push: research.category %}
            {% endunless %}
        {% endif %}
    {% endfor %}
    {% for category in categories | sort %}
    <button class="category-tag" onclick="filterByCategory('{{ category }}'); updateCategoryActive(this)">{{ category }}</button>
    {% endfor %}
</div>

<!-- 연구 그리드 -->
<div class="research-grid">
    {% for research in site.research | sort: 'date' | reverse %}
    <a href="{{ research.url | relative_url }}" 
       class="research-card" 
       data-date="{{ research.date | date: '%Y-%m-%d' }}"
       data-category="{{ research.category | default: 'uncategorized' }}">
        <div class="research-card-title">{{ research.title }}</div>
        <div class="research-card-meta">
            <span>{{ research.date | date: '%Y년 %m월 %d일' }}</span>
            {% if research.category %}
            <span>{{ research.category }}</span>
            {% endif %}
        </div>
        <div class="research-card-excerpt">
            {{ research.excerpt | default: research.content | strip_html | truncatewords: 25 }}
        </div>
        <div class="research-card-tags">
            {% for tag in research.tags | limit: 3 %}
            <span class="tag">#{{ tag }}</span>
            {% endfor %}
            {% if research.tags.size > 3 %}
            <span style="color: var(--text-secondary); font-size: 12px;">+{{ research.tags.size | minus: 3 }}</span>
            {% endif %}
        </div>
    </a>
    {% endfor %}
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
        cards.forEach(card => {
            const title = card.querySelector('.research-card-title').textContent.toLowerCase();
            const excerpt = card.querySelector('.research-card-excerpt').textContent.toLowerCase();
            if (title.includes(query.toLowerCase()) || excerpt.includes(query.toLowerCase())) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    }

    function sortResearch(type) {
        const container = document.querySelector('.research-grid');
        const cards = Array.from(document.querySelectorAll('.research-card'));
        
        cards.sort((a, b) => {
            if (type === 'latest') {
                return new Date(b.dataset.date) - new Date(a.dataset.date);
            } else if (type === 'oldest') {
                return new Date(a.dataset.date) - new Date(b.dataset.date);
            } else if (type === 'title') {
                return a.querySelector('.research-card-title').textContent
                    .localeCompare(b.querySelector('.research-card-title').textContent, 'ko');
            }
            return 0;
        });

        cards.forEach(card => container.appendChild(card));
    }
</script>
