#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PhotoWaterMark 测试文件
"""

import unittest
import os
import sys
import tempfile
import shutil

# 将src目录添加到Python路径中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from command_line_parser import parse_arguments
from exif_extractor import extract_date_from_exif, get_file_modification_date
from image_processor import get_supported_images, create_output_directory, get_watermark_position

class TestPhotoWaterMark(unittest.TestCase):

    def setUp(self):
        """测试前的准备工作"""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """测试后的清理工作"""
        shutil.rmtree(self.test_dir)

    def test_get_supported_images(self):
        """测试获取支持的图像文件"""
        # 创建一些测试文件
        test_files = ["test1.jpg", "test2.png", "test3.gif", "test4.txt", "test5.jpeg"]
        for filename in test_files:
            with open(os.path.join(self.test_dir, filename), 'w') as f:
                f.write("test")

        # 获取支持的图像文件
        images = get_supported_images(self.test_dir)

        # 检查结果
        expected_images = ["test1.jpg", "test2.png", "test5.jpeg"]
        self.assertEqual(len(images), 3)
        for img in expected_images:
            self.assertIn(img, images)

    def test_get_watermark_position(self):
        """测试水印位置计算"""
        image_size = (800, 600)
        text_size = (100, 20)

        # 测试左上角位置
        pos = get_watermark_position(image_size, text_size, 'topLeft')
        self.assertEqual(pos, (10, 10))

        # 测试中心位置
        pos = get_watermark_position(image_size, text_size, 'center')
        self.assertEqual(pos, (350, 290))

        # 测试右下角位置
        pos = get_watermark_position(image_size, text_size, 'bottomRight')
        self.assertEqual(pos, (690, 570))

    def test_get_file_modification_date(self):
        """测试获取文件修改日期"""
        test_image = os.path.join(self.test_dir, "test.jpg")
        # 创建一个简单的测试文件
        with open(test_image, 'w') as f:
            f.write("This is a test image file")

        date_str = get_file_modification_date(test_image)
        # 检查返回的日期格式
        self.assertIsNotNone(date_str)
        self.assertRegex(date_str, r'^\d{4}-\d{2}-\d{2}$')

if __name__ == '__main__':
    unittest.main()