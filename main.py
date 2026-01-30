import os
import json
import re
import threading
import webbrowser
import tempfile
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
import requests

CURRENT_VERSION = "v1.0.0"
GITHUB_REPO = "czxieddan/FTAT"
UPDATE_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

DEFAULT_GOALS_TEMPLATE = """    SpriteType = {
        name = "{ICON}"
        texturefile = "gfx/icons/goals/{TAG}/{ID}.png"
        transparencecheck = yes
    }"""

DEFAULT_SHINE_TEMPLATE = """    SpriteType = {
        name = "{ICON}_shine"
        texturefile = "gfx/icons/goals/{TAG}/{ID}.png"
        effectFile = "gfx/FX/buttonstate.lua"
        animation = {
            animationmaskfile = "gfx/icons/goals/{TAG}/{ID}.png"
            animationtexturefile = "gfx/interface/goals/shine_overlay.dds"
            animationrotation = -90.0
            animationlooping = no
            animationtime = 0.75
            animationdelay = 0
            animationblendmode = "add"
            animationtype = "scrolling"
            animationrotationoffset = { x = 0.0 y = 0.0 }
            animationtexturescale = { x = 2.0 y = 1.0 }
        }
        animation = {
            animationmaskfile = "gfx/icons/goals/{TAG}/{ID}.png"
            animationtexturefile = "gfx/interface/goals/shine_overlay.dds"
            animationrotation = 90.0
            animationlooping = no
            animationtime = 0.75
            animationdelay = 0
            animationblendmode = "add"
            animationtype = "scrolling"
            animationrotationoffset = { x = 0.0 y = 0.0 }
            animationtexturescale = { x = 1.0 y = 1.0 }
        }
        legacy_lazy_load = no
        transparencecheck = yes
    }"""

DEFAULT_LOC_TEMPLATE = """ {ID}: ""
 {ID}_desc: ""
"""

DEFAULT_PATH_GOALS = "interface/{MOD}/icons/goals/{TAG}/{TAG}_{PROJECT}.gfx"
DEFAULT_PATH_SHINE = "interface/{MOD}/icons/goals/{TAG}/{TAG}_{PROJECT}_shine.gfx"
DEFAULT_PATH_LOC = "localisation/{LANG}/focus/{TAG}/{MOD}_focus_{TAG}_{PROJECT}_l_{LANG}.yml"

LANG_KEYS = [
    "braz_por", "english", "french", "german", "japanese", 
    "korean", "polish", "russian", "simp_chinese", "spanish"
]

LOC_LANG_NAMES = {
    "en": {
        "braz_por": "Portuguese (Brazil)", "english": "English", "french": "French", 
        "german": "German", "japanese": "Japanese", "korean": "Korean", 
        "polish": "Polish", "russian": "Russian", "simp_chinese": "Simplified Chinese", "spanish": "Spanish"
    },
    "zh_cn": {
        "braz_por": "葡萄牙语 (巴西)", "english": "英语", "french": "法语", 
        "german": "德语", "japanese": "日语", "korean": "韩语", 
        "polish": "波兰语", "russian": "俄语", "simp_chinese": "简体中文", "spanish": "西班牙语"
    },
    "zh_tw": {
        "braz_por": "葡萄牙語 (巴西)", "english": "英語", "french": "法語", 
        "german": "德語", "japanese": "日語", "korean": "韓語", 
        "polish": "波蘭語", "russian": "俄語", "simp_chinese": "簡體中文", "spanish": "西班牙語"
    }
}

