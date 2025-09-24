#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本 - 用于创建PhotoWaterMark的Windows可执行文件
"""

import os
import sys
import subprocess
import shutil

def build_executable():
    """构建Windows可执行文件"""
    print("开始构建PhotoWaterMark Windows可执行文件...")

    # 确保在正确的目录
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)

    # 检查必要文件
    required_files = [
        'src/photowatermark_gui.py',
        'src/watermark_handler.py',
        'src/config_manager.py',
        'requirements.txt'
    ]

    for file in required_files:
        if not os.path.exists(file):
            print(f"错误: 缺少必要文件 {file}")
            return False

    # 安装依赖
    print("检查并安装依赖...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    except subprocess.CalledProcessError:
        print("警告: 无法安装依赖，继续尝试打包...")

    # 使用PyInstaller打包
    print("使用PyInstaller打包...")
    try:
        # 使用spec文件进行打包
        if os.path.exists('photowatermark_gui.spec'):
            cmd = [sys.executable, '-m', 'PyInstaller', 'photowatermark_gui.spec']
        else:
            # 如果没有spec文件，则使用命令行参数
            cmd = [
                sys.executable, '-m', 'PyInstaller',
                '--onefile',
                '--windowed',
                '--name', 'PhotoWaterMark',
                '--icon', 'NONE',
                'src/photowatermark_gui.py'
            ]

        subprocess.check_call(cmd)
        print("打包完成!")

        # 检查生成的文件
        exe_path = os.path.join('dist', 'PhotoWaterMark.exe')
        if os.path.exists(exe_path):
            print(f"可执行文件已生成: {exe_path}")
        elif os.path.exists(os.path.join('dist', 'photowatermark_gui.exe')):
            print(f"可执行文件已生成: {os.path.join('dist', 'photowatermark_gui.exe')}")
        else:
            print("警告: 未找到生成的可执行文件")

        return True

    except subprocess.CalledProcessError as e:
        print(f"打包过程中出现错误: {e}")
        return False
    except FileNotFoundError:
        print("错误: 未找到PyInstaller，请先安装: pip install pyinstaller")
        return False

def create_portable_package():
    """创建便携式包"""
    print("创建便携式包...")

    # 创建发布目录
    release_dir = 'PhotoWaterMark_Release'
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    os.makedirs(release_dir)

    # 复制可执行文件
    exe_files = [
        os.path.join('dist', 'photowatermark_gui.exe'),
        os.path.join('dist', 'PhotoWaterMark.exe')
    ]

    exe_copied = False
    for exe_file in exe_files:
        if os.path.exists(exe_file):
            shutil.copy2(exe_file, os.path.join(release_dir, 'PhotoWaterMark.exe'))
            exe_copied = True
            break

    if not exe_copied:
        print("错误: 未找到可执行文件")
        return False

    # 创建使用说明
    readme_content = """PhotoWaterMark 桌面版
===================

一个基于Python的桌面应用程序，用于向图片添加自定义文本水印。

## 功能特性

- 图形用户界面: 直观易用的桌面应用程序
- 批量处理: 支持单张图片或批量导入图片
- 自定义水印: 可自定义水印文本、字体、颜色、透明度和旋转角度
- 位置设置: 提供九宫格预设位置和手动拖拽定位
- 实时预览: 所有设置更改都会实时显示在预览窗口中
- 导出选项: 支持JPEG和PNG格式导出，可自定义命名规则
- 模板管理: 可保存、加载和管理水印设置模板

## 系统要求

- Windows 7 或更高版本

## 安装和使用

1. 直接双击运行 PhotoWaterMark.exe 即可使用
2. 无需安装其他依赖，程序是完全独立的

## 使用说明

1. 点击"导入图片"按钮选择要添加水印的图片
2. 在右侧面板设置水印参数：
   - 水印文本：输入要添加的文本
   - 字体大小：调整字体大小
   - 字体颜色：选择水印颜色
   - 透明度：调整水印透明度
   - 旋转角度：调整水印旋转角度
3. 选择水印位置（九宫格预设位置或拖拽自定义位置）
4. 预览效果
5. 点击"导出图片"按钮保存处理后的图片

## 注意事项

- 程序会在同目录下生成配置文件config.json用于保存模板设置
- 如需重新开始，可删除config.json文件
"""

    with open(os.path.join(release_dir, 'README.txt'), 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print(f"便携式包已创建: {release_dir}")
    return True

def main():
    """主函数"""
    print("PhotoWaterMark 打包工具")
    print("=" * 30)

    # 构建可执行文件
    if build_executable():
        # 创建便携式包
        if create_portable_package():
            print("\n打包完成! 您可以在 PhotoWaterMark_Release 目录中找到可分发的文件。")
        else:
            print("\n便携式包创建失败。")
    else:
        print("\n打包失败。")

if __name__ == "__main__":
    main()