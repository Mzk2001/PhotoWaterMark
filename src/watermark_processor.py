from PIL import Image, ImageDraw, ImageFont
import os

def add_watermark_to_image(input_path, output_path, watermark_text, font_size=24, font_color='black', position='bottomRight'):
    """
    向图像添加水印
    :param input_path: 输入图像路径
    :param output_path: 输出图像路径
    :param watermark_text: 水印文本
    :param font_size: 字体大小
    :param font_color: 字体颜色
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
            elif position == 'center':
                x, y = (img_width - text_width) // 2, (img_height - text_height) // 2
            elif position == 'bottomRight':
                x, y = img_width - text_width - margin, img_height - text_height - margin
            else:
                x, y = img_width - text_width - margin, img_height - text_height - margin

            # 绘制水印
            draw.text((x, y), watermark_text, font=font, fill=font_color)

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