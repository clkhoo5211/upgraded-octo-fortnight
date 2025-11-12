/**
 * 使用Global News Aggregator API的JavaScript/Node.js示例
 * 可以在任何Node.js项目中使用
 */

const API_BASE = 'https://upgraded-octo-fortnight.vercel.app';

class NewsAPI {
    constructor(baseUrl = API_BASE) {
        this.baseUrl = baseUrl;
    }

    /**
     * 搜索新闻
     * @param {Object} options - 搜索选项
     * @returns {Promise<Object>} 新闻列表
     */
    async searchNews(options = {}) {
        const {
            keywords = null,
            categories = null,
            languages = 'all',
            dateRange = 'today_and_yesterday',
            maxResults = 50
        } = options;

        try {
            const response = await fetch(`${this.baseUrl}/api/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    keywords,
                    categories,
                    languages,
                    date_range: dateRange,
                    max_results: maxResults
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            return {
                success: false,
                error: error.message,
                count: 0,
                news: []
            };
        }
    }

    /**
     * 下载新闻完整内容
     * @param {string} newsUrl - 新闻URL
     * @param {Object} options - 选项
     * @returns {Promise<Object>} 完整内容
     */
    async downloadContent(newsUrl, options = {}) {
        const {
            includeImages = true,
            includeBanners = true
        } = options;

        try {
            const response = await fetch(`${this.baseUrl}/api/download`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    news_url: newsUrl,
                    include_images: includeImages,
                    include_banners: includeBanners
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * 完整归档（搜索+下载+保存）
     * @param {Object} options - 归档选项
     * @returns {Promise<Object>} 归档结果
     */
    async archiveNews(options = {}) {
        const {
            keywords = null,
            categories = null,
            maxResults = 50,
            downloadContent = true,
            saveToGitHub = false,
            saveFormat = 'md_with_html'
        } = options;

        try {
            const response = await fetch(`${this.baseUrl}/api/archive`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    keywords,
                    categories,
                    max_results: maxResults,
                    download_content: downloadContent,
                    save_to_github: saveToGitHub,
                    save_format: saveFormat
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * 获取所有分类
     * @returns {Promise<Object>} 分类列表
     */
    async getCategories() {
        try {
            const response = await fetch(`${this.baseUrl}/api/manage_categories`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * 健康检查
     * @returns {Promise<Object>} 健康状态
     */
    async healthCheck() {
        try {
            const response = await fetch(`${this.baseUrl}/api/health`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            return {
                status: 'unhealthy',
                error: error.message
            };
        }
    }
}

// 使用示例
async function main() {
    const api = new NewsAPI();

    // 1. 健康检查
    console.log('🔍 检查API状态...');
    const health = await api.healthCheck();
    console.log(`状态: ${health.status || 'unknown'}\n`);

    // 2. 搜索科技新闻
    console.log('📰 搜索科技新闻...');
    const results = await api.searchNews({
        keywords: 'AI',
        categories: ['tech'],
        maxResults: 5,
        dateRange: 'today_and_yesterday'
    });

    if (results.success && results.count > 0) {
        console.log(`✅ 找到 ${results.count} 条新闻\n`);

        // 显示前3条新闻
        results.news.slice(0, 3).forEach((news, i) => {
            console.log(`${i + 1}. ${news.title || 'N/A'}`);
            console.log(`   来源: ${news.source || 'N/A'}`);
            console.log(`   链接: ${news.url || 'N/A'}\n`);
        });

        // 3. 下载第一条新闻的完整内容
        if (results.news.length > 0) {
            const firstNews = results.news[0];
            console.log(`📥 下载完整内容: ${firstNews.title?.substring(0, 50)}...`);
            const content = await api.downloadContent(firstNews.url);

            if (content.success) {
                console.log(`✅ 内容长度: ${content.content?.length || 0} 字符`);
                console.log(`✅ 图片数: ${content.images?.length || 0}`);
                console.log(`✅ 视频数: ${content.videos?.length || 0}`);
            } else {
                console.log(`❌ 下载失败: ${content.error}`);
            }
        }
    } else {
        console.log(`❌ 搜索失败: ${results.error || '未知错误'}`);
    }

    // 4. 查看所有分类
    console.log('\n📁 查看所有分类...');
    const categories = await api.getCategories();
    if (categories.success) {
        const categoryList = Object.keys(categories.categories || {});
        console.log(`✅ 找到 ${categoryList.length} 个分类:`);
        categoryList.forEach(cat => {
            const keywords = categories.categories[cat] || [];
            console.log(`   - ${cat}: ${keywords.length} 个关键词`);
        });
    } else {
        console.log(`❌ 获取分类失败: ${categories.error}`);
    }
}

// 如果在Node.js环境中运行
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NewsAPI;
}

// 如果在浏览器环境中运行
if (typeof window !== 'undefined') {
    window.NewsAPI = NewsAPI;
}

// 如果直接运行
if (require.main === module) {
    main().catch(console.error);
}

