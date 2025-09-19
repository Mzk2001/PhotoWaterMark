#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PhotoWaterMark - 根据图像EXIF元数据向图片添加文本水印
"""

import os
import sys

# 导入项目模块
from command_line_parser import parse_arguments
from exif_extractor import extract_date_from_exif, get_file_modification_date
from image_processor import get_supported_images, create_output_directory, process_image

def main():
    """
    主函数
    """
    # 解析命令行参数
    args = parse_arguments()

    # 获取输入目录中的图像文件
    images = get_supported_images(args.input_directory)

    if not images:
        print(f"警告: 在目录 '{args.input_directory}' 中未找到支持的图像文件")
        sys.exit(0)

    print(f"找到 {len(images)} 个图像文件")

    # 创建输出目录
    output_directory = create_output_directory(args.input_directory)
    print(f"创建输出目录: {output_directory}")

    # 处理每个图像文件
    processed_count = 0
    for image_name in images:
        input_path = os.path.join(args.input_directory, image_name)

        # 提取EXIF日期
        date_str = extract_date_from_exif(input_path)

        # 如果没有EXIF日期，使用文件修改日期
        if not date_str:
            date_str = get_file_modification_date(input_path)
            if date_str:
                print(f"警告: {image_name} 缺少EXIF日期信息，使用文件修改日期: {date_str}")
            else:
                print(f"错误: 无法获取 {image_name} 的日期信息")
                continue
        else:
            print(f"提取 {image_name} 的EXIF日期: {date_str}")

        # 生成输出路径
        output_path = os.path.join(output_directory, image_name)

        # 添加水印
        success = process_image(
            input_path,
            output_path,
            date_str,
            args.font_size,
            args.font_color,
            args.position
        )

        if success:
            processed_count += 1
            print(f"成功处理: {image_name}")
        else:
            print(f"处理失败: {image_name}")

    print(f"\n处理完成! 成功处理 {processed_count}/{len(images)} 个图像文件")
    print(f"输出目录: {output_directory}")

if __name__ == "__main__":
    main()