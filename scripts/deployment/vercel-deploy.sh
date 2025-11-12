#!/bin/bash

###############################################################################
# Vercel部署脚本
# 功能: 自动部署全网新闻聚合MCP服务到Vercel
###############################################################################

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 主函数
main() {
    print_info "开始部署全网新闻聚合服务到Vercel..."
    echo ""
    
    # 1. 检查Vercel CLI
    print_info "检查Vercel CLI..."
    if ! command_exists vercel; then
        print_error "Vercel CLI未安装"
        print_info "请运行: npm install -g vercel"
        exit 1
    fi
    print_success "Vercel CLI已安装"
    
    # 2. 检查是否在正确的目录
    if [ ! -f "vercel.json" ]; then
        print_error "未找到vercel.json文件"
        print_info "请确保在global-news-mcp目录下运行此脚本"
        exit 1
    fi
    print_success "找到vercel.json配置文件"
    
    # 3. 检查必需文件
    print_info "检查必需文件..."
    required_files=(
        "requirements.txt"
        "api/index.py"
        "api/search.py"
        "api/download.py"
        "api/health.py"
        "src/news_tools/__init__.py"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "未找到必需文件: $file"
            exit 1
        fi
    done
    print_success "所有必需文件已就绪"
    
    # 4. 询问部署类型
    echo ""
    print_info "选择部署类型:"
    echo "  1) 预览部署 (Preview)"
    echo "  2) 生产部署 (Production)"
    read -p "请选择 [1/2]: " deploy_type
    
    # 5. 询问是否配置环境变量
    echo ""
    print_warning "部署前请确保已在Vercel Dashboard配置环境变量"
    print_info "必需的环境变量:"
    echo "  - ENABLE_NEWS_FILTER=true"
    print_info "可选的环境变量:"
    echo "  - NEWSAPI_KEY"
    echo "  - BING_API_KEY"
    echo "  - SERPAPI_KEY"
    echo "  - GOOGLE_SEARCH_API_KEY"
    echo "  - GOOGLE_SEARCH_ENGINE_ID"
    echo "  - GITHUB_TOKEN"
    echo ""
    read -p "是否已配置环境变量? [y/N]: " env_configured
    
    if [[ ! "$env_configured" =~ ^[Yy]$ ]]; then
        print_warning "请先在Vercel Dashboard配置环境变量"
        print_info "访问: https://vercel.com/dashboard"
        print_info "选择项目 -> Settings -> Environment Variables"
        read -p "配置完成后按Enter继续..."
    fi
    
    # 6. 开始部署
    echo ""
    print_info "开始部署..."
    
    if [ "$deploy_type" == "2" ]; then
        print_info "执行生产部署..."
        vercel --prod
    else
        print_info "执行预览部署..."
        vercel
    fi
    
    # 7. 部署成功
    echo ""
    print_success "部署完成！"
    echo ""
    print_info "下一步:"
    echo "  1. 访问Vercel提供的URL测试API"
    echo "  2. 测试健康检查: curl https://your-domain.vercel.app/api/health"
    echo "  3. 测试搜索功能: curl https://your-domain.vercel.app/api/search?max_results=5"
    echo "  4. 查看日志: vercel logs"
    echo ""
    print_info "详细文档: DEPLOYMENT.md"
}

# 运行主函数
main
