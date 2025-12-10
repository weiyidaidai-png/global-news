#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import schedule
import logging
import subprocess
import sys
import os
from datetime import datetime

# 配置日志
logging.basicConfig(
    filename='logs/scheduler.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def run_news_crawler():
    """运行新闻爬虫"""
    logger.info("="*50)
    logger.info("开始执行新闻抓取任务")
    logger.info("="*50)

    try:
        # 获取Python解释器路径
        python_path = sys.executable

        # 运行爬虫脚本
        result = subprocess.run(
            [python_path, 'news_crawler.py'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )

        # 记录输出
        if result.stdout:
            logger.info(f"爬虫输出:\n{result.stdout}")
        if result.stderr:
            logger.error(f"爬虫错误:\n{result.stderr}")

        # 检查返回码
        if result.returncode == 0:
            logger.info("新闻抓取任务完成")
            return True
        else:
            logger.error(f"新闻抓取任务失败，返回码: {result.returncode}")
            return False

    except Exception as e:
        logger.error(f"执行新闻爬虫时发生错误: {e}")
        return False

def start_scheduler():
    """启动调度器"""
    logger.info("启动新闻聚合调度器")

    # 每30分钟运行一次
    schedule.every(30).minutes.do(run_news_crawler)

    # 立即运行一次
    logger.info("立即运行首次新闻抓取")
    run_news_crawler()

    logger.info("调度器已启动，每30分钟自动抓取新闻")
    logger.info(f"下次运行时间: {schedule.next_run()}")

    # 循环执行任务
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次

        except KeyboardInterrupt:
            logger.info("调度器已手动停止")
            break

        except Exception as e:
            logger.error(f"调度器运行错误: {e}")
            time.sleep(60)  # 出错后等待一分钟再继续

def show_schedule_info():
    """显示调度信息"""
    print("="*50)
    print("全球新闻标题聚合器 - 调度信息")
    print("="*50)
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if schedule.jobs:
        next_run = schedule.next_run()
        print(f"下次运行时间: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"任务间隔: 30分钟")
    else:
        print("暂无调度任务")

    print("\n新闻来源:")
    sources = [
        'BBC News', 'CNN', 'Reuters', 'Al Jazeera',
        'New York Times', 'The Guardian', 'Associated Press',
        '日经新闻', 'NHK', '人民网', '澎湃新闻'
    ]
    for i, source in enumerate(sources, 1):
        print(f"  {i}. {source}")

    print("\n功能特性:")
    print("  ✓ 自动定期抓取（每30分钟）")
    print("  ✓ 支持12个主要新闻来源")
    print("  ✓ 智能新闻分类")
    print("  ✓ 标题去重和过滤")
    print("  ✓ 本地HTML界面展示")
    print("  ✓ 响应式设计，支持移动端")
    print("  ✓ 搜索和来源过滤功能")
    print("  ✓ 自动页面刷新")

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='全球新闻标题聚合器调度器')
    parser.add_argument('--start', action='store_true', help='启动调度器')
    parser.add_argument('--info', action='store_true', help='显示调度信息')
    parser.add_argument('--run', action='store_true', help='立即运行一次抓取')

    args = parser.parse_args()

    if args.info:
        show_schedule_info()
    elif args.run:
        run_news_crawler()
    elif args.start:
        start_scheduler()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
