#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理器 - 处理应用配置和模板管理
"""

import json
import os
from datetime import datetime

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = {
            "templates": {},
            "last_template": None,
            "window_geometry": None
        }
        self.load_config()

    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self.save_config()
        except Exception as e:
            print(f"加载配置文件时出错: {e}")

    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置文件时出错: {e}")

    def save_template(self, name, settings):
        """保存模板"""
        template = {
            "name": name,
            "settings": settings,
            "created": datetime.now().isoformat(),
            "last_used": datetime.now().isoformat()
        }

        self.config["templates"][name] = template
        self.config["last_template"] = name
        self.save_config()

    def load_template(self, name):
        """加载模板"""
        if name in self.config["templates"]:
            template = self.config["templates"][name]
            template["last_used"] = datetime.now().isoformat()
            self.config["last_template"] = name
            self.save_config()
            return template["settings"]
        return None

    def delete_template(self, name):
        """删除模板"""
        if name in self.config["templates"]:
            del self.config["templates"][name]
            if self.config["last_template"] == name:
                self.config["last_template"] = None
            self.save_config()

    def get_templates(self):
        """获取所有模板名称"""
        return list(self.config["templates"].keys())

    def get_template_info(self, name):
        """获取模板信息"""
        if name in self.config["templates"]:
            template = self.config["templates"][name]
            return {
                "name": template["name"],
                "created": template["created"],
                "last_used": template["last_used"]
            }
        return None

    def save_window_geometry(self, geometry):
        """保存窗口几何信息"""
        self.config["window_geometry"] = geometry
        self.save_config()

    def load_window_geometry(self):
        """加载窗口几何信息"""
        return self.config["window_geometry"]

    def get_last_template(self):
        """获取上次使用的模板"""
        return self.config["last_template"]