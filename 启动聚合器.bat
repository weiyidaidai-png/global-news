@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title 全球新闻标题聚合器 - 启动器

echo ================================================
echo 全球新闻标题聚合器 - 启动器
echo ================================================
echo.
echo 当前目录: %~dp0
echo.

:: 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python环境
    echo 请先安装Python 3.6或更高版本
    echo.
    pause
    exit /b 1
)

:: 检查是否在正确的目录
if not exist "news_crawler.py" (
    echo 错误: 未找到新闻聚合器文件
    echo 请确保此批处理文件位于聚合器目录中
    echo.
    pause
    exit /b 1
)

:: 显示菜单
:menu
cls
echo ================================================
echo 全球新闻标题聚合器 - 启动器
echo ================================================
echo.
echo 请选择要执行的操作:
echo.
echo 1. 启动聚合器（推荐）
echo 2. 运行启动向导
echo 3. 立即抓取新闻
echo 4. 查看调度信息
echo 5. 启动后台自动更新
echo 6. 退出
echo.

set /p choice=请输入选项 [1-6]:

:: 处理用户选择
if "%choice%"=="1" (
    goto start_aggregator
) else if "%choice%"=="2" (
    goto run_wizard
) else if "%choice%"=="3" (
    goto run_crawl
) else if "%choice%"=="4" (
    goto show_schedule
) else if "%choice%"=="5" (
    goto start_scheduler
) else if "%choice%"=="6" (
    goto exit
) else (
    echo 错误: 无效的选项
    pause
    goto menu
)

:: 启动聚合器
:start_aggregator
cls
echo ================================================
echo 启动全球新闻标题聚合器...
echo ================================================
echo.

:: 检查是否存在index.html文件
if exist "index.html" (
    echo ✓ 找到已生成的界面文件
    echo.
    echo 正在打开界面...
    start "" "index.html"
    echo.
    echo 聚合器界面已打开！
    echo.
    echo 如果需要更新新闻，可以：
    echo 1. 点击界面上的刷新按钮
    echo 2. 运行"立即抓取新闻"功能
    echo 3. 启动后台自动更新服务
    echo.
) else (
    echo ⚠️  未找到界面文件
    echo.
    echo 请先运行启动向导或立即抓取新闻
    echo.
)

pause
goto menu

:: 运行启动向导
:run_wizard
cls
echo ================================================
echo 运行启动向导...
echo ================================================
echo.
echo 启动向导将帮助您：
echo - 检查Python环境
echo - 安装所需依赖
echo - 运行首次新闻抓取
echo - 生成界面文件
echo.
pause

echo.
echo 正在启动向导...
echo.

python start.py

goto menu

:: 立即抓取新闻
:run_crawl
cls
echo ================================================
echo 立即抓取新闻...
echo ================================================
echo.
echo 这将连接到各个新闻网站并抓取最新标题
echo 此过程可能需要几分钟时间...
echo.
pause

echo.
echo 正在抓取新闻...
echo.

python news_crawler.py

echo.
echo 新闻抓取完成！
echo.
echo 如果成功生成了界面文件，可以：
echo 1. 选择"启动聚合器"打开界面
echo 2. 直接双击index.html文件
echo.

pause
goto menu

:: 查看调度信息
:show_schedule
cls
echo ================================================
echo 查看调度信息...
echo ================================================
echo.

python scheduler.py --info

echo.
pause
goto menu

:: 启动后台自动更新
:start_scheduler
cls
echo ================================================
echo 启动后台自动更新...
echo ================================================
echo.
echo 此功能将启动后台服务：
echo - 每30分钟自动抓取一次新闻
echo - 自动更新界面文件
echo - 可以使用Ctrl+C停止服务
echo.
echo 注意：此窗口需要保持打开状态
echo.
pause

echo.
echo 正在启动后台自动更新服务...
echo.
echo 按 Ctrl+C 停止服务
echo.

python scheduler.py --start

goto menu

:: 退出
:exit
cls
echo ================================================
echo 感谢使用全球新闻标题聚合器！
echo ================================================
echo.
echo 祝您使用愉快！
echo.
pause
exit /b 0
