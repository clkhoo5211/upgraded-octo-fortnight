"""
新闻搜索和聚合模块
支持多个新闻API和RSS源，以及全网搜索引擎
"""
import os
import httpx
import feedparser
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
from .news_filter import NewsFilter
from .category_manager import CategoryManager


class NewsSearcher:
    """新闻搜索器类"""
    
    # 新闻分类映射 - 扩展关键词列表
    CATEGORY_KEYWORDS = {
        'politics': [
            # 中文关键词
            '政治', '政府', '选举', '投票', '议会', '国会', '参议院', '众议院', 
            '总统', '总理', '首相', '部长', '官员', '政策', '法案', '法律', 
            '立法', '司法', '法院', '最高法院', '宪法', '民主', '共和', 
            '政党', '竞选', '候选人', '执政', '反对党', '内阁', '外交', 
            '内政', '国防', '安全', '情报', '反恐', '军事', '军队', '军费',
            '政治危机', '政变', '抗议', '示威', '罢工', '公投', '全民投票',
            # 英文关键词
            'politics', 'government', 'election', 'vote', 'voting', 'parliament', 
            'congress', 'senate', 'house', 'president', 'prime minister', 'minister',
            'policy', 'bill', 'law', 'legislation', 'judiciary', 'court', 'supreme court',
            'constitution', 'democracy', 'republic', 'party', 'campaign', 'candidate',
            'administration', 'opposition', 'cabinet', 'diplomacy', 'domestic', 'defense',
            'security', 'intelligence', 'counter-terrorism', 'military', 'armed forces',
            'political crisis', 'coup', 'protest', 'demonstration', 'strike', 'referendum'
        ],
        'finance': [
            # 中文关键词
            '财经', '金融', '股票', '经济', '股市', '证券', '期货', '外汇',
            '银行', '央行', '利率', '汇率', '通胀', '通缩', 'GDP', 'CPI',
            '投资', '基金', '债券', '保险', '信贷', '贷款', '债务', '赤字',
            '预算', '财政', '税收', '关税', '贸易', '出口', '进口', '顺差',
            '逆差', '市场', '交易所', '纳斯达克', '道琼斯', '标普', '恒生',
            '上证', '深证', '创业板', '科创板', 'A股', '港股', '美股',
            '财报', '盈利', '亏损', '营收', '利润', '市值', '估值', 'IPO',
            '并购', '收购', '重组', '破产', '清算', '监管', '合规', '审计',
            # 英文关键词
            'finance', 'economy', 'economic', 'stock', 'stocks', 'market', 'securities',
            'futures', 'forex', 'bank', 'central bank', 'interest rate', 'exchange rate',
            'inflation', 'deflation', 'GDP', 'CPI', 'investment', 'fund', 'bond',
            'insurance', 'credit', 'loan', 'debt', 'deficit', 'budget', 'fiscal',
            'tax', 'tariff', 'trade', 'export', 'import', 'surplus', 'deficit',
            'exchange', 'NASDAQ', 'Dow Jones', 'S&P', 'Hang Seng', 'IPO', 'earnings',
            'revenue', 'profit', 'loss', 'market cap', 'valuation', 'merger', 'acquisition',
            'bankruptcy', 'regulation', 'compliance', 'audit', 'financial report'
        ],
        'crypto': [
            # 中文关键词
            '加密货币', '比特币', '以太坊', '数字货币', '虚拟货币', '代币',
            'BTC', 'ETH', 'USDT', 'USDC', 'BNB', 'SOL', 'ADA', 'DOT', 'MATIC',
            '狗狗币', 'DOGE', '柴犬币', 'SHIB', '瑞波币', 'XRP', '莱特币', 'LTC',
            '币安', 'Binance', 'Coinbase', '交易所', '挖矿', '矿工', '矿池',
            '钱包', '冷钱包', '热钱包', '私钥', '公钥', '区块链', '去中心化',
            'DeFi', 'NFT', '非同质化代币', '元宇宙', 'Web3', '智能合约',
            'ICO', 'IEO', 'IDO', '空投', '质押', '流动性', '流动性挖矿',
            '稳定币', '算法稳定币', '央行数字货币', 'CBDC', '数字人民币',
            '加密', '加密资产', '加密市场', '牛市', '熊市', '暴涨', '暴跌',
            '监管', '禁令', '合法化', '税收', '征税', '洗钱', '反洗钱',
            # 英文关键词
            'crypto', 'cryptocurrency', 'bitcoin', 'ethereum', 'digital currency',
            'virtual currency', 'token', 'BTC', 'ETH', 'USDT', 'USDC', 'BNB', 'SOL',
            'ADA', 'DOT', 'MATIC', 'DOGE', 'SHIB', 'XRP', 'LTC', 'Binance', 'Coinbase',
            'exchange', 'mining', 'miner', 'pool', 'wallet', 'cold wallet', 'hot wallet',
            'private key', 'public key', 'blockchain', 'decentralized', 'DeFi', 'NFT',
            'non-fungible token', 'metaverse', 'Web3', 'smart contract', 'ICO', 'IEO',
            'IDO', 'airdrop', 'staking', 'liquidity', 'yield farming', 'stablecoin',
            'algorithmic stablecoin', 'CBDC', 'central bank digital currency',
            'encryption', 'crypto asset', 'crypto market', 'bull market', 'bear market',
            'surge', 'crash', 'regulation', 'ban', 'legalization', 'tax', 'taxation',
            'money laundering', 'anti-money laundering', 'AML'
        ],
        'blockchain': [
            # 中文关键词
            '区块链', '链', '分布式账本', '共识机制', '工作量证明', 'PoW',
            '权益证明', 'PoS', '委托权益证明', 'DPoS', '拜占庭容错', 'BFT',
            '哈希', '哈希值', '区块', '区块高度', '区块奖励', '交易',
            '交易费', 'Gas费', 'Gas', '确认', '确认数', '双花', '51%攻击',
            '分叉', '硬分叉', '软分叉', '主链', '侧链', '跨链', '互操作性',
            'Layer2', '二层网络', '扩容', 'TPS', '吞吐量', '可扩展性',
            '零知识证明', 'ZKP', '隐私', '匿名', '可追溯', '不可篡改',
            '智能合约', 'DApp', '去中心化应用', 'DAO', '去中心化自治组织',
            '治理', '投票', '提案', '代币经济学', '通证经济', '销毁',
            '锁仓', '解锁', '释放', '质押', '流动性', '流动性池',
            'AMM', '自动做市商', 'DEX', '去中心化交易所', 'CEX', '中心化交易所',
            '跨链桥', '桥接', '多链', '公链', '私链', '联盟链', '许可链',
            # 英文关键词
            'blockchain', 'chain', 'distributed ledger', 'consensus', 'proof of work',
            'PoW', 'proof of stake', 'PoS', 'delegated proof of stake', 'DPoS',
            'byzantine fault tolerance', 'BFT', 'hash', 'block', 'block height',
            'block reward', 'transaction', 'transaction fee', 'gas', 'gas fee',
            'confirmation', 'double spending', '51% attack', 'fork', 'hard fork',
            'soft fork', 'main chain', 'sidechain', 'cross-chain', 'interoperability',
            'Layer2', 'scaling', 'TPS', 'throughput', 'scalability', 'zero-knowledge proof',
            'ZKP', 'privacy', 'anonymous', 'traceable', 'immutable', 'smart contract',
            'DApp', 'decentralized application', 'DAO', 'decentralized autonomous organization',
            'governance', 'voting', 'proposal', 'tokenomics', 'burn', 'lock', 'unlock',
            'release', 'staking', 'liquidity', 'liquidity pool', 'AMM', 'automated market maker',
            'DEX', 'decentralized exchange', 'CEX', 'centralized exchange', 'bridge',
            'bridging', 'multi-chain', 'public chain', 'private chain', 'consortium chain'
        ],
        'fengshui': [
            # 中文关键词
            '风水', '玄学', '命理', '八字', '紫微', '六爻', '奇门', '太乙',
            '六壬', '梅花易数', '面相', '手相', '姓名学', '择日', '择时',
            '堪舆', '地理', '阴阳', '五行', '八卦', '九宫', '罗盘', '指南针',
            '龙脉', '穴位', '砂水', '朝向', '坐向', '旺位', '衰位', '财位',
            '文昌位', '桃花位', '健康位', '事业位', '官位', '贵人', '小人',
            '化煞', '辟邪', '开运', '改运', '转运', '招财', '纳福', '聚气',
            '藏风', '得水', '山环水抱', '背山面水', '左青龙', '右白虎',
            '前朱雀', '后玄武', '天干', '地支', '生肖', '属相', '本命年',
            '犯太岁', '冲太岁', '刑太岁', '害太岁', '破太岁', '值太岁',
            '流年', '大运', '小运', '流月', '流日', '流时', '神煞', '吉神',
            '凶神', '喜用神', '忌神', '仇神', '闲神', '格局', '用神',
            '命主', '身主', '命宫', '身宫', '财帛宫', '官禄宫', '迁移宫',
            '疾厄宫', '夫妻宫', '子女宫', '兄弟宫', '父母宫', '福德宫',
            '田宅宫', '奴仆宫', '星曜', '主星', '辅星', '煞星', '化星',
            # 英文关键词
            'fengshui', 'feng shui', 'metaphysics', 'fortune telling', 'divination',
            'astrology', 'horoscope', 'zodiac', 'Chinese astrology', 'BaZi', 'Four Pillars',
            'Zi Wei Dou Shu', 'I Ching', 'Book of Changes', 'face reading', 'palm reading',
            'geomancy', 'geography', 'yin yang', 'five elements', 'eight trigrams',
            'nine palaces', 'compass', 'dragon vein', 'acupoint', 'orientation', 'direction',
            'auspicious', 'inauspicious', 'wealth position', 'career position', 'health position',
            'romance position', 'ward off evil', 'attract wealth', 'good fortune', 'luck',
            'destiny', 'fate', 'fortune', 'auspicious time', 'lucky day', 'Chinese calendar'
        ],
        'tech': [
            # 中文关键词
            '科技', '技术', 'AI', '人工智能', '机器学习', '深度学习', '神经网络',
            '自然语言处理', 'NLP', '计算机视觉', 'CV', '语音识别', '图像识别',
            '算法', '大数据', '云计算', '云服务', 'AWS', 'Azure', 'GCP',
            '边缘计算', '物联网', 'IoT', '5G', '6G', '通信', '网络', '互联网',
            '移动互联网', '智能手机', 'iPhone', 'Android', 'iOS', '鸿蒙', 'HarmonyOS',
            '芯片', '半导体', 'CPU', 'GPU', 'NPU', '处理器', '内存', '存储',
            'SSD', '硬盘', '显示器', '屏幕', 'OLED', 'LCD', 'LED', '量子计算',
            '量子计算机', '量子通信', '量子加密', '量子纠缠', '量子比特', '量子',
            '虚拟现实', 'VR', '增强现实', 'AR', '混合现实', 'MR', '元宇宙',
            'Metaverse', '数字孪生', '机器人', '自动化', '无人机', '自动驾驶',
            '新能源汽车', '电动车', '特斯拉', 'Tesla', '充电桩', '电池', '锂电池',
            '固态电池', '氢能源', '燃料电池', '太阳能', '风能', '可再生能源',
            '软件', '硬件', '操作系统', 'Windows', 'Linux', 'macOS', '开源',
            '编程', '代码', '开发', '程序员', '工程师', '架构师', '产品经理',
            '创业', '初创公司', '独角兽', 'IPO', '融资', '投资', '风投', 'VC',
            'PE', '天使投资', 'A轮', 'B轮', 'C轮', 'D轮', '上市', '退市',
            '专利', '知识产权', '商标', '版权', '创新', '研发', 'R&D',
            # 英文关键词
            'tech', 'technology', 'AI', 'artificial intelligence', 'machine learning',
            'deep learning', 'neural network', 'NLP', 'natural language processing',
            'computer vision', 'CV', 'speech recognition', 'image recognition', 'algorithm',
            'big data', 'cloud computing', 'cloud service', 'AWS', 'Azure', 'GCP',
            'edge computing', 'IoT', 'internet of things', '5G', '6G', 'communication',
            'network', 'internet', 'mobile internet', 'smartphone', 'iPhone', 'Android',
            'iOS', 'chip', 'semiconductor', 'CPU', 'GPU', 'NPU', 'processor', 'memory',
            'storage', 'SSD', 'display', 'screen', 'OLED', 'LCD', 'LED', 'quantum computing',
            'quantum computer', 'quantum communication', 'quantum encryption', 'quantum',
            'VR', 'virtual reality', 'AR', 'augmented reality', 'MR', 'mixed reality',
            'metaverse', 'digital twin', 'robot', 'robotics', 'automation', 'drone',
            'autonomous driving', 'self-driving', 'electric vehicle', 'EV', 'Tesla',
            'charging station', 'battery', 'lithium battery', 'solid-state battery',
            'hydrogen energy', 'fuel cell', 'solar energy', 'wind energy', 'renewable energy',
            'software', 'hardware', 'operating system', 'OS', 'Windows', 'Linux', 'macOS',
            'open source', 'programming', 'coding', 'development', 'developer', 'engineer',
            'architect', 'product manager', 'startup', 'unicorn', 'IPO', 'funding', 'investment',
            'VC', 'venture capital', 'PE', 'private equity', 'angel investment', 'Series A',
            'Series B', 'Series C', 'Series D', 'listing', 'delisting', 'patent', 'IP',
            'intellectual property', 'trademark', 'copyright', 'innovation', 'R&D', 'research'
        ],
        'social': [
            # 中文关键词
            '社会', '生活', '娱乐', '文化', '艺术', '音乐', '电影', '电视剧',
            '综艺', '明星', '演员', '歌手', '导演', '制片', '票房', '收视率',
            '体育', '足球', '篮球', '乒乓球', '羽毛球', '网球', '游泳', '田径',
            '奥运会', '世界杯', '锦标赛', '联赛', '球员', '教练', '裁判', '球迷',
            '美食', '餐厅', '料理', '烹饪', '食谱', '健康', '养生', '健身',
            '运动', '瑜伽', '跑步', '骑行', '旅游', '旅行', '景点', '酒店',
            '民宿', '交通', '出行', '购物', '消费', '时尚', '服装', '化妆品',
            '美容', '护肤', '整形', '医美', '教育', '学校', '大学', '中学',
            '小学', '幼儿园', '老师', '学生', '考试', '高考', '考研', '留学',
            '就业', '招聘', '求职', '面试', '薪资', '工资', '福利', '社保',
            '医保', '养老', '退休', '住房', '买房', '租房', '装修', '家具',
            '家电', '汽车', '驾照', '交通', '出行', '地铁', '公交', '出租车',
            '网约车', '共享单车', '共享汽车', '环保', '垃圾分类', '节能减排',
            '公益', '慈善', '志愿者', '捐赠', '救助', '扶贫', '助残', '助学',
            '医疗', '医院', '医生', '护士', '药品', '疫苗', '疾病', '健康',
            '心理', '心理咨询', '心理健康', '抑郁症', '焦虑', '压力', '情绪',
            '家庭', '婚姻', '恋爱', '分手', '离婚', '孩子', '教育', '育儿',
            '老人', '养老', '退休', '社区', '邻里', '朋友', '社交', '聚会',
            # 英文关键词
            'social', 'society', 'life', 'lifestyle', 'entertainment', 'culture', 'art',
            'music', 'movie', 'film', 'TV', 'television', 'show', 'celebrity', 'actor',
            'singer', 'director', 'producer', 'box office', 'ratings', 'sports', 'football',
            'soccer', 'basketball', 'tennis', 'swimming', 'track', 'Olympics', 'World Cup',
            'championship', 'league', 'player', 'coach', 'referee', 'fan', 'food', 'restaurant',
            'cuisine', 'cooking', 'recipe', 'health', 'fitness', 'exercise', 'yoga', 'running',
            'cycling', 'travel', 'tourism', 'attraction', 'hotel', 'transportation', 'shopping',
            'consumption', 'fashion', 'clothing', 'cosmetics', 'beauty', 'skincare', 'plastic surgery',
            'education', 'school', 'university', 'college', 'teacher', 'student', 'exam', 'test',
            'employment', 'job', 'recruitment', 'interview', 'salary', 'wage', 'benefits', 'insurance',
            'healthcare', 'medical', 'hospital', 'doctor', 'nurse', 'medicine', 'vaccine', 'disease',
            'mental health', 'psychology', 'depression', 'anxiety', 'stress', 'emotion', 'family',
            'marriage', 'relationship', 'dating', 'divorce', 'children', 'parenting', 'elderly', 'retirement',
            'community', 'neighbor', 'friend', 'social', 'gathering', 'charity', 'volunteer', 'donation'
        ],
        'international': [
            # 中文关键词
            '国际', '世界', '全球', '跨国', '多边', '双边', '外交', '外事',
            '联合国', 'UN', '安理会', '世界银行', 'IMF', '国际货币基金组织',
            'WTO', '世界贸易组织', 'WHO', '世界卫生组织', 'G7', 'G20', '金砖国家',
            'BRICS', '欧盟', 'EU', '北约', 'NATO', '东盟', 'ASEAN', 'APEC',
            '一带一路', 'Belt and Road', 'BRI', 'RCEP', '区域全面经济伙伴关系',
            '贸易战', '关税', '制裁', '禁运', '封锁', '冲突', '战争', '和平',
            '停火', '停战', '和谈', '谈判', '协议', '条约', '公约', '协定',
            '峰会', '会议', '论坛', '对话', '合作', '伙伴关系', '战略伙伴',
            '全面战略伙伴', '友好', '建交', '断交', '复交', '互访', '访问',
            '出访', '来访', '接待', '会见', '会谈', '磋商', '交流', '交往',
            '移民', '难民', '庇护', '签证', '护照', '出入境', '海关', '边检',
            '领事', '大使', '大使馆', '领事馆', '外交官', '外交使团', '特使',
            '国际法', '国际关系', '国际秩序', '国际规则', '国际标准', '国际惯例',
            '全球化', '反全球化', '逆全球化', '多极化', '单边主义', '多边主义',
            '保护主义', '自由贸易', '公平贸易', '开放', '封闭', '孤立', '脱钩',
            '供应链', '产业链', '价值链', '分工', '合作', '竞争', '博弈',
            '地缘政治', '地缘经济', '地缘战略', '势力范围', '影响力', '软实力',
            '硬实力', '综合国力', '国际地位', '话语权', '主导权', '领导力',
            # 英文关键词
            'international', 'world', 'global', 'multinational', 'multilateral', 'bilateral',
            'diplomacy', 'foreign affairs', 'United Nations', 'UN', 'Security Council',
            'World Bank', 'IMF', 'International Monetary Fund', 'WTO', 'World Trade Organization',
            'WHO', 'World Health Organization', 'G7', 'G20', 'BRICS', 'EU', 'European Union',
            'NATO', 'ASEAN', 'APEC', 'Belt and Road', 'BRI', 'RCEP', 'trade war', 'tariff',
            'sanctions', 'embargo', 'blockade', 'conflict', 'war', 'peace', 'ceasefire',
            'truce', 'peace talks', 'negotiation', 'agreement', 'treaty', 'convention',
            'summit', 'conference', 'forum', 'dialogue', 'cooperation', 'partnership',
            'strategic partnership', 'friendship', 'diplomatic relations', 'visit', 'meeting',
            'talks', 'consultation', 'exchange', 'interaction', 'immigration', 'refugee',
            'asylum', 'visa', 'passport', 'customs', 'border', 'consul', 'ambassador',
            'embassy', 'consulate', 'diplomat', 'diplomatic mission', 'envoy', 'international law',
            'international relations', 'international order', 'international rules', 'international standards',
            'globalization', 'anti-globalization', 'de-globalization', 'multipolarity', 'unilateralism',
            'multilateralism', 'protectionism', 'free trade', 'fair trade', 'open', 'closed',
            'isolation', 'decoupling', 'supply chain', 'industrial chain', 'value chain',
            'division of labor', 'cooperation', 'competition', 'game', 'geopolitics', 'geo-economics',
            'geostrategy', 'sphere of influence', 'influence', 'soft power', 'hard power',
            'comprehensive national power', 'international status', 'discourse power', 'leadership'
        ]
    }
    
    # RSS源配置
    RSS_FEEDS = {
        'zh': [
            'http://rss.sina.com.cn/news/china/focus15.xml',  # 新浪新闻
            'http://www.people.com.cn/rss/politics.xml',  # 人民网政治
            'http://www.chinanews.com/rss/scroll-news.xml',  # 中新网
        ],
        'en': [
            'http://feeds.bbci.co.uk/news/rss.xml',  # BBC News
            'http://rss.cnn.com/rss/edition.rss',  # CNN
            'https://feeds.reuters.com/reuters/topNews',  # Reuters
        ]
    }
    
    def __init__(
        self, 
        newsapi_key: Optional[str] = None, 
        newsdata_key: Optional[str] = None,
        bing_api_key: Optional[str] = None,
        serpapi_key: Optional[str] = None,
        google_search_key: Optional[str] = None,
        google_engine_id: Optional[str] = None,
        enable_filter: bool = True,
        custom_filter: Optional[NewsFilter] = None
    ):
        """
        初始化新闻搜索器
        
        Args:
            newsapi_key: NewsAPI.org API密钥
            newsdata_key: NewsData.io API密钥
            bing_api_key: Bing Search API密钥（用于全网搜索）
            serpapi_key: SerpAPI密钥（用于多搜索引擎支持）
            google_search_key: Google Custom Search API密钥
            google_engine_id: Google Custom Search Engine ID
            enable_filter: 是否启用智能过滤
            custom_filter: 自定义过滤器（如果不提供则使用默认）
        """
        self.newsapi_key = newsapi_key or os.getenv('NEWSAPI_KEY')
        self.newsdata_key = newsdata_key or os.getenv('NEWSDATA_KEY')
        self.bing_api_key = bing_api_key or os.getenv('BING_API_KEY')
        self.serpapi_key = serpapi_key or os.getenv('SERPAPI_KEY')
        self.google_search_key = google_search_key or os.getenv('GOOGLE_SEARCH_API_KEY')
        self.google_engine_id = google_engine_id or os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # 分类管理器（加载自定义分类）
        self.category_manager = CategoryManager()
        # 更新CATEGORY_KEYWORDS以包含自定义分类
        self.CATEGORY_KEYWORDS = self.category_manager.get_all_categories()
        
        # 智能过滤器
        self.enable_filter = enable_filter
        if enable_filter:
            self.news_filter = custom_filter or NewsFilter.create_default_filter()
        else:
            self.news_filter = None
    
    async def search_news(
        self,
        keywords: Optional[str] = None,
        categories: Optional[List[str]] = None,
        languages: str = 'all',
        date_range: str = 'today_and_yesterday',
        sources: Optional[List[str]] = None,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        搜索和聚合新闻
        
        Args:
            keywords: 搜索关键词
            categories: 新闻分类列表
            languages: 语言过滤 (zh/en/all)
            date_range: 日期范围 (today_and_yesterday/yesterday/today/last_7_days/last_30_days)
                        默认: today_and_yesterday (当日和前一日的新闻)
            sources: 指定新闻源
            max_results: 最大结果数
            
        Returns:
            新闻数据列表
        """
        all_news = []
        
        # 从不同源搜索新闻
        tasks = []
        
        # 1. NewsAPI.org
        if self.newsapi_key:
            tasks.append(self._search_newsapi(keywords, languages, date_range, max_results))
        
        # 2. NewsData.io
        if self.newsdata_key:
            tasks.append(self._search_newsdata(keywords, languages, date_range, max_results))
        
        # 3. RSS源
        tasks.append(self._search_rss(languages))
        
        # 3. Bing News Search（全网搜索）
        if self.bing_api_key:
            tasks.append(self._search_bing_news(keywords, languages, max_results))
        
        # 4. Google News（免费RSS）
        tasks.append(self._search_google_news(keywords, languages, max_results))
        
        # 5. Hacker News (仅当日最新，不包含历史热门)
        # 注意：Hacker News默认返回最新新闻，不是历史热门，符合需求
        if languages in ['en', 'all'] and date_range in ['today_and_yesterday', 'today', 'yesterday']:
            tasks.append(self._search_hackernews(20))
        
        # 6. Product Hunt
        if languages in ['en', 'all']:
            tasks.append(self._search_producthunt(20))
        
        # 7. 搜索引擎搜索（SerpAPI）
        if keywords and self.serpapi_key:
            tasks.append(self._search_serpapi(keywords, max_results))
        
        # 8. 搜索引擎搜索（Google Custom Search）
        if keywords and self.google_search_key and self.google_engine_id:
            tasks.append(self._search_google_custom(keywords, max_results))
        
        # 9. 自定义搜索链接（从环境变量读取）
        custom_links = os.getenv('CUSTOM_NEWS_LINKS', '').split(',')
        for link in custom_links:
            if link.strip():
                tasks.append(self._search_custom_link(link.strip()))
        
        # 并行执行所有搜索
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 合并结果
        for result in results:
            if isinstance(result, list):
                all_news.extend(result)
        
        # 过滤和分类
        filtered_news = self._filter_and_classify(
            all_news, 
            keywords, 
            categories,
            languages
        )
        
        # 去重
        unique_news = self._deduplicate(filtered_news)
        
        # 排序（按时间倒序）
        unique_news.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        
        return unique_news[:max_results]
    
    async def _search_newsapi(
        self,
        keywords: Optional[str],
        languages: str,
        date_range: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """使用NewsAPI.org搜索新闻"""
        if not self.newsapi_key:
            return []
        
        try:
            # 构建日期参数
            date_from = self._get_date_from(date_range)
            
            # 构建语言参数
            lang_param = ''
            if languages == 'zh':
                lang_param = 'zh'
            elif languages == 'en':
                lang_param = 'en'
            
            url = 'https://newsapi.org/v2/everything'
            params = {
                'apiKey': self.newsapi_key,
                'q': keywords or 'news',
                'from': date_from,
                'sortBy': 'publishedAt',
                'pageSize': min(max_results, 100)
            }
            
            if lang_param:
                params['language'] = lang_param
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # 转换为统一格式
            news_list = []
            for article in data.get('articles', []):
                news_list.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'content': article.get('content', ''),
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', 'NewsAPI'),
                    'published_at': article.get('publishedAt', ''),
                    'image_url': article.get('urlToImage', ''),
                    'language': self._detect_language(article.get('title', '')),
                    'category': ''  # 稍后分类
                })
            
            return news_list
        except Exception as e:
            print(f"NewsAPI搜索错误: {e}")
            return []
    
    async def _search_newsdata(
        self,
        keywords: Optional[str],
        languages: str,
        date_range: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """使用NewsData.io搜索新闻"""
        if not self.newsdata_key:
            return []
        
        try:
            # 构建语言参数
            lang_param = ''
            if languages == 'zh':
                lang_param = 'zh'
            elif languages == 'en':
                lang_param = 'en'
            
            url = 'https://newsdata.io/api/1/news'
            params = {
                'apikey': self.newsdata_key,
                'q': keywords or '',
            }
            
            if lang_param:
                params['language'] = lang_param
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # 转换为统一格式
            news_list = []
            for article in data.get('results', []):
                news_list.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'content': article.get('content', ''),
                    'url': article.get('link', ''),
                    'source': article.get('source_id', 'NewsData'),
                    'published_at': article.get('pubDate', ''),
                    'image_url': article.get('image_url', ''),
                    'language': self._detect_language(article.get('title', '')),
                    'category': article.get('category', [''])[0] if article.get('category') else ''
                })
            
            return news_list
        except Exception as e:
            print(f"NewsData搜索错误: {e}")
            return []
    
    async def _search_bing_news(
        self,
        keywords: Optional[str],
        languages: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """使用Bing News Search API搜索全网新闻"""
        if not self.bing_api_key:
            return []
        
        try:
            url = 'https://api.bing.microsoft.com/v7.0/news/search'
            headers = {'Ocp-Apim-Subscription-Key': self.bing_api_key}
            
            # 构建语言参数
            market = 'en-US' if languages == 'en' else 'zh-CN' if languages == 'zh' else 'en-US'
            
            params = {
                'q': keywords or 'news',
                'mkt': market,
                'count': min(max_results, 100),
                'freshness': 'Day',
                'sortBy': 'Date'
            }
            
            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            # 转换为统一格式
            news_list = []
            for article in data.get('value', []):
                news_list.append({
                    'title': article.get('name', ''),
                    'description': article.get('description', ''),
                    'content': article.get('description', ''),
                    'url': article.get('url', ''),
                    'source': article.get('provider', [{}])[0].get('name', 'Bing News'),
                    'published_at': article.get('datePublished', ''),
                    'image_url': article.get('image', {}).get('thumbnail', {}).get('contentUrl', ''),
                    'language': languages if languages != 'all' else 'en',
                    'category': article.get('category', '')
                })
            
            return news_list
        except Exception as e:
            print(f"Bing News搜索错误: {e}")
            return []
    
    async def _search_google_news(
        self,
        keywords: Optional[str],
        languages: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """使用Google RSS搜索新闻（免费替代方案）"""
        try:
            # Google News RSS不需要API key
            lang_code = 'zh-CN' if languages == 'zh' else 'en-US' if languages == 'en' else 'en-US'
            query = keywords or 'news'
            url = f'https://news.google.com/rss/search?q={query}&hl={lang_code}&gl=US&ceid=US:en'
            
            response = await self.client.get(url)
            feed = feedparser.parse(response.text)
            
            news_list = []
            for entry in feed.entries[:max_results]:
                news_list.append({
                    'title': entry.get('title', ''),
                    'description': entry.get('summary', ''),
                    'content': entry.get('summary', ''),
                    'url': entry.get('link', ''),
                    'source': entry.get('source', {}).get('title', 'Google News'),
                    'published_at': entry.get('published', ''),
                    'image_url': '',
                    'language': languages if languages != 'all' else 'en',
                    'category': ''
                })
            
            return news_list
        except Exception as e:
            print(f"Google News搜索错误: {e}")
            return []
    
    async def _search_hackernews(self, max_results: int = 20) -> List[Dict[str, Any]]:
        """搜索Hacker News热门新闻"""
        try:
            # 获取热门故事ID
            url = 'https://hacker-news.firebaseio.com/v0/topstories.json'
            response = await self.client.get(url)
            story_ids = response.json()[:max_results]
            
            # 并发获取故事详情
            tasks = [
                self.client.get(f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json')
                for story_id in story_ids
            ]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            news_list = []
            for response in responses:
                if isinstance(response, Exception):
                    continue
                
                story = response.json()
                if story and story.get('type') == 'story':
                    news_list.append({
                        'title': story.get('title', ''),
                        'description': story.get('text', '')[:200] if story.get('text') else '',
                        'content': story.get('text', ''),
                        'url': story.get('url', f"https://news.ycombinator.com/item?id={story.get('id')}"),
                        'source': 'Hacker News',
                        'published_at': datetime.fromtimestamp(story.get('time', 0)).isoformat() if story.get('time') else '',
                        'image_url': '',
                        'language': 'en',
                        'category': 'tech'
                    })
            
            return news_list
        except Exception as e:
            print(f"Hacker News搜索错误: {e}")
            return []
    
    async def _search_producthunt(self, max_results: int = 20) -> List[Dict[str, Any]]:
        """搜索Product Hunt热门产品（使用公开的GraphQL API）"""
        try:
            # Product Hunt GraphQL API（公开接口）
            url = 'https://www.producthunt.com/frontend/graphql'
            query = '''
            {
              posts(first: %d, order: VOTES) {
                edges {
                  node {
                    id
                    name
                    tagline
                    description
                    url
                    votesCount
                    createdAt
                    featuredAt
                    thumbnail {
                      url
                    }
                  }
                }
              }
            }
            ''' % max_results
            
            response = await self.client.post(url, json={'query': query})
            data = response.json()
            
            news_list = []
            for edge in data.get('data', {}).get('posts', {}).get('edges', []):
                node = edge.get('node', {})
                news_list.append({
                    'title': node.get('name', ''),
                    'description': node.get('tagline', ''),
                    'content': node.get('description', ''),
                    'url': node.get('url', ''),
                    'source': 'Product Hunt',
                    'published_at': node.get('createdAt', ''),
                    'image_url': node.get('thumbnail', {}).get('url', ''),
                    'language': 'en',
                    'category': 'tech'
                })
            
            return news_list
        except Exception as e:
            print(f"Product Hunt搜索错误: {e}")
            return []
    
    async def _search_rss(self, languages: str) -> List[Dict[str, Any]]:
        """从RSS源搜索新闻"""
        news_list = []
        
        # 确定要使用的RSS源
        feeds = []
        if languages == 'zh':
            feeds = self.RSS_FEEDS['zh']
        elif languages == 'en':
            feeds = self.RSS_FEEDS['en']
        else:  # all
            feeds = self.RSS_FEEDS['zh'] + self.RSS_FEEDS['en']
        
        # 解析每个RSS源
        for feed_url in feeds:
            try:
                response = await self.client.get(feed_url)
                feed = feedparser.parse(response.text)
                
                for entry in feed.entries[:10]:  # 每个源最多10条
                    news_list.append({
                        'title': entry.get('title', ''),
                        'description': entry.get('summary', ''),
                        'content': entry.get('content', [{}])[0].get('value', '') if entry.get('content') else '',
                        'url': entry.get('link', ''),
                        'source': feed.feed.get('title', 'RSS Feed'),
                        'published_at': entry.get('published', ''),
                        'image_url': '',
                        'language': self._detect_language(entry.get('title', '')),
                        'category': ''
                    })
            except Exception as e:
                print(f"RSS解析错误 ({feed_url}): {e}")
                continue
        
        return news_list
    
    def _filter_and_classify(
        self,
        news_list: List[Dict[str, Any]],
        keywords: Optional[str],
        categories: Optional[List[str]],
        languages: str
    ) -> List[Dict[str, Any]]:
        """过滤和分类新闻"""
        filtered = []
        
        for news in news_list:
            # 语言过滤
            if languages != 'all':
                if news['language'] != languages:
                    continue
            
            # 关键词过滤
            if keywords:
                text = f"{news['title']} {news['description']}".lower()
                if keywords.lower() not in text:
                    continue
            
            # 使用智能过滤器进行高级过滤
            if self.enable_filter and self.news_filter:
                if not self.news_filter.should_include(news):
                    continue
            
            # 自动分类
            if not news['category']:
                news['category'] = self._classify_news(news)
            
            # 分类过滤
            if categories:
                if news['category'] not in categories:
                    continue
            
            filtered.append(news)
        
        return filtered
    
    def _classify_news(self, news: Dict[str, Any]) -> str:
        """使用关键词分类新闻"""
        text = f"{news['title']} {news['description']}".lower()
        
        # 按优先级匹配分类
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    return category
        
        return 'social'  # 默认分类
    
    def _detect_language(self, text: str) -> str:
        """简单的语言检测"""
        if not text:
            return 'en'
        
        # 检测中文字符
        chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        if chinese_chars > len(text) * 0.3:
            return 'zh'
        
        return 'en'
    
    def _deduplicate(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """根据标题去重"""
        seen_titles = set()
        unique_news = []
        
        for news in news_list:
            title = news['title'].strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_news.append(news)
        
        return unique_news
    
    def _get_date_from(self, date_range: str) -> str:
        """计算起始日期"""
        today = datetime.now()
        
        if date_range == 'yesterday':
            date_from = today - timedelta(days=1)
        elif date_range == 'last_7_days':
            date_from = today - timedelta(days=7)
        elif date_range == 'last_30_days':
            date_from = today - timedelta(days=30)
        else:
            date_from = today - timedelta(days=7)
        
        return date_from.strftime('%Y-%m-%d')
    
    async def _search_custom_link(self, url: str) -> List[Dict[str, Any]]:
        """搜索自定义RSS/JSON链接"""
        try:
            response = await self.client.get(url)
            content_type = response.headers.get('content-type', '')
            
            # 判断是RSS还是JSON
            if 'xml' in content_type or 'rss' in content_type:
                return await self._parse_custom_rss(response.text, url)
            elif 'json' in content_type:
                return await self._parse_custom_json(response.json(), url)
            else:
                # 尝试作为RSS解析
                return await self._parse_custom_rss(response.text, url)
        except Exception as e:
            print(f"自定义链接搜索错误 ({url}): {e}")
            return []
    
    async def _parse_custom_rss(self, text: str, source_url: str) -> List[Dict[str, Any]]:
        """解析自定义RSS源"""
        try:
            feed = feedparser.parse(text)
            news_list = []
            
            for entry in feed.entries[:20]:
                news_list.append({
                    'title': entry.get('title', ''),
                    'description': entry.get('summary', ''),
                    'content': entry.get('content', [{}])[0].get('value', '') if entry.get('content') else '',
                    'url': entry.get('link', ''),
                    'source': f'Custom RSS ({source_url})',
                    'published_at': entry.get('published', ''),
                    'image_url': '',
                    'language': self._detect_language(entry.get('title', '')),
                    'category': ''
                })
            
            return news_list
        except Exception as e:
            print(f"自定义RSS解析错误: {e}")
            return []
    
    async def _parse_custom_json(self, data: Dict[str, Any], source_url: str) -> List[Dict[str, Any]]:
        """解析自定义JSON数据"""
        try:
            # 支持常见的JSON结构
            items = data.get('items', data.get('articles', data.get('data', [])))
            if not isinstance(items, list):
                return []
            
            news_list = []
            for item in items[:20]:
                news_list.append({
                    'title': item.get('title', item.get('name', '')),
                    'description': item.get('description', item.get('summary', '')),
                    'content': item.get('content', item.get('body', '')),
                    'url': item.get('url', item.get('link', '')),
                    'source': f'Custom JSON ({source_url})',
                    'published_at': item.get('published_at', item.get('date', '')),
                    'image_url': item.get('image', item.get('thumbnail', '')),
                    'language': self._detect_language(item.get('title', '')),
                    'category': item.get('category', '')
                })
            
            return news_list
        except Exception as e:
            print(f"自定义JSON解析错误: {e}")
            return []
    
    def load_custom_keywords(self) -> Dict[str, List[str]]:
        """从环境变量加载自定义搜索关键词"""
        custom_keywords = {}
        
        # 从环境变量读取格式: CUSTOM_KEYWORDS=politics:选举,投票;finance:股市,投资
        keywords_str = os.getenv('CUSTOM_KEYWORDS', '')
        if keywords_str:
            try:
                for category_part in keywords_str.split(';'):
                    if ':' in category_part:
                        category, keywords = category_part.split(':', 1)
                        custom_keywords[category.strip()] = [
                            kw.strip() for kw in keywords.split(',')
                        ]
            except Exception as e:
                print(f"自定义关键词解析错误: {e}")
        
        # 合并到默认关键词
        for category, keywords in custom_keywords.items():
            if category in self.CATEGORY_KEYWORDS:
                self.CATEGORY_KEYWORDS[category].extend(keywords)
            else:
                self.CATEGORY_KEYWORDS[category] = keywords
        
        return custom_keywords
    
    async def _search_serpapi(
        self,
        keywords: str,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """使用 SerpAPI 搜索新闻（支持多搜索引擎）"""
        if not self.serpapi_key:
            return []
        
        try:
            url = 'https://serpapi.com/search'
            params = {
                'q': keywords,
                'tbm': 'nws',  # 新闻搜索
                'api_key': self.serpapi_key,
                'num': min(max_results, 100)
            }
            
            response = await self.client.get(url, params=params)
            data = response.json()
            
            news_list = []
            for item in data.get('news_results', []):
                news_list.append({
                    'title': item.get('title', ''),
                    'description': item.get('snippet', ''),
                    'content': item.get('snippet', ''),
                    'url': item.get('link', ''),
                    'source': item.get('source', 'SerpAPI'),
                    'published_at': item.get('date', ''),
                    'image_url': item.get('thumbnail', ''),
                    'language': self._detect_language(item.get('title', '')),
                    'category': ''
                })
            
            return news_list
        except Exception as e:
            print(f"SerpAPI搜索错误: {e}")
            return []
    
    async def _search_google_custom(
        self,
        keywords: str,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """使用 Google Custom Search API 搜索新闻"""
        if not self.google_search_key or not self.google_engine_id:
            return []
        
        try:
            url = 'https://www.googleapis.com/customsearch/v1'
            
            news_list = []
            # Google API 每次最多返回10条，需要分页
            for start in range(1, min(max_results, 100), 10):
                params = {
                    'key': self.google_search_key,
                    'cx': self.google_engine_id,
                    'q': keywords,
                    'start': start,
                    'num': 10
                }
                
                response = await self.client.get(url, params=params)
                data = response.json()
                
                for item in data.get('items', []):
                    pagemap = item.get('pagemap', {})
                    metatags = pagemap.get('metatags', [{}])[0] if pagemap.get('metatags') else {}
                    
                    news_list.append({
                        'title': item.get('title', ''),
                        'description': item.get('snippet', ''),
                        'content': item.get('snippet', ''),
                        'url': item.get('link', ''),
                        'source': item.get('displayLink', 'Google Search'),
                        'published_at': metatags.get('article:published_time', ''),
                        'image_url': pagemap.get('cse_image', [{}])[0].get('src', '') if pagemap.get('cse_image') else '',
                        'language': self._detect_language(item.get('title', '')),
                        'category': ''
                    })
                
                # 如果已经获取足够的结果，停止
                if len(news_list) >= max_results:
                    break
            
            return news_list[:max_results]
        except Exception as e:
            print(f"Google Custom Search错误: {e}")
            return []
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()
