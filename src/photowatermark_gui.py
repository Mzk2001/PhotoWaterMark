#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PhotoWaterMark - 桌面版图片水印工具
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import sys

# 导入拖拽支持
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_SUPPORTED = True
except ImportError:
    DND_SUPPORTED = False
    print("tkinterdnd2未安装，拖拽功能不可用")

# 导入水印处理器和配置管理器
from watermark_handler import WatermarkHandler
from config_manager import ConfigManager

class PhotoWaterMarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PhotoWaterMark - 图片水印工具")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)

        # 如果支持拖拽，注册拖拽事件
        if DND_SUPPORTED:
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.on_drop_files)

        # 存储导入的图片路径
        self.image_paths = []
        self.current_image_index = -1

        # 水印设置
        self.watermark_text = tk.StringVar(value="水印文本")
        self.font_size = tk.IntVar(value=24)
        self.font_color = tk.StringVar(value="black")
        self.transparency = tk.IntVar(value=100)
        self.rotation = tk.IntVar(value=0)
        self.selected_position = tk.StringVar(value="bottomRight")  # 默认位置为右下角

        # 位置模式管理（简单明确的方式）
        self.position_mode = "grid"  # "grid" 或 "manual"
        self.grid_position = "bottomRight"  # 九宫格位置
        self.manual_x = 0  # 手动X位置
        self.manual_y = 0  # 手动Y位置

        # 导出设置
        self.output_directory = tk.StringVar()
        self.output_format = tk.StringVar(value="JPEG")
        self.naming_rule = tk.StringVar(value="")  # 命名规则选择：""=保留原名, "prefix"=添加前缀, "suffix"=添加后缀
        self.naming_prefix = tk.StringVar()  # 前缀文本
        self.naming_suffix = tk.StringVar(value="_watermarked")  # 后缀文本
        self.allow_overwrite = tk.BooleanVar(value=False)

        # 当前模板
        self.current_template = tk.StringVar(value="默认模板")

        # 水印处理器
        self.watermark_handler = WatermarkHandler()

        # 配置管理器
        self.config_manager = ConfigManager()

        # 加载上次使用的模板
        self.load_last_template()

        self.create_widgets()
        self.setup_layout()

    def create_widgets(self):
        """创建所有UI组件"""
        self.create_menu()
        self.create_toolbar()
        self.create_main_panels()
        self.create_status_bar()

    def create_menu(self):
        """创建菜单栏"""
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # 文件菜单
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导入图片", command=self.import_images, accelerator="Ctrl+O")
        file_menu.add_command(label="导入文件夹", command=self.import_folder, accelerator="Ctrl+Shift+O")
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit, accelerator="Ctrl+Q")

        # 模板菜单
        template_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="模板", menu=template_menu)
        template_menu.add_command(label="保存模板", command=self.save_template, accelerator="Ctrl+S")
        template_menu.add_command(label="加载模板", command=self.load_template)
        template_menu.add_command(label="管理模板", command=self.manage_templates)

        # 帮助菜单
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)

    def create_toolbar(self):
        """创建工具栏"""
        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # 工具栏按钮
        ttk.Button(self.toolbar, text="导入图片", command=self.import_images).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="导入文件夹", command=self.import_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="导出图片", command=self.export_images).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="保存模板", command=self.save_template).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="加载模板", command=self.load_template).pack(side=tk.LEFT, padx=2)

    def create_main_panels(self):
        """创建主面板"""
        # 创建主容器
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 左侧面板 - 图片列表
        self.create_left_panel(main_container)

        # 中间面板 - 预览区
        self.create_middle_panel(main_container)

        # 右侧面板 - 设置区
        self.create_right_panel(main_container)

        # 添加面板到主容器
        main_container.add(self.left_panel, weight=1)
        main_container.add(self.middle_panel, weight=3)
        main_container.add(self.right_panel, weight=1)

    def create_left_panel(self, parent):
        """创建左侧面板"""
        self.left_panel = ttk.Frame(parent)

        # 标题
        ttk.Label(self.left_panel, text="导入的图片", font=("微软雅黑", 12, "bold")).pack(pady=5)

        # 图片列表框架
        list_frame = ttk.Frame(self.left_panel)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 创建Treeview和滚动条用于显示带缩略图的图片列表
        self.image_tree = ttk.Treeview(list_frame, columns=("name",), show="tree")
        self.image_tree.column("#0", width=50, stretch=tk.NO)  # 第一列用于显示缩略图
        self.image_tree.column("name", width=150, stretch=tk.YES)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.image_tree.yview)
        self.image_tree.configure(yscrollcommand=scrollbar.set)

        self.image_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定Treeview选择事件
        self.image_tree.bind('<<TreeviewSelect>>', self.on_image_select_tree)

        # 添加拖拽文件处理方法
        # 注意：由于tkinter本身不支持文件拖拽，这里提供一个备用方案
        # 可以通过安装tkinterdnd2库来启用真正的拖拽功能

        # 操作按钮
        button_frame = ttk.Frame(self.left_panel)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(button_frame, text="导入单个文件", command=self.import_single_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="移除选中", command=self.remove_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="清空所有", command=self.clear_all).pack(side=tk.LEFT, padx=2)

    def on_image_select(self, event):
        """图片列表选择事件处理"""
        selection = self.image_listbox.curselection()
        if selection:
            index = selection[0]
            self.show_image(index)

    def on_image_select_tree(self, event):
        """Treeview图片选择事件处理"""
        selection = self.image_tree.selection()
        if selection:
            # 获取选中项的索引
            item_id = selection[0]
            children = self.image_tree.get_children()
            index = children.index(item_id) if item_id in children else -1
            if index >= 0:
                self.show_image(index)

    def create_middle_panel(self, parent):
        """创建中间面板"""
        self.middle_panel = ttk.Frame(parent)

        # 标题
        ttk.Label(self.middle_panel, text="图片预览", font=("微软雅黑", 12, "bold")).pack(pady=5)

        # 预览画布
        self.preview_canvas = tk.Canvas(self.middle_panel, bg="lightgray")
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 添加鼠标事件处理
        self.preview_canvas.bind("<Button-1>", self.on_canvas_click)
        self.preview_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.preview_canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

        # 控制按钮
        control_frame = ttk.Frame(self.middle_panel)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(control_frame, text="放大", command=self.zoom_in).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="缩小", command=self.zoom_out).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="适应窗口", command=self.fit_window).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="实际大小", command=self.actual_size).pack(side=tk.LEFT, padx=2)

    def create_right_panel(self, parent):
        """创建右侧面板"""
        self.right_panel = ttk.Notebook(parent)

        # 水印设置标签页
        self.watermark_frame = ttk.Frame(self.right_panel)
        self.right_panel.add(self.watermark_frame, text="水印设置")
        self.create_watermark_settings()

        # 位置设置标签页
        self.position_frame = ttk.Frame(self.right_panel)
        self.right_panel.add(self.position_frame, text="位置设置")
        self.create_position_settings()

        # 导出设置标签页
        self.export_frame = ttk.Frame(self.right_panel)
        self.right_panel.add(self.export_frame, text="导出设置")
        self.create_export_settings()

        # 模板管理标签页
        self.template_frame = ttk.Frame(self.right_panel)
        self.right_panel.add(self.template_frame, text="模板管理")
        self.create_template_settings()

    def create_watermark_settings(self):
        """创建水印设置界面"""
        # 水印文本
        ttk.Label(self.watermark_frame, text="水印文本:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        watermark_entry = ttk.Entry(self.watermark_frame, textvariable=self.watermark_text, width=20)
        watermark_entry.grid(row=0, column=1, padx=5, pady=5)
        watermark_entry.bind('<KeyRelease>', self.on_watermark_setting_change)

        # 字体大小
        ttk.Label(self.watermark_frame, text="字体大小:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        font_size_scale = ttk.Scale(self.watermark_frame, from_=8, to=72, variable=self.font_size, orient=tk.HORIZONTAL)
        font_size_scale.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        font_size_scale.bind('<ButtonRelease-1>', self.on_watermark_setting_change)
        font_size_scale.bind('<Motion>', self.on_watermark_setting_change)
        ttk.Label(self.watermark_frame, textvariable=self.font_size).grid(row=1, column=2, padx=5, pady=5)

        # 字体颜色
        ttk.Label(self.watermark_frame, text="字体颜色:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        color_frame = ttk.Frame(self.watermark_frame)
        color_frame.grid(row=2, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        color_entry = ttk.Entry(color_frame, textvariable=self.font_color, width=10)
        color_entry.pack(side=tk.LEFT)
        color_entry.bind('<KeyRelease>', self.on_watermark_setting_change)
        color_button = ttk.Button(color_frame, text="选择", command=self.choose_color)
        color_button.pack(side=tk.LEFT, padx=5)
        color_button.bind('<ButtonRelease-1>', self.on_watermark_setting_change)

        # 透明度
        ttk.Label(self.watermark_frame, text="透明度:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        transparency_scale = ttk.Scale(self.watermark_frame, from_=0, to=100, variable=self.transparency, orient=tk.HORIZONTAL)
        transparency_scale.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        transparency_scale.bind('<ButtonRelease-1>', self.on_watermark_setting_change)
        transparency_scale.bind('<Motion>', self.on_watermark_setting_change)
        ttk.Label(self.watermark_frame, textvariable=self.transparency).grid(row=3, column=2, padx=5, pady=5)

        # 旋转角度
        ttk.Label(self.watermark_frame, text="旋转角度:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        rotation_scale = ttk.Scale(self.watermark_frame, from_=-180, to=180, variable=self.rotation, orient=tk.HORIZONTAL)
        rotation_scale.grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        rotation_scale.bind('<ButtonRelease-1>', self.on_watermark_setting_change)
        rotation_scale.bind('<Motion>', self.on_watermark_setting_change)
        ttk.Label(self.watermark_frame, textvariable=self.rotation).grid(row=4, column=2, padx=5, pady=5)

    def create_position_settings(self):
        """创建位置设置界面"""
        # 九宫格位置按钮
        positions = [
            ("↖", "topLeft"), ("↑", "top"), ("↗", "topRight"),
            ("←", "left"), ("●", "center"), ("→", "right"),
            ("↙", "bottomLeft"), ("↓", "bottom"), ("↘", "bottomRight")
        ]

        # 当前选中的位置（已在第35行定义）
        pass

        # 清除之前的位置按钮
        for widget in self.position_frame.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.destroy()

        # 创建位置按钮并保存引用
        self.position_buttons = {}
        for i, (text, pos) in enumerate(positions):
            row, col = divmod(i, 3)
            # 修复lambda闭包问题，使用默认参数确保捕获正确的pos值
            btn = ttk.Button(self.position_frame, text=text, width=5,
                           command=lambda pos=pos: self.set_watermark_position(pos))
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.position_buttons[pos] = btn
            print(f"创建九宫格按钮: {text} ({pos})")

        # 更新选中按钮的样式
        self.update_position_button_styles()

    def set_watermark_position(self, position):
        """设置水印位置"""
        print(f"=== 按钮点击事件触发! ===")
        old_mode = self.position_mode
        old_grid_pos = self.grid_position
        self.selected_position.set(position)
        self.grid_position = position

        # 切换到九宫格模式
        self.position_mode = "grid"

        print(f"九宫格位置设置: {old_grid_pos} -> {position}, 模式: {old_mode} -> {self.position_mode}")
        self.status_label.config(text=f"水印位置设置为: {position}")
        self.on_watermark_setting_change(None)

        # 更新按钮样式
        self.update_position_button_styles()

    def update_position_button_styles(self):
        """更新位置按钮的样式以显示选中状态"""
        # 检查位置按钮是否已创建
        if not hasattr(self, 'position_buttons'):
            return

        selected_pos = self.selected_position.get()
        for pos, btn in self.position_buttons.items():
            if pos == selected_pos:
                btn.configure(style='Selected.TButton')
            else:
                btn.configure(style='TButton')  # 恢复默认样式

    def create_export_settings(self):
        """创建导出设置界面"""
        # 输出文件夹
        ttk.Label(self.export_frame, text="输出文件夹:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        folder_frame = ttk.Frame(self.export_frame)
        folder_frame.grid(row=0, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        ttk.Entry(folder_frame, textvariable=self.output_directory, width=15).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(folder_frame, text="浏览", command=self.browse_output_directory).pack(side=tk.LEFT, padx=5)

        # 输出格式
        ttk.Label(self.export_frame, text="输出格式:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        format_frame = ttk.Frame(self.export_frame)
        format_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(format_frame, text="JPEG", variable=self.output_format, value="JPEG").pack(side=tk.LEFT)
        ttk.Radiobutton(format_frame, text="PNG", variable=self.output_format, value="PNG").pack(side=tk.LEFT, padx=(10, 0))

        # 命名规则
        ttk.Label(self.export_frame, text="命名规则:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(self.export_frame, text="保留原文件名", variable=self.naming_rule, value="").grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Radiobutton(self.export_frame, text="添加前缀", variable=self.naming_rule, value="prefix").grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(self.export_frame, textvariable=self.naming_prefix, width=15).grid(row=3, column=2, padx=5, pady=2)
        ttk.Radiobutton(self.export_frame, text="添加后缀", variable=self.naming_rule, value="suffix").grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(self.export_frame, textvariable=self.naming_suffix, width=15).grid(row=4, column=2, padx=5, pady=2)

        # 覆盖原文件夹警告
        ttk.Checkbutton(self.export_frame, text="允许导出到原文件夹", variable=self.allow_overwrite).grid(row=5, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)

    def create_template_settings(self):
        """创建模板设置界面"""
        # 当前模板
        ttk.Label(self.template_frame, text="当前模板:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(self.template_frame, textvariable=self.current_template).grid(row=0, column=1, padx=5, pady=5)

        # 模板操作按钮
        button_frame = ttk.Frame(self.template_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="保存当前设置为模板", command=self.save_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="加载模板", command=self.load_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="管理模板", command=self.manage_templates).pack(side=tk.LEFT, padx=5)

    def choose_color(self):
        """选择颜色"""
        color = colorchooser.askcolor(title="选择水印颜色")
        if color[1]:
            self.font_color.set(color[1])
            self.on_watermark_setting_change(None)

    def browse_output_directory(self):
        """浏览输出目录"""
        directory = filedialog.askdirectory(title="选择输出文件夹")
        if directory:
            self.output_directory.set(directory)

    def on_watermark_setting_change(self, event):
        """水印设置改变时的事件处理"""
        # 如果有选中的图片，重新显示带水印的预览
        if self.current_image_index >= 0:
            self.show_image(self.current_image_index)

    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = ttk.Label(self.status_bar, text="就绪")
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.status_bar, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(side=tk.RIGHT, padx=5, pady=2, fill=tk.X, expand=True)

    def import_images(self):
        """导入图片"""
        file_paths = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
                ("JPEG文件", "*.jpg *.jpeg"),
                ("PNG文件", "*.png"),
                ("BMP文件", "*.bmp"),
                ("TIFF文件", "*.tiff *.tif"),
                ("所有文件", "*.*")
            ]
        )

        if file_paths:
            self.add_images(file_paths)

    def import_single_file(self):
        """导入单个文件"""
        file_path = filedialog.askopenfilename(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
                ("JPEG文件", "*.jpg *.jpeg"),
                ("PNG文件", "*.png"),
                ("BMP文件", "*.bmp"),
                ("TIFF文件", "*.tiff *.tif"),
                ("所有文件", "*.*")
            ]
        )

        if file_path:
            self.add_images([file_path])

    def import_folder(self):
        """导入文件夹"""
        folder_path = filedialog.askdirectory(title="选择包含图片的文件夹")

        if folder_path:
            # 获取文件夹中所有支持的图片文件
            supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
            image_files = []

            for filename in os.listdir(folder_path):
                _, ext = os.path.splitext(filename)
                if ext.lower() in supported_extensions:
                    image_files.append(os.path.join(folder_path, filename))

            if image_files:
                self.add_images(image_files)
            else:
                messagebox.showinfo("提示", "所选文件夹中没有找到支持的图片文件")

    def add_images(self, file_paths):
        """添加图片到列表"""
        for path in file_paths:
            if path not in self.image_paths:
                self.image_paths.append(path)
                filename = os.path.basename(path)

                # 生成缩略图
                item_id = None
                try:
                    image = Image.open(path)
                    # 调整图片大小以创建缩略图
                    image.thumbnail((40, 40), Image.LANCZOS)
                    # 转换为PhotoImage
                    photo = ImageTk.PhotoImage(image)

                    # 在Treeview中添加条目
                    item_id = self.image_tree.insert("", tk.END, text="", values=(filename,))

                    # 配置Treeview项以显示图像
                    self.image_tree.item(item_id, image=photo)

                    # 存储缩略图引用以防止被垃圾回收
                    if not hasattr(self, 'thumbnails'):
                        self.thumbnails = {}
                    self.thumbnails[item_id] = photo

                except Exception as e:
                    print(f"无法生成缩略图: {e}")
                    # 如果无法生成缩略图，仍然添加文件名
                    item_id = self.image_tree.insert("", tk.END, text="", values=(filename,))

        self.status_label.config(text=f"已导入 {len(self.image_paths)} 张图片")

        # 如果这是第一张图片，自动选择并显示
        if len(self.image_paths) == 1:
            first_item = self.image_tree.get_children()[0] if self.image_tree.get_children() else None
            if first_item:
                self.image_tree.selection_set(first_item)
                self.show_image(0)

    def show_image(self, index):
        """显示指定索引的图片"""
        if 0 <= index < len(self.image_paths):
            try:
                # 打开图片并调整大小以适应预览区域
                image = Image.open(self.image_paths[index])

                # 获取画布大小
                canvas_width = self.preview_canvas.winfo_width()
                canvas_height = self.preview_canvas.winfo_height()

                # 如果画布大小为0（窗口刚创建），使用默认大小
                if canvas_width <= 1 or canvas_height <= 1:
                    canvas_width, canvas_height = 600, 400

                # 计算缩放比例
                scale_w = canvas_width / image.width
                scale_h = canvas_height / image.height
                scale = min(scale_w, scale_h, 1.0)  # 不放大图片

                # 调整图片大小
                new_width = int(image.width * scale)
                new_height = int(image.height * scale)

                # 添加水印到图片
                watermarked_image = self.add_watermark_to_preview(image)

                # 调整带水印的图片大小
                watermarked_image = watermarked_image.resize((new_width, new_height), Image.LANCZOS)

                # 转换为PhotoImage
                photo = ImageTk.PhotoImage(watermarked_image)

                # 清除画布
                self.preview_canvas.delete("all")

                # 在画布中心显示图片
                x = (canvas_width - new_width) // 2
                y = (canvas_height - new_height) // 2
                self.preview_canvas.create_image(x, y, anchor=tk.NW, image=photo)

                # 保存对photo的引用，防止被垃圾回收
                self.preview_canvas.image = photo

                # 更新当前选中索引
                self.current_image_index = index

            except Exception as e:
                messagebox.showerror("错误", f"无法加载图片: {str(e)}")

    def add_watermark_to_preview(self, image):
        """为预览图添加水印"""
        try:
            # 转换为RGBA模式以支持透明度
            if image.mode != 'RGBA':
                image = image.convert('RGBA')

            # 创建一个透明图层用于绘制水印
            txt_layer = Image.new('RGBA', image.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(txt_layer)

            # 获取水印文本
            watermark_text = self.watermark_text.get()

            # 尝试使用支持中文的字体
            font_names = [
                "simhei.ttf",      # 黑体
                "simsun.ttc",      # 宋体
                "msyh.ttc",        # 微软雅黑
                "simkai.ttf",      # 楷体
                "fangsong.ttf",    # 仿宋
                "arial.ttf",
                "DejaVuSans.ttf"
            ]

            font = None
            for font_name in font_names:
                try:
                    font = ImageFont.truetype(font_name, self.font_size.get())
                    print(f"成功加载字体: {font_name}")
                    break
                except Exception as e:
                    print(f"无法加载字体 {font_name}: {e}")
                    continue

            # 如果所有字体都失败，使用默认字体
            if font is None:
                print("使用默认字体")
                font = ImageFont.load_default()
                # 如果默认字体也不支持中文，尝试使用系统字体
                try:
                    # Windows系统字体
                    font = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", self.font_size.get())
                    print("成功加载Windows系统黑体字体")
                except:
                    try:
                        # macOS系统字体
                        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", self.font_size.get())
                        print("成功加载macOS系统字体")
                    except:
                        try:
                            # Linux系统字体
                            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", self.font_size.get())
                            print("成功加载Linux系统字体")
                        except:
                            print("无法加载任何系统字体，使用PIL默认字体")

            # 获取文本尺寸
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # 计算水印位置
            img_width, img_height = image.size
            margin = 10

            # 根据模式选择位置
            if self.position_mode == "manual":
                # 使用手动位置
                x = self.manual_x
                y = self.manual_y
                # 确保位置在图像范围内
                x = max(0, min(x, img_width - text_width))
                y = max(0, min(y, img_height - text_height))
                print(f"使用手动位置: ({x}, {y}), 原始: ({self.manual_x}, {self.manual_y})")
            else:
                # 使用九宫格位置
                position = self.grid_position
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
                print(f"使用九宫格位置: {position} -> ({x}, {y})")

            # 调整透明度
            alpha = int(255 * self.transparency.get() / 100)

            # 解析颜色
            font_color = self.font_color.get()
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

            # 如果有旋转，应用旋转（仅在预览中简单实现）
            rotation = self.rotation.get()
            if rotation != 0:
                # 对于预览，我们简化旋转实现
                # 创建一个新的图层用于旋转
                rotated_layer = Image.new('RGBA', image.size, (255, 255, 255, 0))
                rotated_watermark = txt_layer.rotate(rotation, expand=1)
                rotated_layer.paste(rotated_watermark, (0, 0), rotated_watermark)
                txt_layer = rotated_layer

            # 合并图像和水印图层
            watermarked = Image.alpha_composite(image, txt_layer)

            return watermarked

        except Exception as e:
            print(f"添加水印时出错: {e}")
            return image

    def remove_selected(self):
        """移除选中的图片"""
        selection = self.image_tree.selection()
        if selection:
            # 获取选中项的索引
            children = self.image_tree.get_children()
            indices = [children.index(item) for item in selection if item in children]
            indices.sort(reverse=True)  # 从后往前删除，避免索引变化

            for index in indices:
                # 删除Treeview中的项
                item_id = children[index]
                self.image_tree.delete(item_id)
                # 删除对应的图片路径
                del self.image_paths[index]
                # 删除缩略图引用
                if hasattr(self, 'thumbnails') and item_id in self.thumbnails:
                    del self.thumbnails[item_id]

            self.status_label.config(text=f"已移除选中的图片，剩余 {len(self.image_paths)} 张")

    def clear_all(self):
        """清空所有图片"""
        if self.image_paths:
            if messagebox.askyesno("确认", "确定要清空所有图片吗？"):
                self.image_paths.clear()
                # 清空Treeview
                for item in self.image_tree.get_children():
                    self.image_tree.delete(item)
                # 清空缩略图引用
                if hasattr(self, 'thumbnails'):
                    self.thumbnails.clear()
                self.status_label.config(text="已清空所有图片")

    def zoom_in(self):
        """放大"""
        self.status_label.config(text="放大预览")

    def zoom_out(self):
        """缩小"""
        self.status_label.config(text="缩小预览")

    def fit_window(self):
        """适应窗口"""
        self.status_label.config(text="适应窗口大小")

    def actual_size(self):
        """实际大小"""
        self.status_label.config(text="显示实际大小")

    def on_drop_files(self, event):
        """处理拖拽文件事件"""
        if DND_SUPPORTED:
            # 获取拖拽的文件路径
            files = event.data.split()
            if files:
                # 过滤出图片文件
                image_files = []
                supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}

                for file_path in files:
                    # 移除可能的花括号
                    if file_path.startswith('{') and file_path.endswith('}'):
                        file_path = file_path[1:-1]

                    # 检查文件扩展名
                    _, ext = os.path.splitext(file_path)
                    if ext.lower() in supported_extensions:
                        image_files.append(file_path)

                if image_files:
                    self.add_images(image_files)
                    self.status_label.config(text=f"通过拖拽导入了 {len(image_files)} 张图片")
                else:
                    self.status_label.config(text="拖拽的文件中没有支持的图片格式")

    def on_canvas_click(self, event):
        """画布点击事件处理"""
        print(f"画布点击事件: x={event.x}, y={event.y}")
        # 记录点击位置
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_canvas_drag(self, event):
        """画布拖拽事件处理"""
        # 计算拖拽偏移量
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y

        # 更新拖拽起始位置
        self.drag_start_x = event.x
        self.drag_start_y = event.y

        # 更新手动位置
        self.manual_x += dx
        self.manual_y += dy

        # 切换到手动模式
        old_mode = self.position_mode
        self.position_mode = "manual"
        print(f"拖拽: ({dx}, {dy}) -> 手动位置 ({self.manual_x}, {self.manual_y}), 模式: {old_mode} -> {self.position_mode}")

        # 更新预览
        self.on_watermark_setting_change(None)

    def on_canvas_release(self, event):
        """画布释放事件处理"""
        pass

    def save_template(self):
        """保存当前设置为模板"""
        # 获取模板名称
        template_name = self.current_template.get()
        if not template_name or template_name == "默认模板":
            # 如果没有设置模板名称，提示用户输入
            from tkinter import simpledialog
            template_name = simpledialog.askstring("保存模板", "请输入模板名称:")
            if not template_name:
                return

        # 收集当前设置
        settings = {
            "watermark_text": self.watermark_text.get(),
            "font_size": self.font_size.get(),
            "font_color": self.font_color.get(),
            "transparency": self.transparency.get(),
            "rotation": self.rotation.get(),
            "position": self.selected_position.get()
        }

        # 保存模板
        self.config_manager.save_template(template_name, settings)
        self.current_template.set(template_name)
        self.status_label.config(text=f"模板 '{template_name}' 已保存")

    def load_template(self):
        """加载模板"""
        # 获取所有模板名称
        templates = self.config_manager.get_templates()
        if not templates:
            messagebox.showinfo("提示", "没有可用的模板")
            return

        # 创建选择对话框
        from tkinter import simpledialog
        template_name = simpledialog.askstring("加载模板", "请选择模板名称:", initialvalue=templates[0] if templates else "")
        if not template_name or template_name not in templates:
            return

        # 加载模板
        settings = self.config_manager.load_template(template_name)
        if settings:
            self.apply_template_settings(settings)
            self.current_template.set(template_name)
            self.status_label.config(text=f"模板 '{template_name}' 已加载")

    def manage_templates(self):
        """管理模板"""
        # 创建模板管理窗口
        template_window = tk.Toplevel(self.root)
        template_window.title("模板管理")
        template_window.geometry("400x300")

        # 模板列表
        list_frame = ttk.Frame(template_window)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        template_listbox = tk.Listbox(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=template_listbox.yview)
        template_listbox.configure(yscrollcommand=scrollbar.set)

        template_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 添加模板到列表
        templates = self.config_manager.get_templates()
        for template in templates:
            template_listbox.insert(tk.END, template)

        # 按钮框架
        button_frame = ttk.Frame(template_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        def load_selected_template():
            selection = template_listbox.curselection()
            if selection:
                template_name = template_listbox.get(selection[0])
                settings = self.config_manager.load_template(template_name)
                if settings:
                    self.apply_template_settings(settings)
                    self.current_template.set(template_name)
                    self.status_label.config(text=f"模板 '{template_name}' 已加载")
                    template_window.destroy()

        def delete_selected_template():
            selection = template_listbox.curselection()
            if selection:
                template_name = template_listbox.get(selection[0])
                if messagebox.askyesno("确认", f"确定要删除模板 '{template_name}' 吗?"):
                    self.config_manager.delete_template(template_name)
                    template_listbox.delete(selection[0])
                    self.status_label.config(text=f"模板 '{template_name}' 已删除")

        def rename_template():
            selection = template_listbox.curselection()
            if selection:
                old_name = template_listbox.get(selection[0])
                from tkinter import simpledialog
                new_name = simpledialog.askstring("重命名模板", "请输入新名称:", initialvalue=old_name)
                if new_name and new_name != old_name:
                    # 加载旧模板设置
                    settings = self.config_manager.load_template(old_name)
                    if settings:
                        # 保存为新名称
                        self.config_manager.save_template(new_name, settings)
                        # 删除旧模板
                        self.config_manager.delete_template(old_name)
                        # 更新列表
                        template_listbox.delete(selection[0])
                        template_listbox.insert(selection[0], new_name)
                        self.status_label.config(text=f"模板 '{old_name}' 已重命名为 '{new_name}'")

        # 操作按钮
        ttk.Button(button_frame, text="加载选中模板", command=load_selected_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除选中模板", command=delete_selected_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="重命名模板", command=rename_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", command=template_window.destroy).pack(side=tk.RIGHT, padx=5)

    def apply_template_settings(self, settings):
        """应用模板设置"""
        # 应用水印设置
        if "watermark_text" in settings:
            self.watermark_text.set(settings["watermark_text"])
        if "font_size" in settings:
            self.font_size.set(settings["font_size"])
        if "font_color" in settings:
            self.font_color.set(settings["font_color"])
        if "transparency" in settings:
            self.transparency.set(settings["transparency"])
        if "rotation" in settings:
            self.rotation.set(settings["rotation"])
        if "position" in settings:
            self.selected_position.set(settings["position"])
            # 同时更新grid_position以确保位置正确应用
            self.grid_position = settings["position"]
            # 确保位置模式为网格模式
            self.position_mode = "grid"

        # 更新按钮样式（确保按钮已创建）
        if hasattr(self, 'position_buttons') and self.position_buttons:
            self.update_position_button_styles()

        # 更新预览
        self.on_watermark_setting_change(None)

    def load_last_template(self):
        """加载上次使用的模板"""
        last_template = self.config_manager.get_last_template()
        if last_template:
            settings = self.config_manager.load_template(last_template)
            if settings:
                # 应用模板设置
                self.apply_template_settings(settings)
                self.current_template.set(last_template)

    def export_images(self):
        """导出图片"""
        if not self.image_paths:
            messagebox.showwarning("警告", "请先导入图片")
            return

        if not self.output_directory.get():
            output_dir = filedialog.askdirectory(title="选择输出文件夹")
            if not output_dir:
                return
            self.output_directory.set(output_dir)

        # 检查是否允许导出到原文件夹
        if not self.allow_overwrite.get():
            # 检查输出目录是否与任何输入图片的目录相同
            input_dirs = set(os.path.dirname(path) for path in self.image_paths)
            if self.output_directory.get() in input_dirs:
                messagebox.showwarning("警告", "为防止覆盖原图，默认禁止导出到原文件夹。\n请更改输出文件夹或启用'允许导出到原文件夹'选项。")
                return

        # 开始导出过程
        self.status_label.config(text="开始导出图片...")
        self.progress_var.set(0)

        # 创建输出目录（如果不存在）
        output_dir = self.output_directory.get()
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 处理每张图片
        total_images = len(self.image_paths)
        for i, input_path in enumerate(self.image_paths):
            try:
                # 生成输出文件名
                filename = os.path.basename(input_path)
                name, ext = os.path.splitext(filename)

                # 根据命名规则生成新文件名
                naming_rule = self.naming_rule.get()
                if naming_rule == "prefix":
                    prefix = self.naming_prefix.get()
                    new_name = f"{prefix}_{name}" if prefix else name
                elif naming_rule == "suffix":
                    suffix = self.naming_suffix.get()
                    new_name = f"{name}{suffix}" if suffix else name
                else:
                    new_name = name  # 保留原文件名

                # 根据输出格式设置扩展名
                output_format = self.output_format.get()
                if output_format == "JPEG":
                    output_ext = ".jpg"
                else:
                    output_ext = ".png"

                output_filename = new_name + output_ext
                output_path = os.path.join(output_dir, output_filename)

                # 添加水印并保存
                success = self.watermark_handler.add_text_watermark(
                    input_path,
                    output_path,
                    self.watermark_text.get(),
                    self.font_size.get(),
                    self.font_color.get(),
                    self.transparency.get(),
                    self.rotation.get(),
                    self.selected_position.get()
                )

                if success:
                    self.status_label.config(text=f"已处理: {filename}")
                else:
                    self.status_label.config(text=f"处理失败: {filename}")

                # 更新进度条
                progress = (i + 1) / total_images * 100
                self.progress_var.set(progress)
                self.root.update_idletasks()

            except Exception as e:
                messagebox.showerror("错误", f"处理图片 {filename} 时出错: {str(e)}")

        self.status_label.config(text=f"导出完成! 成功处理 {total_images} 张图片")
        self.progress_var.set(100)
        messagebox.showinfo("完成", f"导出完成! 成功处理 {total_images} 张图片")

    def show_help(self):
        """显示帮助"""
        messagebox.showinfo("使用说明", "PhotoWaterMark 桌面版使用说明")

    def show_about(self):
        """显示关于信息"""
        messagebox.showinfo("关于", "PhotoWaterMark 桌面版\n版本 1.0")

    def setup_layout(self):
        """设置布局"""
        # 绑定快捷键
        self.root.bind('<Control-o>', lambda e: self.import_images())
        self.root.bind('<Control-O>', lambda e: self.import_images())
        self.root.bind('<Control-Shift-O>', lambda e: self.import_folder())
        self.root.bind('<Control-s>', lambda e: self.save_template())
        self.root.bind('<Control-S>', lambda e: self.save_template())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Control-Q>', lambda e: self.root.quit())

def main():
    # 如果支持拖拽，使用TkinterDnD创建根窗口
    if DND_SUPPORTED:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()

    app = PhotoWaterMarkApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()