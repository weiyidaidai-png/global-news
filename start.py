#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import logging
from datetime import datetime

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 6):
        print("错误：需要Python 3.6或更高版本")
        return False
    return True

def install_dependencies():
    """安装依赖"""
    print("正在安装Python依赖...")

    try:
        # 使用pip安装requirements.txt中的依赖
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("OK 依赖安装成功")
            return True
        else:
            print(f"ERR 依赖安装失败:\n{result.stderr}")
            return False

    except Exception as e:
        print(f"ERR 安装依赖时发生错误: {e}")
        return False

def run_initial_crawl():
    """运行首次抓取"""
    print("正在运行首次新闻抓取...")

    try:
        result = subprocess.run(
            [sys.executable, 'news_crawler.py'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("OK 首次新闻抓取完成")
            return True
        else:
            print(f"ERR 首次抓取失败:\n{result.stderr}")
            return False

    except Exception as e:
        print(f"ERR 首次抓取时发生错误: {e}")
        return False

def main():
    """主函数"""
    print("="*50)
    print("全球新闻标题聚合器 - 启动向导")
    print("="*50)
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python版本: {sys.version.split()[0]}")
    print()

    # 检查Python版本
    if not check_python_version():
        input("按回车键退出...")
        return

    # 检查是否已安装依赖
    print("检查已安装的依赖...")
    missing_deps = []

    try:
        import requests
    except ImportError:
        missing_deps.append("requests")

    try:
        from bs4 import BeautifulSoup
    except ImportError:
        missing_deps.append("beautifulsoup4")

    try:
        import schedule
    except ImportError:
        missing_deps.append("schedule")

    try:
        import jinja2
    except ImportError:
        missing_deps.append("jinja2")

    if missing_deps:
        print(f"发现缺失的依赖: {', '.join(missing_deps)}")
        if not install_dependencies():
            input("按回车键退出...")
            return
    else:
        print("OK 所有依赖都已安装")

    # 运行首次抓取
    print()
    if not run_initial_crawl():
        input("按回车键退出...")
        return

    # 检查是否生成了HTML文件
    if os.path.exists("index.html"):
        print()
        print("="*50)
        print("OK 全球新闻标题聚合器已成功启动！")
        print("="*50)
        print()
        print("使用说明:")
        print("1. 打开浏览器访问: file://" + os.path.abspath("index.html"))
        print("2. 或者直接双击打开当前目录下的 index.html 文件")
        print()
        print("自动更新功能:")
        print("- 新闻将每30分钟自动更新一次")
        print("- 页面会自动刷新以显示最新新闻")
        print("- 您也可以手动刷新页面")
        print()
        print("如需启动后台自动更新服务，请运行:")
        print(f"  {sys.executable} scheduler.py --start")
        print()
        print("如需查看调度信息，请运行:")
        print(f"  {sys.executable} scheduler.py --info")
        print()
    else:
        print("ERR 无法找到生成的index.html文件")
        print("请检查日志文件获取详细错误信息")

    print()
    input("按回车键退出...")

if __name__ == "__main__":
    main()
