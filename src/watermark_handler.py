#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
水印处理器 - 处理图片水印添加功能
"""

from PIL import Image, ImageDraw, ImageFont
import os

class WatermarkHandler:
    def __init__(self):
        pass

    def add_text_watermark(self, input_path, output_path, watermark_text, font_size=24,
                          font_color='black', transparency=100, rotation=0, position='bottomRight'):
        """
        向图像添加文本水印

        :param input_path: 输入图像路径
        :param output_path: 输出图像路径
        :param watermark_text: 水印文本
        :param font_size: 字体大小
        :param font_color: 字体颜色
        :param transparency: 透明度 (0-100)
        :param rotation: 旋转角度 (-180到180)
        :param position: 水印位置
        :return: 是否成功添加水印
        """
        try:
            # 打开图像
            with Image.open(input_path) as img:
                # 转换为RGBA模式以支持透明度
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')

                # 创建一个透明图层用于绘制水印
                txt_layer = Image.new('RGBA', img.size, (255, 255, 255, 0))
                draw = ImageDraw.Draw(txt_layer)

                # 尝试使用默认字体，如果失败则使用默认字体
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    try:
                        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
                    except:
                        font = ImageFont.load_default()

                # 获取文本尺寸
                bbox = draw.textbbox((0, 0), watermark_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                # 计算水印位置
                img_width, img_height = img.size
                margin = 10

                if position == 'topLeft':
                    x, y = margin, margin
                elif position == 'top':
                    x, y = (img_width - text_width) // 2, margin
                elif position == 'topRight':
                    x, y = img_width - text_width - margin, margin
                elif position == 'left':
                    x, y = margin, (img_height - text_height) // 2
                elif position == 'center':
                    x, y = (img_width - text_width) // 2, (img_height - text_height) // 2
                elif position == 'right':
                    x, y = img_width - text_width - margin, (img_height - text_height) // 2
                elif position == 'bottomLeft':
                    x, y = margin, img_height - text_height - margin
                elif position == 'bottom':
                    x, y = (img_width - text_width) // 2, img_height - text_height - margin
                elif position == 'bottomRight':
                    x, y = img_width - text_width - margin, img_height - text_height - margin
                else:
                    x, y = img_width - text_width - margin, img_height - text_height - margin

                # 调整透明度
                alpha = int(255 * transparency / 100)

                # 解析颜色
                if font_color.startswith('#'):
                    # HEX颜色
                    color = tuple(int(font_color[i:i+2], 16) for i in (1, 3, 5))
                elif font_color.lower() == 'black':
                    color = (0, 0, 0)
                elif font_color.lower() == 'white':
                    color = (255, 255, 255)
                elif font_color.lower() == 'red':
                    color = (255, 0, 0)
                elif font_color.lower() == 'green':
                    color = (0, 255, 0)
                elif font_color.lower() == 'blue':
                    color = (0, 0, 255)
                else:
                    color = (0, 0, 0)  # 默认黑色

                # 绘制水印
                draw.text((x, y), watermark_text, font=font, fill=(*color, alpha))

                # 如果有旋转，应用旋转
                if rotation != 0:
                    # 创建一个新的图层用于旋转
                    rotated_layer = Image.new('RGBA', img.size, (255, 255, 255, 0))
                    rotated_watermark = txt_layer.rotate(rotation, expand=0, center=(x + text_width//2, y + text_height//2))
                    rotated_layer.paste(rotated_watermark, (0, 0), rotated_watermark)
                    txt_layer = rotated_layer

                # 合并图像和水印图层
                watermarked = Image.alpha_composite(img, txt_layer)

                # 转换回RGB模式以保存为JPEG等格式
                watermarked = watermarked.convert('RGB')

                # 保存图像
                watermarked.save(output_path)

                return True

        except Exception as e:
            print(f"错误: 处理图像 {input_path} 时出错: {e}")
            return False

    def get_watermark_position(self, image_size, text_size, position):
        """
        计算水印位置
        :param image_size: 图像尺寸 (width, height)
        :param text_size: 文本尺寸 (width, height)
        :param position: 位置参数
        :return: 水印位置 (x, y)
        """
        img_width, img_height = image_size
        text_width, text_height = text_size

        margin = 10  # 边距

        if position == 'topLeft':
            return (margin, margin)
        elif position == 'top':
            return ((img_width - text_width) // 2, margin)
        elif position == 'topRight':
            return (img_width - text_width - margin, margin)
        elif position == 'left':
            return (margin, (img_height - text_height) // 2)
        elif position == 'center':
            return ((img_width - text_width) // 2, (img_height - text_height) // 2)
        elif position == 'right':
            return (img_width - text_width - margin, (img_height - text_height) // 2)
        elif position == 'bottomLeft':
            return (margin, img_height - text_height - margin)
        elif position == 'bottom':
            return ((img_width - text_width) // 2, img_height - text_height - margin)
        elif position == 'bottomRight':
            return (img_width - text_width - margin, img_height - text_height - margin)
        else:
            # 默认为右下角
            return (img_width - text_width - margin, img_height - text_height - margin)