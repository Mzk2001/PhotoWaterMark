# PhotoWaterMark

一个Python命令行工具，用于根据图像EXIF元数据向图片添加拍摄日期水印。

## 功能特性
- 读取指定目录下的图像文件
- 从EXIF元数据中提取拍摄日期
- 添加包含拍摄日期的文本水印(格式为YYYY-MM-DD)
- 将添加水印的图像保存到新的子目录中
- 支持自定义字体大小、颜色和水印位置

## 技术栈
- Python 3.6+
- Pillow (用于图像处理)
- exifread (用于EXIF元数据提取)

## 项目结构
```
PhotoWaterMark/
├── src/
│   ├── photowatermark.py      (主程序)
│   ├── command_line_parser.py  (命令行参数解析)
│   ├── exif_extractor.py       (EXIF元数据提取)
│   ├── image_processor.py      (图像处理)
│   └── watermark_processor.py  (水印处理)
├── tests/
│   └── test_photowatermark.py (测试文件)
├── requirements.txt            (Python依赖包列表)
└── README.md
```

## 安装依赖
```bash
pip install -r requirements.txt
```

## 使用方法
```bash
python src/photowatermark.py [目录路径] [选项参数]

选项参数:
  --font-size <大小>     水印字体大小 (默认值: 24)
  --font-color <颜色>    水印字体颜色 (默认值: black)
  --position <位置>      水印位置: topLeft, center, bottomRight (默认值: bottomRight)
```

## 示例
```bash
# 基本用法
python src/photowatermark.py /path/to/images

# 自定义水印样式
python src/photowatermark.py /path/to/images --font-size 32 --font-color red --position center

# 指定水印位置为左上角
python src/photowatermark.py /path/to/images --position topLeft
```