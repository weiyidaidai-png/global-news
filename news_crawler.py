#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime, timedelta
import os
import logging

# 配置日志
logging.basicConfig(
    filename='logs/news_crawler.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# 新闻源配置
NEWS_SOURCES = {
    # 国际新闻源
    'bbc': {
        'name': 'BBC News',
        'url': 'https://www.bbc.com/news',
        'selector': 'h3[data-testid="card-headline"]',
        'link_selector': 'a[data-testid="card-link"]'
    },
    'cnn': {
        'name': 'CNN',
        'url': 'https://www.cnn.com',
        'selector': 'span[data-editable="headline"]',
        'link_selector': 'a[data-link-type="article"]'
    },
    'reuters': {
        'name': 'Reuters',
        'url': 'https://www.reuters.com',
        'selector': 'h3[data-testid="Heading"]',
        'link_selector': 'a[data-testid="ArticleLink"]'
    },
    'aljazeera': {
        'name': 'Al Jazeera',
        'url': 'https://www.aljazeera.com',
        'selector': 'h3.gc__title',
        'link_selector': 'a.gc__link'
    },
    'nytimes': {
        'name': 'New York Times',
        'url': 'https://www.nytimes.com',
        'selector': 'h3.css-2fgx4k',
        'link_selector': 'a.css-9mylee'
    },
    'theguardian': {
        'name': 'The Guardian',
        'url': 'https://www.theguardian.com',
        'selector': 'h3.card-headline',
        'link_selector': 'a.js-headline-text'
    },
    'ap': {
        'name': 'Associated Press',
        'url': 'https://apnews.com',
        'selector': 'h1.PagePromo-title',
        'link_selector': 'a.PagePromo-link'
    },
    'nikkei': {
        'name': '日经新闻',
        'url': 'https://www.nikkei.com',
        'selector': 'h3.title',
        'link_selector': 'a.title-link'
    },
    'nhk': {
        'name': 'NHK',
        'url': 'https://www3.nhk.or.jp/news/',
        'selector': 'h3.news-txt',
        'link_selector': 'a.link-color'
    },

    # 中国新闻源 - 增加更多
    'people': {
        'name': '人民网',
        'url': 'http://www.people.com.cn',
        'selector': '.news_title a, .p1 a.tit, .title a, h1 a, h2 a, h3 a',
        'link_selector': '.news_title a, .p1 a.tit, .title a, h1 a, h2 a, h3 a'
    },
    'thepaper': {
        'name': '澎湃新闻',
        'url': 'https://www.thepaper.cn',
        'selector': 'h2.news_title',
        'link_selector': 'a.news_li'
    },
    'xinhua': {
        'name': '新华网',
        'url': 'http://www.xinhuanet.com',
        'selector': '.title a, .tit a, h1 a, h2 a, h3 a, .news-title a',
        'link_selector': '.title a, .tit a, h1 a, h2 a, h3 a, .news-title a'
    },
    'cctv': {
        'name': '央视新闻',
        'url': 'https://news.cctv.com',
        'selector': '.title a, .tit a, h1 a, h2 a, h3 a, .more a',
        'link_selector': '.title a, .tit a, h1 a, h2 a, h3 a, .more a'
    },
    'chinanews': {
        'name': '中国新闻网',
        'url': 'http://www.chinanews.com',
        'selector': '.news_title a, .tit a, h1 a, h2 a, h3 a',
        'link_selector': '.news_title a, .tit a, h1 a, h2 a, h3 a'
    },
    'guancha': {
        'name': '观察者网',
        'url': 'https://www.guancha.cn',
        'selector': 'h4.content-title a, h3.content-title a, .content a',
        'link_selector': 'h4.content-title a, h3.content-title a, .content a'
    },
    'southcn': {
        'name': '南方网',
        'url': 'http://www.southcn.com',
        'selector': '.newsTitle a, .title a, h1 a, h2 a, h3 a',
        'link_selector': '.newsTitle a, .title a, h1 a, h2 a, h3 a'
    },
    'eastday': {
        'name': '东方网',
        'url': 'http://www.eastday.com',
        'selector': '.title a, .tit a, h1 a, h2 a, h3 a, .news-title a',
        'link_selector': '.title a, .tit a, h1 a, h2 a, h3 a, .news-title a'
    },

    # 科技新闻源
    'techweb': {
        'name': 'TechWeb',
        'url': 'http://www.techweb.com.cn',
        'selector': 'a.news_title',
        'link_selector': 'a.news_title'
    },
    'donews': {
        'name': 'DoNews',
        'url': 'http://www.donews.com',
        'selector': 'a.title',
        'link_selector': 'a.title'
    },

    # 财经新闻源
    'hexun': {
        'name': '和讯网',
        'url': 'http://www.hexun.com',
        'selector': 'a.article-title',
        'link_selector': 'a.article-title'
    },
    'eastmoney': {
        'name': '东方财富网',
        'url': 'http://www.eastmoney.com',
        'selector': 'a.title',
        'link_selector': 'a.title'
    },

    # 体育新闻源
    'sports.sohu': {
        'name': '搜狐体育',
        'url': 'http://sports.sohu.com',
        'selector': 'a.title',
        'link_selector': 'a.title'
    },
    'sports.sina': {
        'name': '新浪体育',
        'url': 'http://sports.sina.com.cn',
        'selector': 'a.news-title',
        'link_selector': 'a.news-title'
    }
}

# 新闻分类关键词
CATEGORY_KEYWORDS = {
    '国际': ['国际', 'world', 'global', 'international', 'foreign'],
    '政治': ['政治', 'politics', 'government', 'election', 'policy'],
    '商业': ['商业', 'business', 'economy', 'market', 'finance'],
    '科技': ['科技', 'technology', 'tech', 'digital', 'innovation'],
    '社会': ['社会', 'society', 'social', 'community', 'life'],
    '体育': ['体育', 'sports', 'football', 'basketball', 'olympics'],
    '娱乐': ['娱乐', 'entertainment', 'movie', 'music', 'celebrity']
}

# 请求头部
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

def fetch_html(url, retries=3, delay=5):
    """抓取网页HTML内容"""
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败 {url}: {e}")
            if attempt < retries - 1:
                logger.info(f"等待 {delay} 秒后重试...")
                time.sleep(delay)
                delay *= 2  # 指数退避
    return None

def extract_news(html, source_config):
    """从HTML中提取新闻标题和链接"""
    soup = BeautifulSoup(html, 'html.parser')
    news_items = []

    try:
        # 尝试使用配置的选择器
        if source_config.get('link_selector'):
            # 先找链接，再找标题
            link_elements = soup.select(source_config['link_selector'])
            for link in link_elements:
                # 查找链接内的标题
                title = None

                # 尝试多种方式提取标题
                if source_config.get('selector'):
                    # 使用配置的标题选择器
                    title_element = link.select_one(source_config['selector'])
                    if title_element:
                        title = title_element.get_text().strip()

                # 如果配置的选择器没找到，尝试常见的标题标签
                if not title:
                    common_title_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
                    for tag in common_title_tags:
                        title_element = link.find(tag)
                        if title_element:
                            title = title_element.get_text().strip()
                            break

                # 如果还是没找到，直接从链接文本提取
                if not title:
                    title = link.get_text().strip()

                if title and len(title) > 10:  # 过滤过短的标题
                    news_items.append({
                        'title': title,
                        'url': link['href'],
                        'source': source_config['name']
                    })
        elif source_config.get('selector'):
            # 直接找标题元素
            title_elements = soup.select(source_config['selector'])
            for title_element in title_elements:
                title = title_element.get_text().strip()
                if title and len(title) > 10:
                    # 查找父级链接
                    link = title_element.find_parent('a')
                    if link and 'href' in link.attrs:
                        news_items.append({
                            'title': title,
                            'url': link['href'],
                            'source': source_config['name']
                        })
        else:
            # 如果没有配置选择器，尝试通用抓取方式
            logger.info(f"使用通用抓取方式处理 {source_config['name']}")

            # 尝试查找所有带标题的链接
            common_selectors = [
                'a[href][title]',  # 带title属性的链接
                'a[href] h1', 'a[href] h2', 'a[href] h3',  # 链接内的标题标签
                '.news-item a', '.article-item a', '.story a'  # 常见的新闻容器类
            ]

            for selector in common_selectors:
                elements = soup.select(selector)
                for element in elements:
                    title = None
                    link = None

                    # 如果元素是标题标签，查找其父链接
                    if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        title = element.get_text().strip()
                        link = element.find_parent('a')
                    else:
                        # 如果元素是链接，尝试提取标题
                        link = element
                        # 尝试从链接的title属性获取
                        if 'title' in link.attrs:
                            title = link['title'].strip()
                        # 否则尝试从链接文本获取
                        if not title:
                            title = link.get_text().strip()

                    # 如果找到了标题和链接
                    if title and len(title) > 10 and link and 'href' in link.attrs:
                        news_items.append({
                            'title': title,
                            'url': link['href'],
                            'source': source_config['name']
                        })

                    # 如果已经找到足够的新闻，停止
                    if len(news_items) >= 20:
                        break
                if len(news_items) >= 20:
                    break

        # 去重
        seen_titles = set()
        unique_news = []
        for news in news_items:
            if news['title'] not in seen_titles:
                seen_titles.add(news['title'])
                unique_news.append(news)

        logger.info(f"成功提取 {len(unique_news)} 条新闻")
        return unique_news[:30]  # 限制每条来源的新闻数量

    except Exception as e:
        logger.error(f"提取新闻失败: {e}")
        return []

def categorize_news(news_item):
    """对新闻进行分类"""
    title = news_item['title'].lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in title:
                return category

    # 如果没有匹配的分类，返回默认分类
    return '国际'

# 广告关键词过滤列表
AD_KEYWORDS = [
    '广告', '推广', '推荐', '赞助', '合作', 'APP', '下载',
    '注册', '登录', '会员', '充值', '付费', '优惠', '活动',
    '抽奖', '福利', '红包', '现金', '礼品', '奖品', '游戏',
    '娱乐', '视频', '音乐', '直播', '购物', '电商', '淘宝',
    '京东', '拼多多', '天猫', '苏宁', '国美', '海淘', '代购'
]

def filter_ad_news(news_item):
    """过滤广告和推荐内容"""
    title = news_item['title'].lower()

    # 检查是否包含广告关键词
    for keyword in AD_KEYWORDS:
        if keyword in title:
            logger.info(f"过滤广告新闻: {news_item['title']}")
            return True

    # 检查标题是否过于简短（可能是广告）
    if len(title) < 15:
        logger.info(f"过滤过短标题: {news_item['title']}")
        return True

    # 检查是否包含特殊字符过多
    special_chars = sum(1 for c in title if not c.isalnum() and not c.isspace())
    if special_chars > len(title) * 0.3:
        logger.info(f"过滤特殊字符过多的标题: {news_item['title']}")
        return True

    return False

def process_news_item(news_item):
    """处理单个新闻条目"""
    # 首先过滤广告
    if filter_ad_news(news_item):
        return None

    # 补全相对链接
    if not news_item['url'].startswith(('http://', 'https://')):
        # 尝试从来源URL获取基础域名
        for source_id, source_config in NEWS_SOURCES.items():
            if source_config['name'] == news_item['source']:
                base_url = source_config['url'].split('/')[0] + '//' + source_config['url'].split('/')[2]
                news_item['url'] = base_url + news_item['url']
                break

    # 分类
    news_item['category'] = categorize_news(news_item)

    # 添加抓取时间
    news_item['crawl_time'] = datetime.now().isoformat()

    # 添加唯一ID
    news_item['id'] = f"{news_item['source']}_{int(time.time())}_{hash(news_item['title'])}"

    return news_item

def crawl_all_news():
    """抓取所有新闻源的新闻"""
    all_news = []

    logger.info("开始抓取新闻...")

    for source_id, source_config in NEWS_SOURCES.items():
        logger.info(f"正在抓取 {source_config['name']}...")

        html = fetch_html(source_config['url'])
        if not html:
            logger.error(f"无法获取 {source_config['name']} 的内容，跳过...")
            continue

        news_items = extract_news(html, source_config)
        if not news_items:
            logger.error(f"无法从 {source_config['name']} 提取新闻，跳过...")
            continue

        # 处理新闻条目
        processed_news = []
        for item in news_items:
            processed_item = process_news_item(item)
            if processed_item:  # 只有非广告的新闻才会被添加
                processed_news.append(processed_item)
        all_news.extend(processed_news)

        # 控制访问频率
        logger.info(f"完成抓取 {source_config['name']}，获取 {len(processed_news)} 条新闻")
        time.sleep(2)  # 每个来源之间等待2秒

    # 按时间排序（最新的在前）
    all_news.sort(key=lambda x: x['crawl_time'], reverse=True)

    # 整体去重
    seen_titles = set()
    final_news = []
    for news in all_news:
        if news['title'] not in seen_titles:
            seen_titles.add(news['title'])
            final_news.append(news)

    logger.info(f"完成所有抓取，共获取 {len(final_news)} 条独特新闻")

    return final_news

def save_news_to_file(news, filename='data/news.json'):
    """将新闻保存到JSON文件"""
    try:
        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(news, f, ensure_ascii=False, indent=2)

        logger.info(f"新闻已保存到 {filename}")
        return True

    except Exception as e:
        logger.error(f"保存新闻失败: {e}")
        return False

def load_news_from_file(filename='data/news.json'):
    """从JSON文件加载新闻"""
    try:
        if not os.path.exists(filename):
            return []

        with open(filename, 'r', encoding='utf-8') as f:
            news = json.load(f)

        logger.info(f"从 {filename} 加载了 {len(news)} 条新闻")
        return news

    except Exception as e:
        logger.error(f"加载新闻失败: {e}")
        return []

def generate_html_page(news, filename='index.html'):
    """生成HTML页面"""
    try:
        html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>全球新闻标题聚合器</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }

        .container {
            display: flex;
            max-width: 1400px;
            margin: 0 auto;
            min-height: 100vh;
        }

        .sidebar {
            width: 250px;
            background-color: #fff;
            border-right: 1px solid #e0e0e0;
            padding: 20px;
            position: sticky;
            top: 0;
            height: 100vh;
            overflow-y: auto;
        }

        .sidebar h2 {
            font-size: 18px;
            margin-bottom: 20px;
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }

        .source-list {
            list-style: none;
        }

        .source-item {
            padding: 10px 15px;
            margin-bottom: 5px;
            background-color: #f8f9fa;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
        }

        .source-item:hover {
            background-color: #e9ecef;
            transform: translateX(5px);
        }

        .source-item.active {
            background-color: #3498db;
            color: #fff;
        }

        .main-content {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }

        .header {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .header h1 {
            font-size: 24px;
            margin-bottom: 15px;
            color: #2c3e50;
        }

        .search-bar {
            position: relative;
        }

        .search-bar input {
            width: 100%;
            padding: 12px 20px;
            border: 1px solid #ddd;
            border-radius: 25px;
            font-size: 14px;
            transition: all 0.3s ease;
        }

        .search-bar input:focus {
            outline: none;
            border-color: #3498db;
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
        }

        .news-stats {
            margin-top: 15px;
            font-size: 14px;
            color: #666;
        }

        .news-grid {
            display: grid;
            gap: 15px;
        }

        .news-card {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            border-left: 4px solid #3498db;
        }

        .news-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }

        .news-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            flex-wrap: wrap;
            gap: 10px;
        }

        .news-source {
            display: inline-block;
            padding: 4px 12px;
            background-color: #3498db;
            color: #fff;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }

        .news-category {
            display: inline-block;
            padding: 4px 12px;
            background-color: #95a5a6;
            color: #fff;
            border-radius: 12px;
            font-size: 12px;
        }

        .news-time {
            font-size: 12px;
            color: #999;
        }

        .news-title {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 10px;
            line-height: 1.4;
        }

        .news-title a {
            color: #2c3e50;
            text-decoration: none;
            transition: color 0.3s ease;
        }

        .news-title a:hover {
            color: #3498db;
        }

        .refresh-indicator {
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 10px 20px;
            background-color: #27ae60;
            color: #fff;
            border-radius: 25px;
            font-size: 14px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .refresh-indicator.show {
            opacity: 1;
        }

        .no-results {
            text-align: center;
            padding: 40px 20px;
            color: #666;
        }

        .no-results h3 {
            font-size: 18px;
            margin-bottom: 10px;
        }

        @media (max-width: 768px) {
            .container {
                flex-direction: column;
            }

            .sidebar {
                width: 100%;
                height: auto;
                position: static;
                border-right: none;
                border-bottom: 1px solid #e0e0e0;
            }

            .main-content {
                padding: 15px;
            }

            .header h1 {
                font-size: 20px;
            }

            .news-card {
                padding: 15px;
            }

            .news-title {
                font-size: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h2>新闻来源</h2>
            <ul class="source-list" id="sourceList">
                <li class="source-item active" data-source="all">全部来源</li>
                {% for source in news_sources %}
                <li class="source-item" data-source="{{ source }}">{{ source_names[source] }}</li>
                {% endfor %}
            </ul>
        </div>

        <div class="main-content">
            <div class="header">
                <h1>全球新闻标题聚合器</h1>
                <div class="search-bar">
                    <input type="text" id="searchInput" placeholder="搜索新闻标题...">
                </div>
                <div class="news-stats">
                    共 <span id="totalNews">{{ total_news }}</span> 条新闻 | 最后更新: <span id="lastUpdate">{{ last_update }}</span>
                </div>
            </div>

            <div class="news-grid" id="newsGrid">
                {% if news %}
                    {% for item in news %}
                    <div class="news-card" data-source="{{ item.source }}" data-category="{{ item.category }}">
                        <div class="news-header">
                            <span class="news-source">{{ item.source }}</span>
                            <span class="news-category">{{ item.category }}</span>
                            <span class="news-time">{{ item.formatted_time }}</span>
                        </div>
                        <div class="news-title">
                            <a href="{{ item.url }}" target="_blank" rel="noopener noreferrer">{{ item.title }}</a>
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <div class="no-results">
                        <h3>没有找到新闻</h3>
                        <p>请尝试其他搜索条件</p>
                    </div>
                {% endif %}
            </div>
        </div>
    </div>

    <div class="refresh-indicator" id="refreshIndicator">新闻已更新</div>

    <script>
        // 搜索功能
        const searchInput = document.getElementById('searchInput');
        const newsCards = document.querySelectorAll('.news-card');

        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();

            newsCards.forEach(card => {
                const title = card.querySelector('.news-title a').textContent.toLowerCase();
                if (title.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });

            // 更新统计
            updateNewsStats();
        });

        // 来源过滤
        const sourceItems = document.querySelectorAll('.source-item');

        sourceItems.forEach(item => {
            item.addEventListener('click', function() {
                // 更新活动状态
                sourceItems.forEach(i => i.classList.remove('active'));
                this.classList.add('active');

                const source = this.getAttribute('data-source');

                // 过滤新闻卡片
                newsCards.forEach(card => {
                    if (source === 'all' || card.getAttribute('data-source') === source) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                });

                // 更新统计
                updateNewsStats();
            });
        });

        // 更新新闻统计
        function updateNewsStats() {
            const visibleCards = document.querySelectorAll('.news-card[style*="display: block"]');
            document.getElementById('totalNews').textContent = visibleCards.length;
        }

        // 自动刷新功能（1800秒 = 30分钟）
        const REFRESH_INTERVAL = 1800000;

        function autoRefresh() {
            // 显示刷新指示器
            const indicator = document.getElementById('refreshIndicator');
            indicator.classList.add('show');

            // 重新加载页面
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        }

        // 启动自动刷新定时器
        let refreshTimer = setTimeout(autoRefresh, REFRESH_INTERVAL);

        // 当用户活动时，重置定时器
        document.addEventListener('mousemove', resetRefreshTimer);
        document.addEventListener('keypress', resetRefreshTimer);
        document.addEventListener('scroll', resetRefreshTimer);

        function resetRefreshTimer() {
            clearTimeout(refreshTimer);
            refreshTimer = setTimeout(autoRefresh, REFRESH_INTERVAL);
        }
    </script>
</body>
</html>
"""

        # 准备模板数据
        news_sources = sorted(list(set(news_item['source'] for news_item in news)))
        source_names = {source: NEWS_SOURCES[next(key for key, value in NEWS_SOURCES.items() if value['name'] == source)]['name'] for source in news_sources}

        # 格式化时间
        for item in news:
            try:
                crawl_time = datetime.fromisoformat(item['crawl_time'])
                item['formatted_time'] = crawl_time.strftime('%Y-%m-%d %H:%M:%S')
            except:
                item['formatted_time'] = '未知时间'

        # 渲染模板
        from jinja2 import Template
        template = Template(html_template)
        html_content = template.render(
            news=news,
            news_sources=news_sources,
            source_names=source_names,
            total_news=len(news),
            last_update=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

        # 保存HTML文件
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"HTML页面已生成: {filename}")
        return True

    except Exception as e:
        logger.error(f"生成HTML页面失败: {e}")
        return False

def main():
    """主函数"""
    logger.info("="*50)
    logger.info("启动全球新闻标题聚合器")
    logger.info("="*50)

    try:
        # 抓取新闻
        news = crawl_all_news()

        if not news:
            logger.error("没有抓取到任何新闻")
            return False

        # 保存到JSON
        save_news_to_file(news)

        # 生成HTML页面
        generate_html_page(news)

        logger.info("新闻聚合完成！")
        return True

    except Exception as e:
        logger.error(f"新闻聚合失败: {e}")
        return False

if __name__ == "__main__":
    main()
