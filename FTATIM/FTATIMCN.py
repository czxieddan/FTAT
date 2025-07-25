import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import re

class FocusIconConverter:
    def __init__(self, master):
        self.master = master
        master.title("国策树icon格式转换工具适配FTAT(https://github.com/czxieddan/FTAT)(中文版)by@CzXieDdan——czxieddan.top")
        master.geometry("1000x700")

        self.text = scrolledtext.ScrolledText(master, wrap=tk.WORD, font=("Consolas", 12))
        self.text.pack(expand=True, fill=tk.BOTH)

        self.button_frame = tk.Frame(master)
        self.button_frame.pack(fill=tk.X)

        self.load_btn = tk.Button(self.button_frame, text="打开文件", command=self.load_file)
        self.load_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.convert_btn = tk.Button(self.button_frame, text="转换icon格式", command=self.convert_icons)
        self.convert_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.save_btn = tk.Button(self.button_frame, text="保存文件", command=self.save_file)
        self.save_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.preview_btn = tk.Button(self.button_frame, text="icon列表", command=self.preview_icons)
        self.preview_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.filename = None

    def load_file(self):
        filename = filedialog.askopenfilename(filetypes=[("txt文件", "*.txt"), ("所有文件", "*.*")])
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    data = f.read()
                    self.text.delete(1.0, tk.END)
                    self.text.insert(tk.END, data)
                self.filename = filename
            except Exception as e:
                messagebox.showerror("错误", f"无法打开文件: {e}")

    def save_file(self):
        if self.filename:
            import os
            original_name = os.path.basename(self.filename)
            save_filename = filedialog.asksaveasfilename(
                initialfile=original_name,
                defaultextension=".txt",
                filetypes=[("txt文件", "*.txt"), ("所有文件", "*.*")]
            )
            if save_filename:
                try:
                    with open(save_filename, "w", encoding="utf-8") as f:
                        f.write(self.text.get(1.0, tk.END))
                    messagebox.showinfo("保存成功", f"文件已保存到: {save_filename}")
                except Exception as e:
                    messagebox.showerror("错误", f"无法保存文件: {e}")
        else:
            messagebox.showwarning("警告", "请先打开一个文件")

    def convert_icons(self):
        content = self.text.get(1.0, tk.END)
        focus_pattern = re.compile(r'(focus\s*=\s*{[^}]*?id\s*=\s*(\w+)[^}]*?icon\s*=\s*)(\S+)', re.DOTALL)
        def icon_replacer(match):
            prefix = match.group(1)
            focus_id = match.group(2)
            new_icon = f'GFX_focus_goals_{focus_id}'
            return f'{prefix}{new_icon}'
        new_content = focus_pattern.sub(icon_replacer, content)
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, new_content)
        messagebox.showinfo("转换完成", "已将所有icon转换为GFX_focus_goals_<id>格式")

    def preview_icons(self):
        content = self.text.get(1.0, tk.END)
        focus_pattern = re.compile(r'focus\s*=\s*{[^}]*?id\s*=\s*(\w+)[^}]*?icon\s*=\s*(\S+)', re.DOTALL)
        focus_icons = focus_pattern.findall(content)
        preview_win = tk.Toplevel(self.master)
        preview_win.title("icon列表")
        preview_win.geometry("600x400")
        preview_text = scrolledtext.ScrolledText(preview_win, wrap=tk.WORD, font=("Consolas", 12))
        preview_text.pack(expand=True, fill=tk.BOTH)
        for focus_id, icon in focus_icons:
            preview_text.insert(tk.END, f"id: {focus_id}  icon: {icon}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = FocusIconConverter(root)
    root.mainloop()