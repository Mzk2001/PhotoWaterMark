import argparse
import sys
import os

def parse_arguments():
    """
    解析命令行参数
    :return: 解析后的参数对象
    """
    parser = argparse.ArgumentParser(
        description='PhotoWaterMark - 根据图像EXIF元数据向图片添加文本水印'
    )

    parser.add_argument(
        'input_directory',
        help='包含图像文件的目录路径'
    )

    parser.add_argument(
        '--font-size',
        type=int,
        default=24,
        help='水印字体大小 (默认值: 24)'
    )

    parser.add_argument(
        '--font-color',
        default='black',
        help='水印字体颜色 (默认值: black)'
    )

    parser.add_argument(
        '--position',
        choices=['topLeft', 'center', 'bottomRight'],
        default='bottomRight',
        help='水印位置: topLeft, center, bottomRight (默认值: bottomRight)'
    )

    args = parser.parse_args()

    # 验证输入目录是否存在
    if not os.path.exists(args.input_directory):
        print(f"错误: 目录 '{args.input_directory}' 不存在")
        sys.exit(1)

    if not os.path.isdir(args.input_directory):
        print(f"错误: '{args.input_directory}' 不是一个有效的目录")
        sys.exit(1)

    return args