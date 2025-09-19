import os
from PIL import Image, ImageDraw, ImageFont
import shutil

def get_supported_images(directory):
    """
    获取目录中支持的图像文件
    :param directory: 目录路径
    :return: 支持的图像文件列表
    """
    supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    images = []

    for filename in os.listdir(directory):
        _, ext = os.path.splitext(filename)
        if ext.lower() in supported_extensions:
            images.append(filename)

    return images

def create_output_directory(input_directory):
    """
    创建输出目录
    :param input_directory: 输入目录路径
    :return: 输出目录路径
    """
    dir_name = os.path.basename(os.path.normpath(input_directory))
    output_dir = f"{dir_name}_watermark"
    output_path = os.path.join(os.path.dirname(input_directory), output_dir)

    # 如果输出目录已存在，先删除它
    if os.path.exists(output_path):
        shutil.rmtree(output_path)

    # 创建新的输出目录
    os.makedirs(output_path)
    return output_path

def get_watermark_position(image_size, text_size, position):
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
    elif position == 'center':
        return ((img_width - text_width) // 2, (img_height - text_height) // 2)
    elif position == 'bottomRight':
        return (img_width - text_width - margin, img_height - text_height - margin)
    else:
        # 默认为右下角
        return (img_width - text_width - margin, img_height - text_height - margin)

def process_image(input_path, output_path, watermark_text, font_size=24, font_color='black', position='bottomRight'):
    """
    处理单个图像，添加水印
    :param input_path: 输入图像路径
    :param output_path: 输出图像路径
    :param watermark_text: 水印文本
    :param font_size: 字体大小
    :param font_color: 字体颜色
    :param position: 水印位置
    :return: 是否成功处理
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