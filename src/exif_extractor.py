import exifread
import os
from datetime import datetime

def extract_date_from_exif(image_path):
    """
    从图像的EXIF数据中提取拍摄日期
    :param image_path: 图像文件路径
    :return: 拍摄日期字符串 (YYYY-MM-DD) 或 None（如果未找到）
    """
    try:
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f, details=False)

            # 查找日期相关的标签
            date_tags = [
                'EXIF DateTimeOriginal',
                'Image DateTime',
                'EXIF DateTimeDigitized'
            ]

            for tag in date_tags:
                if tag in tags:
                    date_str = str(tags[tag])
                    # 尝试解析日期格式
                    # EXIF日期格式通常是 "YYYY:MM:DD HH:MM:SS"
                    if ':' in date_str:
                        try:
                            # 将 "YYYY:MM:DD" 转换为 "YYYY-MM-DD"
                            date_part = date_str.split(' ')[0]
                            year, month, day = date_part.split(':')
                            return f"{year}-{month}-{day}"
                        except (ValueError, IndexError):
                            continue

            # 如果没有找到EXIF日期，返回None
            return None

    except Exception as e:
        print(f"警告: 读取 {image_path} 的EXIF数据时出错: {e}")
        return None

def get_file_modification_date(image_path):
    """
    获取文件的修改日期作为备选方案
    :param image_path: 图像文件路径
    :return: 修改日期字符串 (YYYY-MM-DD)
    """
    try:
        mtime = os.path.getmtime(image_path)
        return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
    except Exception as e:
        print(f"警告: 获取 {image_path} 的修改日期时出错: {e}")
        return None