UI_TEXTS = {
    "title": {"en": "HOI4 Focus Tree Asset Tool", "zh_cn": "HOI4 国策树资产生成工具", "zh_tw": "HOI4 國策樹資產生成工具"},
    "load_file": {"en": "Load Focus Tree (.txt)", "zh_cn": "读取国策树文件 (.txt)", "zh_tw": "讀取國策樹檔案 (.txt)"},
    "drag_hint": {"en": "Drag & Drop file here", "zh_cn": "拖拽文件到此处", "zh_tw": "拖曳檔案到此處"},
    "settings": {"en": "Settings", "zh_cn": "设置", "zh_tw": "設定"},
    "mod_abbr": {"en": "MOD Abbr", "zh_cn": "MOD缩写", "zh_tw": "MOD縮寫"},
    "tag": {"en": "TAG", "zh_cn": "TAG", "zh_tw": "TAG"},
    "project": {"en": "Project ID", "zh_cn": "项目编号", "zh_tw": "專案編號"},
    "loc_lang": {"en": "Loc Language", "zh_cn": "本地化语言", "zh_tw": "本地化語言"},
    "ui_lang": {"en": "UI Language", "zh_cn": "界面语言", "zh_tw": "介面語言"},
    "tab_goals": {"en": "Goals GFX", "zh_cn": "图标 GFX", "zh_tw": "圖標 GFX"},
    "tab_shine": {"en": "Shine GFX", "zh_cn": "光效 GFX", "zh_tw": "光效 GFX"},
    "tab_loc": {"en": "Localisation", "zh_cn": "本地化", "zh_tw": "本地化"},
    "template": {"en": "Template", "zh_cn": "模板", "zh_tw": "模板"},
    "path_template": {"en": "Export Path", "zh_cn": "导出路径", "zh_tw": "導出路徑"},
    "preview": {"en": "Preview", "zh_cn": "预览", "zh_tw": "預覽"},
    "save_file": {"en": "Save This File", "zh_cn": "保存当前文件", "zh_tw": "儲存當前檔案"},
    "save_to_mod": {"en": "Save to MOD", "zh_cn": "保存至 MOD", "zh_tw": "儲存至 MOD"},
    "load_preset": {"en": "Load Preset", "zh_cn": "加载预设", "zh_tw": "載入預設"},
    "save_preset": {"en": "Save Preset", "zh_cn": "保存预设", "zh_tw": "儲存預設"},
    "info_loaded": {"en": "Loaded {} focuses from {}", "zh_cn": "已从 {} 读取 {} 个国策", "zh_tw": "已從 {} 讀取 {} 個國策"},
    "error_params": {"en": "Please fill in all fields (MOD, TAG, Project)", "zh_cn": "请填写所有字段 (MOD, TAG, 项目编号)", "zh_tw": "請填寫所有欄位 (MOD, TAG, 專案編號)"},
    "success_save": {"en": "Saved to {}", "zh_cn": "已保存至 {}", "zh_tw": "已儲存至 {}"},
    "github": {"en": "GitHub", "zh_cn": "GitHub", "zh_tw": "GitHub"},
    "select_mod_dir": {"en": "Select MOD Root Directory", "zh_cn": "选择 MOD 根目录", "zh_tw": "選擇 MOD 根目錄"},
    "mod_dir_cancel": {"en": "Export cancelled. No MOD directory selected.", "zh_cn": "导出已取消。未选择 MOD 目录。", "zh_tw": "導出已取消。未選擇 MOD 目錄。"},
    "success_export": {"en": "Successfully exported all files to MOD directory.", "zh_cn": "成功导出所有文件至 MOD 目录。", "zh_tw": "成功導出所有檔案至 MOD 目錄。"},
    "warning": {"en": "Warning", "zh_cn": "警告", "zh_tw": "警告"},
    "error": {"en": "Error", "zh_cn": "错误", "zh_tw": "錯誤"},
    "info": {"en": "Info", "zh_cn": "提示", "zh_tw": "提示"},
    "success": {"en": "Success", "zh_cn": "成功", "zh_tw": "成功"},
    "save_preset_title": {"en": "Save Preset", "zh_cn": "保存预设", "zh_tw": "儲存預設"},
    "load_preset_title": {"en": "Load Preset", "zh_cn": "加载预设", "zh_tw": "載入預設"},
    "save_file_title": {"en": "Save File", "zh_cn": "保存文件", "zh_tw": "儲存檔案"},
    "mod_dir": {"en": "MOD Directory:", "zh_cn": "MOD 目录:", "zh_tw": "MOD 目錄:"},
    "change": {"en": "Change", "zh_cn": "更改", "zh_tw": "更改"},
    "not_selected": {"en": "Not Selected", "zh_cn": "未选择", "zh_tw": "未選擇"},
    "update_available": {"en": "New version {version} available!", "zh_cn": "发现新版本 {version}！", "zh_tw": "發現新版本 {version}！"},
    "download_button": {"en": "Download Update", "zh_cn": "下载更新", "zh_tw": "下載更新"},
    "downloading_update": {"en": "Downloading update... {percent}%", "zh_cn": "正在下载更新... {percent}%", "zh_tw": "正在下載更新... {percent}%"},
    "applying_update": {"en": "Update downloaded. Restarting...", "zh_cn": "更新下载完成，正在重启...", "zh_tw": "更新下載完成，正在重啟..."},
    "update_title": {"en": "Updating", "zh_cn": "正在更新", "zh_tw": "正在更新"},
    "version": {"en": "Version {version}", "zh_cn": "版本 {version}", "zh_tw": "版本 {version}"},
}

UI_LANG_MAP = {"English": "en", "简体中文": "zh_cn", "繁体中文": "zh_tw"}
UI_LANG_DISPLAY = list(UI_LANG_MAP.keys())

