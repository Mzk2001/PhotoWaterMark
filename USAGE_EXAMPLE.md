# PhotoWaterMark 使用示例

## 基本用法

```bash
# 处理指定目录中的所有图像
python src/photowatermark.py example_images

# 输出:
# 找到 3 个图像文件
# 创建输出目录: example_images_watermark
# 警告: image1.jpg 缺少EXIF日期信息，使用文件修改日期: 2025-09-19
# 警告: image2.png 缺少EXIF日期信息，使用文件修改日期: 2025-09-19
# 警告: image3.jpeg 缺少EXIF日期信息，使用文件修改日期: 2025-09-19
# 成功处理: image1.jpg
# 成功处理: image2.png
# 成功处理: image3.jpeg
#
# 处理完成! 成功处理 3/3 个图像文件
# 输出目录: example_images_watermark
```

## 自定义水印样式

```bash
# 使用较大的字体和红色水印
python src/photowatermark.py example_images --font-size 32 --font-color red

# 将水印放置在图像中心
python src/photowatermark.py example_images --position center

# 将水印放置在左上角
python src/photowatermark.py example_images --position topLeft
```

## 支持的参数

- `input_directory`: 包含图像文件的目录路径（必需）
- `--font-size`: 水印字体大小（默认值: 24）
- `--font-color`: 水印字体颜色（默认值: black）
- `--position`: 水印位置，可选值:
  - `topLeft`: 左上角
  - `center`: 中心
  - `bottomRight`: 右下角（默认值）

## 输出结果

处理后的图像将保存在新创建的目录中，目录名为原始目录名加上 `_watermark` 后缀。例如，处理 `example_images` 目录中的图像将在 `example_images_watermark` 目录中生成带水印的图像。