#!/usr/bin/env python3
"""
归档功能验证脚本
测试归档功能并验证GitHub仓库中的文件
"""
import requests
import json
from datetime import datetime
import time

BASE_URL = "https://upgraded-octo-fortnight.vercel.app"
REPO = "clkhoo5211/upgraded-octo-fortnight"

def test_archive():
    """测试归档功能"""
    print("=" * 70)
    print("🚀 执行归档测试")
    print("=" * 70)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/archive",
            json={
                "max_results": 3,
                "download_content": True,
                "save_to_github": True,
                "save_format": "md_with_html"
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"响应: {response.text[:300]}")
            return None
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

def verify_github_files(date_path):
    """验证GitHub仓库中的文件"""
    print("\n" + "=" * 70)
    print("🔍 验证GitHub仓库中的文件")
    print("=" * 70)
    
    try:
        url = f"https://api.github.com/repos/{REPO}/contents/{date_path}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            files = response.json()
            if isinstance(files, list):
                print(f"✅ 找到 {len(files)} 个文件:")
                for file in files:
                    if file.get('type') == 'file':
                        name = file.get('name', '')
                        size = file.get('size', 0)
                        path = file.get('path', '')
                        html_url = file.get('html_url', '')
                        print(f"\n   📄 {name}")
                        print(f"      大小: {size} bytes")
                        print(f"      路径: {path}")
                        print(f"      URL: {html_url}")
                return True
            else:
                print(f"⚠️ 返回的不是文件列表")
                return False
        elif response.status_code == 404:
            print(f"⚠️ 目录不存在: {date_path}")
            print(f"   可能原因:")
            print(f"   - 归档还在处理中（等待几秒后重试）")
            print(f"   - 归档失败")
            return False
        else:
            print(f"⚠️ GitHub API返回: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 检查GitHub文件时出错: {e}")
        return False

def main():
    print("\n" + "=" * 70)
    print("📋 归档功能完整验证")
    print("=" * 70)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API地址: {BASE_URL}")
    print(f"GitHub仓库: {REPO}")
    print()
    
    # 步骤1: 执行归档
    result = test_archive()
    
    if not result:
        print("\n❌ 归档测试失败，无法继续验证")
        return
    
    print(f"\n📊 归档结果:")
    print(f"   成功: {result.get('success')}")
    print(f"   新闻数: {result.get('search_results', {}).get('count', 0)}")
    
    saved_files = result.get('saved_files', [])
    errors = result.get('errors', [])
    
    if saved_files:
        print(f"\n✅ 成功创建 {len(saved_files)} 个文件:")
        for f in saved_files:
            print(f"   - {f}")
        
        # 提取日期路径
        if saved_files:
            date_path = '/'.join(saved_files[0].split('/')[:-1])
            
            # 等待几秒让GitHub处理
            print(f"\n⏳ 等待3秒让GitHub处理...")
            time.sleep(3)
            
            # 步骤2: 验证GitHub文件
            verified = verify_github_files(date_path)
            
            if verified:
                print(f"\n" + "=" * 70)
                print("🎉 验证成功！")
                print("=" * 70)
                print(f"✅ 归档功能正常工作")
                print(f"✅ 文件已成功创建到GitHub仓库")
                print(f"\n📁 查看文件:")
                print(f"   https://github.com/{REPO}/tree/main/{date_path}")
            else:
                print(f"\n⚠️ 文件可能还在处理中，请稍后手动检查")
                print(f"   检查地址: https://github.com/{REPO}/tree/main/{date_path}")
    else:
        print(f"\n⚠️ 没有创建文件")
        if errors:
            print(f"\n❌ 错误信息:")
            for e in errors:
                error_msg = e if isinstance(e, str) else e.get('error', '')
                print(f"   - {error_msg}")
        
        print(f"\n💡 可能原因:")
        print(f"   - GITHUB_TOKEN未设置或权限不足")
        print(f"   - GitHub API调用失败")
        print(f"   - Token没有Contents: Read and write权限")

if __name__ == '__main__':
    main()