class ConfigManager:
    def __init__(self):
        self.config_path = os.path.join(tempfile.gettempdir(), "ftat_config.json")
        self.config = {
            "ui_language": "zh_cn",
            "loc_language": "simp_chinese",
            "mod_root": "",
            "last_load_dir": "",
            "last_save_dir": ""
        }
        self.load()

    def load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.config.update(data)
            except:
                pass

    def save(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except:
            pass

    def get(self, key):
        return self.config.get(key)

    def set(self, key, value):
        self.config[key] = value
        self.save()

class FocusParser:
    @staticmethod
    def parse(text):
        text = re.sub(r'#.*', '', text)
        definitions = []
        
        starts = []
        for match in re.finditer(r'(focus|shared_focus|joint_focus)\s*=\s*\{', text):
            starts.append(match)
            
        for match in starts:
            start_idx = match.end() - 1
            balance = 0
            end_idx = -1
            
            for i in range(start_idx, len(text)):
                if text[i] == '{':
                    balance += 1
                elif text[i] == '}':
                    balance -= 1
                    if balance == 0:
                        end_idx = i
                        break
            
            if end_idx != -1:
                block_content = text[start_idx+1:end_idx]
                FocusParser._parse_block_content(block_content, definitions)
                
        tag = ""
        project = ""
        
        tree_match = re.search(r'focus_tree\s*=\s*\{[^}]*id\s*=\s*([A-Za-z0-9_]+)', text)
        if tree_match:
            tree_id = tree_match.group(1)
            parts = tree_id.split('_')
            if len(parts) >= 2 and len(parts[0]) == 3:
                tag = parts[0]
                project = parts[1]
        
        if not tag:
            tag_match = re.search(r'country\s*=\s*\{.*?modifier\s*=\s*\{.*?tag\s*=\s*([A-Z]{3})', text, re.DOTALL)
            if tag_match:
                tag = tag_match.group(1)
                
        return definitions, tag, project

    @staticmethod
    def _parse_block_content(content, definitions):
        id_match = re.search(r'\bid\s*=\s*([^\s{}]+)', content)
        if not id_match:
            return
        
        focus_id = id_match.group(1).strip('"')
        icons = []
        
        depth = 0
        i = 0
        n = len(content)
        
        while i < n:
            char = content[i]
            
            if char == '{':
                depth += 1
                i += 1
                continue
            elif char == '}':
                depth -= 1
                i += 1
                continue
            
            if depth == 0 and char == 'i':
                is_start = (i == 0) or (not content[i-1].isalnum() and content[i-1] != '_')
                if is_start and content[i:i+4] == 'icon':
                    end_idx = i + 4
                    is_end = (end_idx >= n) or (not content[end_idx].isalnum() and content[end_idx] != '_')
                    
                    if is_end:
                        j = i + 4
                        while j < n and content[j].isspace():
                            j += 1
                        
                        if j < n and content[j] == '=':
                            i = j + 1
                            while i < n and content[i].isspace():
                                i += 1
                            
                            if i >= n:
                                break
                                
                            if content[i] == '{':
                                block_start = i
                                block_depth = 0
                                block_end = -1
                                
                                for k in range(i, n):
                                    if content[k] == '{':
                                        block_depth += 1
                                    elif content[k] == '}':
                                        block_depth -= 1
                                        if block_depth == 0:
                                            block_end = k
                                            break
                                
                                if block_end != -1:
                                    sub_block = content[block_start+1:block_end]
                                    val_match = re.search(r'value\s*=\s*("[^"]*"|[^\s{}]+)', sub_block)
                                    if val_match:
                                        icons.append(val_match.group(1).strip('"'))
                                    i = block_end + 1
                                else:
                                    i += 1
                            else:
                                if content[i] == '"':
                                    val_start = i + 1
                                    i += 1
                                    while i < n and content[i] != '"':
                                        i += 1
                                    val = content[val_start:i]
                                    i += 1
                                else:
                                    val_start = i
                                    while i < n and not content[i].isspace() and content[i] != '}':
                                        i += 1
                                    val = content[val_start:i]
                                icons.append(val)
                            continue
            i += 1
        
        definitions.append({'id': focus_id, 'icons': icons})

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class FTATApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)
        
        self.config_manager = ConfigManager()
        self.current_ui_lang = self.config_manager.get("ui_language")
        
        self.title(self.get_text("title"))
        self.geometry("1200x850")
        self.minsize(1000, 750)
        
        self.focus_data = []
        self.current_file_path = ""
        self.mod_root_dir = self.config_manager.get("mod_root")
        
        self.templates = {
            "goals": DEFAULT_GOALS_TEMPLATE,
            "shine": DEFAULT_SHINE_TEMPLATE,
            "loc": DEFAULT_LOC_TEMPLATE,
            "path_goals": DEFAULT_PATH_GOALS,
            "path_shine": DEFAULT_PATH_SHINE,
            "path_loc": DEFAULT_PATH_LOC
        }
        
        self.build_ui()
        self.update_ui_text()
        self.update_loc_lang_options()
        self.update_mod_dir_display()
        
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.on_drop)
        
        self.pending_update_version = None
        self.pending_update_url = None
        self.update_frame = None
        self.progress_window = None
        threading.Thread(target=self.check_for_update, daemon=True).start()

    def get_text(self, key):
        return UI_TEXTS.get(key, {}).get(self.current_ui_lang, key)

    def build_ui(self):
        self.top_frame = ctk.CTkFrame(self, height=60, corner_radius=0)
        self.top_frame.pack(fill="x", padx=10, pady=10)
        
        self.btn_load = ctk.CTkButton(self.top_frame, command=self.load_file, width=200)
        self.btn_load.pack(side="left", padx=10)
        
        self.lbl_drag_hint = ctk.CTkLabel(self.top_frame, text=self.get_text("drag_hint"), text_color="gray", width=200, anchor="w")
        self.lbl_drag_hint.pack(side="left", padx=10)
        
        self.btn_github = ctk.CTkButton(self.top_frame, command=lambda: webbrowser.open(f"https://github.com/{GITHUB_REPO}"), 
                                        fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), width=100)
        self.btn_github.pack(side="right", padx=10)
        
        self.ui_lang_var = ctk.StringVar()
        for k, v in UI_LANG_MAP.items():
            if v == self.current_ui_lang:
                self.ui_lang_var.set(k)
                break
        
        self.combo_ui_lang = ctk.CTkOptionMenu(self.top_frame, values=UI_LANG_DISPLAY, command=self.change_ui_language, width=120)
        self.combo_ui_lang.set(self.ui_lang_var.get())
        self.combo_ui_lang.pack(side="right", padx=5)
        
        self.lbl_ui_lang = ctk.CTkLabel(self.top_frame, width=100, anchor="e")
        self.lbl_ui_lang.pack(side="right", padx=5)

        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(fill="x", padx=10, pady=5)
        
        self.settings_frame.grid_columnconfigure((0, 2, 4, 6, 7), weight=0)
        self.settings_frame.grid_columnconfigure((1, 3, 5), weight=1)
        
        self.lbl_mod = ctk.CTkLabel(self.settings_frame, width=100, anchor="e")
        self.lbl_mod.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.ent_mod = ctk.CTkEntry(self.settings_frame, width=100)
        self.ent_mod.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.ent_mod.bind("<KeyRelease>", self.on_param_change)
        
        self.lbl_tag = ctk.CTkLabel(self.settings_frame, width=60, anchor="e")
        self.lbl_tag.grid(row=0, column=2, padx=10, pady=10, sticky="e")
        self.ent_tag = ctk.CTkEntry(self.settings_frame, width=100)
        self.ent_tag.grid(row=0, column=3, padx=5, pady=10, sticky="ew")
        self.ent_tag.bind("<KeyRelease>", self.on_param_change)
        
        self.lbl_project = ctk.CTkLabel(self.settings_frame, width=100, anchor="e")
        self.lbl_project.grid(row=0, column=4, padx=10, pady=10, sticky="e")
        self.ent_project = ctk.CTkEntry(self.settings_frame, width=100)
        self.ent_project.grid(row=0, column=5, padx=5, pady=10, sticky="ew")
        self.ent_project.bind("<KeyRelease>", self.on_param_change)
        
        self.lbl_lang = ctk.CTkLabel(self.settings_frame, width=120, anchor="e")
        self.lbl_lang.grid(row=0, column=6, padx=10, pady=10, sticky="e")
        
        self.combo_loc_lang = ctk.CTkOptionMenu(self.settings_frame, command=self.on_loc_lang_change, width=220)
        self.combo_loc_lang.grid(row=0, column=7, padx=5, pady=10, sticky="ew")

        self.mod_dir_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.mod_dir_frame.pack(fill="x", padx=20, pady=(0, 5))
        
        self.lbl_mod_dir_title = ctk.CTkLabel(self.mod_dir_frame, font=ctk.CTkFont(weight="bold"))
        self.lbl_mod_dir_title.pack(side="left")
        
        self.lbl_mod_dir_path = ctk.CTkLabel(self.mod_dir_frame, text_color="gray")
        self.lbl_mod_dir_path.pack(side="left", padx=10)
        
        self.btn_change_mod_dir = ctk.CTkButton(self.mod_dir_frame, command=self.change_mod_directory, width=80, height=24)
        self.btn_change_mod_dir.pack(side="left", padx=5)
        
        self.lbl_version = ctk.CTkLabel(self.mod_dir_frame, text=self.get_text("version").format(version=CURRENT_VERSION), text_color="gray")
        self.lbl_version.pack(side="right")
        
        self.btn_update = ctk.CTkButton(self.mod_dir_frame, text="", fg_color="#D70000", hover_color="#B50000", height=24)

        self.tab_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.tab_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.tab_nav = ctk.CTkSegmentedButton(self.tab_frame, command=self.on_tab_change)
        self.tab_nav.pack(fill="x", pady=(0, 10))

        self.content_area = ctk.CTkFrame(self.tab_frame, fg_color="transparent")
        self.content_area.pack(fill="both", expand=True)
        
        self.frames = {}
        self.frames["goals"] = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.frames["shine"] = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.frames["loc"] = ctk.CTkFrame(self.content_area, fg_color="transparent")
        
        self.create_editor_content(self.frames["goals"], "goals", "path_goals")
        self.create_editor_content(self.frames["shine"], "shine", "path_shine")
        self.create_editor_content(self.frames["loc"], "loc", "path_loc")
        
        self.current_tab_key = "goals"
        
        self.bottom_frame = ctk.CTkFrame(self, height=50, fg_color="transparent")
        self.bottom_frame.pack(fill="x", padx=10, pady=10)
        
        self.btn_save_preset = ctk.CTkButton(self.bottom_frame, command=self.save_preset, width=140)
        self.btn_save_preset.pack(side="left", padx=5)
        
        self.btn_load_preset = ctk.CTkButton(self.bottom_frame, command=self.load_preset, width=140)
        self.btn_load_preset.pack(side="left", padx=5)
        
        self.btn_save_mod = ctk.CTkButton(self.bottom_frame, command=self.save_to_mod, fg_color="#2CC985", hover_color="#229965", width=140)
        self.btn_save_mod.pack(side="right", padx=5)
        
        self.btn_save_current = ctk.CTkButton(self.bottom_frame, command=self.save_current_file, width=140)
        self.btn_save_current.pack(side="right", padx=5)

    def create_editor_content(self, parent, type_key, path_key):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=0)
        parent.grid_rowconfigure(1, weight=0)
        parent.grid_rowconfigure(2, weight=1)
        
        path_frame = ctk.CTkFrame(parent, fg_color="transparent")
        path_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        lbl_path = ctk.CTkLabel(path_frame, font=ctk.CTkFont(weight="bold"))
        lbl_path.pack(side="left")
        
        ent_path = ctk.CTkEntry(path_frame)
        ent_path.pack(side="left", fill="x", expand=True, padx=10)
        ent_path.insert(0, self.templates[path_key])
        ent_path.bind("<KeyRelease>", lambda e: self.on_path_change(path_key, ent_path))
        
        lbl_template = ctk.CTkLabel(parent, font=ctk.CTkFont(weight="bold"))
        lbl_template.grid(row=1, column=0, sticky="w", padx=0, pady=(0, 5))
        
        lbl_preview = ctk.CTkLabel(parent, font=ctk.CTkFont(weight="bold"))
        lbl_preview.grid(row=1, column=1, sticky="w", padx=5, pady=(0, 5))
        
        txt_template = ctk.CTkTextbox(parent, font=("Consolas", 12))
        txt_template.grid(row=2, column=0, sticky="nsew", padx=(0, 5))
        txt_template.insert("1.0", self.templates[type_key])
        txt_template.bind("<KeyRelease>", lambda e: self.on_template_change(type_key, txt_template))
        
        txt_preview = ctk.CTkTextbox(parent, font=("Consolas", 12), fg_color=("gray90", "gray20"))
        txt_preview.grid(row=2, column=1, sticky="nsew", padx=(5, 0))
        txt_preview.configure(state="disabled")
        
        setattr(self, f"txt_template_{type_key}", txt_template)
        setattr(self, f"txt_preview_{type_key}", txt_preview)
        setattr(self, f"lbl_template_{type_key}", lbl_template)
        setattr(self, f"lbl_preview_{type_key}", lbl_preview)
        setattr(self, f"lbl_path_{type_key}", lbl_path)
        setattr(self, f"ent_path_{type_key}", ent_path)

    def update_ui_text(self):
        self.title(self.get_text("title"))
        self.btn_load.configure(text=self.get_text("load_file"))
        self.lbl_drag_hint.configure(text=self.get_text("drag_hint"))
        self.btn_github.configure(text=self.get_text("github"))
        self.lbl_ui_lang.configure(text=self.get_text("ui_lang"))
        
        self.lbl_mod.configure(text=self.get_text("mod_abbr"))
        self.lbl_tag.configure(text=self.get_text("tag"))
        self.lbl_project.configure(text=self.get_text("project"))
        self.lbl_lang.configure(text=self.get_text("loc_lang"))
        
        self.lbl_mod_dir_title.configure(text=self.get_text("mod_dir"))
        self.btn_change_mod_dir.configure(text=self.get_text("change"))
        self.lbl_version.configure(text=self.get_text("version").format(version=CURRENT_VERSION))
        
        tab_values = [self.get_text("tab_goals"), self.get_text("tab_shine"), self.get_text("tab_loc")]
        self.tab_nav.configure(values=tab_values)
        
        current_text = self.get_text(f"tab_{self.current_tab_key}")
        self.tab_nav.set(current_text)
        
        self.show_tab(self.current_tab_key)

        for key in ["goals", "shine", "loc"]:
            getattr(self, f"lbl_template_{key}").configure(text=self.get_text("template"))
            getattr(self, f"lbl_preview_{key}").configure(text=self.get_text("preview"))
            getattr(self, f"lbl_path_{key}").configure(text=self.get_text("path_template"))
            
        self.btn_save_preset.configure(text=self.get_text("save_preset"))
        self.btn_load_preset.configure(text=self.get_text("load_preset"))
        self.btn_save_mod.configure(text=self.get_text("save_to_mod"))
        self.btn_save_current.configure(text=self.get_text("save_file"))
        
        self.update_mod_dir_display()

    def update_loc_lang_options(self):
        current_loc_code = self.config_manager.get("loc_language")
        display_map = LOC_LANG_NAMES.get(self.current_ui_lang, LOC_LANG_NAMES["en"])
        display_values = []
        current_display = ""
        
        for code in LANG_KEYS:
            name = display_map.get(code, code)
            display_str = f"{name} ({code})"
            display_values.append(display_str)
            if code == current_loc_code:
                current_display = display_str
        
        self.combo_loc_lang.configure(values=display_values)
        if current_display:
            self.combo_loc_lang.set(current_display)
        elif display_values:
            self.combo_loc_lang.set(display_values[1])

    def update_mod_dir_display(self):
        if self.mod_root_dir:
            self.lbl_mod_dir_path.configure(text=self.mod_root_dir, text_color=("black", "white"))
        else:
            self.lbl_mod_dir_path.configure(text=self.get_text("not_selected"), text_color="gray")

    def change_ui_language(self, choice):
        self.current_ui_lang = UI_LANG_MAP[choice]
        self.config_manager.set("ui_language", self.current_ui_lang)
        self.update_ui_text()
        self.update_loc_lang_options()
        if self.pending_update_version:
             self.show_update_prompt(self.pending_update_version, self.pending_update_url)

    def on_loc_lang_change(self, choice):
        match = re.search(r'\(([^)]+)\)$', choice)
        if match:
            code = match.group(1)
            self.config_manager.set("loc_language", code)
            self.refresh_previews()

    def on_tab_change(self, value):
        key_map = {
            self.get_text("tab_goals"): "goals",
            self.get_text("tab_shine"): "shine",
            self.get_text("tab_loc"): "loc"
        }
        key = key_map.get(value, "goals")
        self.current_tab_key = key
        self.show_tab(key)

    def show_tab(self, key):
        for k, frame in self.frames.items():
            if k == key:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()

    def change_mod_directory(self):
        initial = self.mod_root_dir if self.mod_root_dir else self.config_manager.get("last_load_dir")
        dir_path = filedialog.askdirectory(title=self.get_text("select_mod_dir"), initialdir=initial)
        if dir_path:
            self.mod_root_dir = dir_path
            self.config_manager.set("mod_root", dir_path)
            self.update_mod_dir_display()

    def on_drop(self, event):
        files = self.tk.splitlist(event.data)
        if files:
            self.process_file(files[0])

    def load_file(self):
        initial = self.config_manager.get("last_load_dir")
        filepath = filedialog.askopenfilename(
            title=self.get_text("load_file"),
            filetypes=[("Focus Tree", "*.txt"), ("All Files", "*.*")],
            initialdir=initial
        )
        if filepath:
            self.config_manager.set("last_load_dir", os.path.dirname(filepath))
            self.process_file(filepath)

    def process_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(filepath, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
            except:
                messagebox.showerror(self.get_text("error"), "Failed to read file. Please ensure it is UTF-8 encoded.")
                return

        self.current_file_path = filepath
        definitions, tag, project = FocusParser.parse(content)
        self.focus_data = definitions
        
        if tag:
            self.ent_tag.delete(0, "end")
            self.ent_tag.insert(0, tag)
        if project:
            self.ent_project.delete(0, "end")
            self.ent_project.insert(0, project)
            
        messagebox.showinfo(self.get_text("info"), self.get_text("info_loaded").format(len(definitions), os.path.basename(filepath)))
        self.refresh_previews()

    def on_param_change(self, event=None):
        self.refresh_previews()

    def on_template_change(self, type_key, widget):
        self.templates[type_key] = widget.get("1.0", "end").rstrip("\n")
        self.refresh_previews(type_key)

    def on_path_change(self, path_key, widget):
        self.templates[path_key] = widget.get().strip()

    def get_params(self):
        return {
            "MOD": self.ent_mod.get().strip(),
            "TAG": self.ent_tag.get().strip(),
            "PROJECT": self.ent_project.get().strip(),
            "LANG": self.config_manager.get("loc_language")
        }

    def generate_content(self, type_key):
        params = self.get_params()
        template = self.templates[type_key]
        
        output = []
        
        if type_key == "loc":
            output.append(f"l_{params['LANG']}:")
            output.append(f" # {params['TAG']} {params['PROJECT']}")
            output.append("")
            
            for item in self.focus_data:
                block = template.replace("{ID}", item['id'])
                for k, v in params.items():
                    block = block.replace(f"{{{k}}}", v)
                output.append(block)
        else:
            output.append("spriteTypes = {")
            
            for item in self.focus_data:
                icons = item['icons']
                if not icons:
                    continue
                    
                for i, icon in enumerate(icons):
                    current_id = item['id']
                    if len(icons) > 1:
                        current_id = f"{item['id']}_{i}"
                    
                    block = template.replace("{ICON}", icon).replace("{ID}", current_id)
                    for k, v in params.items():
                        block = block.replace(f"{{{k}}}", v)
                    
                    if type_key == "shine":
                        output.append("###############################################################################################")
                    output.append(block)
            
            output.append("}")
            
        return "\n".join(output)

    def refresh_previews(self, specific_key=None):
        keys = [specific_key] if specific_key else ["goals", "shine", "loc"]
        
        for key in keys:
            content = self.generate_content(key)
            widget = getattr(self, f"txt_preview_{key}")
            widget.configure(state="normal")
            widget.delete("1.0", "end")
            widget.insert("1.0", content)
            widget.configure(state="disabled")

    def save_preset(self):
        initial = self.config_manager.get("last_save_dir")
        filepath = filedialog.asksaveasfilename(
            title=self.get_text("save_preset_title"),
            filetypes=[("JSON Preset", "*.json")], 
            defaultextension=".json",
            initialdir=initial
        )
        if filepath:
            self.config_manager.set("last_save_dir", os.path.dirname(filepath))
            data = self.templates.copy()
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            messagebox.showinfo(self.get_text("success"), self.get_text("success"))

    def load_preset(self):
        initial = self.config_manager.get("last_load_dir")
        filepath = filedialog.askopenfilename(
            title=self.get_text("load_preset_title"),
            filetypes=[("JSON Preset", "*.json")],
            initialdir=initial
        )
        if filepath:
            self.config_manager.set("last_load_dir", os.path.dirname(filepath))
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.templates.update(data)
            
            for key in ["goals", "shine", "loc"]:
                widget = getattr(self, f"txt_template_{key}")
                widget.delete("1.0", "end")
                widget.insert("1.0", self.templates[key])
                
                path_widget = getattr(self, f"ent_path_{key}")
                path_widget.delete(0, "end")
                path_widget.insert(0, self.templates.get(f"path_{key}", ""))
                
            self.refresh_previews()

    def save_current_file(self):
        if self.current_tab_key in ["goals", "shine", "loc"]:
            self._save_file_dialog(self.current_tab_key)

    def _save_file_dialog(self, key):
        params = self.get_params()
        content = self.generate_content(key)
        
        filename = "untitled"
        if key == "goals":
            filename = f"{params['TAG']}_{params['PROJECT']}.gfx"
        elif key == "shine":
            filename = f"{params['TAG']}_{params['PROJECT']}_shine.gfx"
        elif key == "loc":
            filename = f"{params['MOD']}_focus_{params['TAG']}_{params['PROJECT']}_l_{params['LANG']}.yml"
            
        initial = self.config_manager.get("last_save_dir")
        filepath = filedialog.asksaveasfilename(
            initialfile=filename, 
            title=self.get_text("save_file_title"),
            filetypes=[("GFX/YML", "*.gfx *.yml"), ("All Files", "*.*")],
            initialdir=initial
        )
        
        if filepath:
            self.config_manager.set("last_save_dir", os.path.dirname(filepath))
            encoding = 'utf-8'
            if key == "loc":
                encoding = 'utf-8-sig'
                
            with open(filepath, 'w', encoding=encoding, newline='\n') as f:
                f.write(content)
            
            messagebox.showinfo(self.get_text("success"), self.get_text("success_save").format(os.path.basename(filepath)))

    def save_to_mod(self):
        params = self.get_params()
        if not params["TAG"] or not params["PROJECT"] or not params["MOD"]:
            messagebox.showerror(self.get_text("error"), self.get_text("error_params"))
            return

        if not self.mod_root_dir:
            self.change_mod_directory()
            if not self.mod_root_dir:
                messagebox.showwarning(self.get_text("warning"), self.get_text("mod_dir_cancel"))
                return

        for key, path_key in [("goals", "path_goals"), ("shine", "path_shine"), ("loc", "path_loc")]:
            content = self.generate_content(key)
            path_template = self.templates[path_key]
            
            rel_path = path_template
            for k, v in params.items():
                rel_path = rel_path.replace(f"{{{k}}}", v)
            
            full_path = os.path.join(self.mod_root_dir, rel_path)
            
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            encoding = 'utf-8'
            if key == "loc":
                encoding = 'utf-8-sig'
                
            try:
                with open(full_path, 'w', encoding=encoding, newline='\n') as f:
                    f.write(content)
            except Exception as e:
                messagebox.showerror(self.get_text("error"), f"Failed to save {key}: {str(e)}")
                return

        messagebox.showinfo(self.get_text("success"), self.get_text("success_export"))

    def parse_version(self, v):
        return tuple(map(int, v.lstrip('v').split('.')))

    def check_for_update(self):
        try:
            response = requests.get(UPDATE_API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            latest_tag = data["tag_name"]
            latest_version = self.parse_version(latest_tag)
            current_version = self.parse_version(CURRENT_VERSION)
            
            if latest_version > current_version:
                download_url = None
                for asset in data["assets"]:
                    if asset["name"].endswith(".exe"):
                        download_url = asset["browser_download_url"]
                        break
                if download_url:
                    self.pending_update_version = latest_tag
                    self.pending_update_url = download_url
                    self.after(0, lambda: self.show_update_prompt(latest_tag, download_url))
        except Exception:
            pass

    def show_update_prompt(self, latest_version, download_url):
        self.btn_update.configure(text=self.get_text("update_available").format(version=latest_version), 
                                  command=lambda: self.start_update(download_url))
        self.btn_update.pack(side="right", padx=10)

    def start_update(self, url):
        self.btn_update.pack_forget()
        self.create_progress_window()
        threading.Thread(target=self.download_thread, args=(url,), daemon=True).start()

    def create_progress_window(self):
        self.progress_window = ctk.CTkToplevel(self)
        self.progress_window.title(self.get_text("update_title"))
        self.progress_window.geometry("400x120")
        self.progress_window.resizable(False, False)
        self.progress_window.transient(self)
        self.progress_window.grab_set()
        
        self.progress_label = ctk.CTkLabel(self.progress_window, text=self.get_text("downloading_update").format(percent=0))
        self.progress_label.pack(pady=20)
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_window, width=350)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

    def update_progress(self, percent):
        if self.progress_window:
            self.progress_label.configure(text=self.get_text("downloading_update").format(percent=int(percent * 100)))
            self.progress_bar.set(percent)

    def download_thread(self, url):
        temp_dir = tempfile.gettempdir()
        new_exe = os.path.join(temp_dir, "FTAT_new.exe")
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                total = int(r.headers.get('content-length', 0))
                downloaded = 0
                with open(new_exe, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total > 0:
                                percent = downloaded / total
                                self.after(0, self.update_progress, percent)
            self.after(0, self.apply_update_after_download)
        except Exception:
            self.after(0, lambda: messagebox.showerror(self.get_text("error"), "Update failed."))
            if self.progress_window:
                self.progress_window.destroy()

    def apply_update_after_download(self):
        if self.progress_window:
            self.progress_label.configure(text=self.get_text("applying_update"))
            self.progress_window.update()
            
        temp_dir = tempfile.gettempdir()
        new_exe = os.path.join(temp_dir, "FTAT_new.exe")
        bat_file = os.path.join(temp_dir, "ftat_update.bat")
        current_exe = sys.executable
        exe_name = os.path.basename(current_exe)
        
        bat_content = f'''@echo off
:retry
ping 127.0.0.1 -n 3 > nul
taskkill /f /im "{exe_name}" > nul 2>&1
if exist "{current_exe}" (
    move /Y "{new_exe}" "{current_exe}" > nul
    if not exist "{new_exe}" goto success
    goto retry
)
:success
start "" "{current_exe}"
del "%~f0"
'''
        with open(bat_file, "w") as f:
            f.write(bat_content)

        env = os.environ.copy()
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            meipass = sys._MEIPASS.lower()
            if 'PATH' in env:
                paths = env['PATH'].split(os.pathsep)
                env['PATH'] = os.pathsep.join([p for p in paths if meipass not in p.lower()])
            
            keys_to_remove = [k for k, v in env.items() if meipass in str(v).lower() and k.upper() != 'PATH']
            for k in keys_to_remove:
                del env[k]
            
            for k in list(env.keys()):
                if k.startswith('_PYI_') or k == '_MEIPASS2':
                    del env[k]

        subprocess.Popen(bat_file, creationflags=subprocess.CREATE_NO_WINDOW, env=env)
        self.quit()

if __name__ == "__main__":
    app = FTATApp()
    app.mainloop()
