#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PhotoWaterMark - 桌面版图片水印工具
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk
import os
import sys

class PhotoWaterMarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PhotoWaterMark - 图片水印工具")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)

        # 存储导入的图片路径
        self.image_paths = []
        self.current_image_index = -1

        # 水印设置
        self.watermark_text = tk.StringVar(value="水印文本")
        self.font_size = tk.IntVar(value=24)
        self.font_color = tk.StringVar(value="black")
        self.transparency = tk.IntVar(value=100)
        self.rotation = tk.IntVar(value=0)

        # 导出设置
        self.output_directory = tk.StringVar()
        self.output_format = tk.StringVar(value="JPEG")
        self.naming_prefix = tk.StringVar()
        self.naming_suffix = tk.StringVar(value="_watermarked")
        self.allow_overwrite = tk.BooleanVar(value=False)

        # 当前模板
        self.current_template = tk.StringVar(value="默认模板")

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

        # 创建列表框和滚动条
        self.image_listbox = tk.Listbox(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.image_listbox.yview)
        self.image_listbox.configure(yscrollcommand=scrollbar.set)

        self.image_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定列表框选择事件
        self.image_listbox.bind('<<ListboxSelect>>', self.on_image_select)

        # 操作按钮
        button_frame = ttk.Frame(self.left_panel)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(button_frame, text="移除选中", command=self.remove_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="清空所有", command=self.clear_all).pack(side=tk.LEFT, padx=2)

    def on_image_select(self, event):
        """图片列表选择事件处理"""
        selection = self.image_listbox.curselection()
        if selection:
            index = selection[0]
            self.show_image(index)

    def create_middle_panel(self, parent):
        """创建中间面板"""
        self.middle_panel = ttk.Frame(parent)

        # 标题
        ttk.Label(self.middle_panel, text="图片预览", font=("微软雅黑", 12, "bold")).pack(pady=5)

        # 预览画布
        self.preview_canvas = tk.Canvas(self.middle_panel, bg="lightgray")
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

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
        ttk.Entry(self.watermark_frame, textvariable=self.watermark_text, width=20).grid(row=0, column=1, padx=5, pady=5)

        # 字体大小
        ttk.Label(self.watermark_frame, text="字体大小:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Scale(self.watermark_frame, from_=8, to=72, variable=self.font_size, orient=tk.HORIZONTAL).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Label(self.watermark_frame, textvariable=self.font_size).grid(row=1, column=2, padx=5, pady=5)

        # 字体颜色
        ttk.Label(self.watermark_frame, text="字体颜色:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        color_frame = ttk.Frame(self.watermark_frame)
        color_frame.grid(row=2, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        ttk.Entry(color_frame, textvariable=self.font_color, width=10).pack(side=tk.LEFT)
        ttk.Button(color_frame, text="选择", command=self.choose_color).pack(side=tk.LEFT, padx=5)

        # 透明度
        ttk.Label(self.watermark_frame, text="透明度:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Scale(self.watermark_frame, from_=0, to=100, variable=self.transparency, orient=tk.HORIZONTAL).grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Label(self.watermark_frame, textvariable=self.transparency).grid(row=3, column=2, padx=5, pady=5)

        # 旋转角度
        ttk.Label(self.watermark_frame, text="旋转角度:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Scale(self.watermark_frame, from_=-180, to=180, variable=self.rotation, orient=tk.HORIZONTAL).grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Label(self.watermark_frame, textvariable=self.rotation).grid(row=4, column=2, padx=5, pady=5)

    def create_position_settings(self):
        """创建位置设置界面"""
        # 九宫格位置按钮
        positions = [
            ("↖", "topLeft"), ("↑", "top"), ("↗", "topRight"),
            ("←", "left"), ("●", "center"), ("→", "right"),
            ("↙", "bottomLeft"), ("↓", "bottom"), ("↘", "bottomRight")
        ]

        for i, (text, pos) in enumerate(positions):
            row, col = divmod(i, 3)
            btn = ttk.Button(self.position_frame, text=text, width=5, command=lambda p=pos: self.set_watermark_position(p))
            btn.grid(row=row, column=col, padx=2, pady=2)

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
        ttk.Radiobutton(self.export_frame, text="保留原文件名", variable=self.naming_prefix, value="").grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Radiobutton(self.export_frame, text="添加前缀", variable=self.naming_prefix, value="prefix").grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(self.export_frame, textvariable=self.naming_prefix, width=15, state="disabled").grid(row=3, column=2, padx=5, pady=2)
        ttk.Radiobutton(self.export_frame, text="添加后缀", variable=self.naming_prefix, value="suffix").grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)
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

    def browse_output_directory(self):
        """浏览输出目录"""
        directory = filedialog.askdirectory(title="选择输出文件夹")
        if directory:
            self.output_directory.set(directory)

    def set_watermark_position(self, position):
        """设置水印位置"""
        self.status_label.config(text=f"水印位置设置为: {position}")

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
                self.image_listbox.insert(tk.END, filename)

        self.status_label.config(text=f"已导入 {len(self.image_paths)} 张图片")

        # 如果这是第一张图片，自动选择并显示
        if len(self.image_paths) == 1:
            self.image_listbox.selection_set(0)
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
                image = image.resize((new_width, new_height), Image.LANCZOS)

                # 转换为PhotoImage
                photo = ImageTk.PhotoImage(image)

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

    def remove_selected(self):
        """移除选中的图片"""
        selection = self.image_listbox.curselection()
        if selection:
            for index in reversed(selection):
                self.image_listbox.delete(index)
                del self.image_paths[index]
            self.status_label.config(text=f"已移除选中的图片，剩余 {len(self.image_paths)} 张")

    def clear_all(self):
        """清空所有图片"""
        if self.image_paths:
            if messagebox.askyesno("确认", "确定要清空所有图片吗？"):
                self.image_paths.clear()
                self.image_listbox.delete(0, tk.END)
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

    def save_template(self):
        """保存模板"""
        self.status_label.config(text="保存模板")

    def load_template(self):
        """加载模板"""
        self.status_label.config(text="加载模板")

    def manage_templates(self):
        """管理模板"""
        self.status_label.config(text="管理模板")

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

        self.status_label.config(text="开始导出图片...")

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
    root = tk.Tk()
    app = PhotoWaterMarkApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()