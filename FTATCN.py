import tkinter as tk
from tkinter import filedialog, messagebox
import re
import os

def is_valid_localization_id(key):
    key = key.strip()
    if key.lower().replace(":", "") == "l_simp_chinese":
        return False
    if key.endswith("_desc") or key.endswith("_tt") or key.endswith("_text"):
        return False
    return True

def extract_ids_from_localization(filename):
    ids = []
    try:
        with open(filename, encoding='utf-8-sig') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if ":" in line:
                    key = line.split(":", 1)[0].strip()
                    if is_valid_localization_id(key):
                        ids.append(key)
    except Exception as e:
        messagebox.showerror("读取本地化文件失败", str(e))
    return ids

def extract_ids_from_national_focus(filename):
    ids = []
    tag = ""
    name = ""
    try:
        with open(filename, encoding='utf-8-sig') as f:
            text = f.read()
            m = re.search(r'focus_tree\s*=\s*{\s*id\s*=\s*([^\s\}\n]+)', text)
            if m:
                focus_tree_id = m.group(1)
                tree_parts = focus_tree_id.split("_")
                ids_raw = re.findall(r'focus\s*=\s*{[^}]*?id\s*=\s*([^\s\}\n]+)', text)
                ids = [id_ for id_ in ids_raw if len(id_) >= 1]
                if ids:
                    first_focus_parts = ids[0].split("_")
                    if len(tree_parts) >= 2 and len(first_focus_parts) >= 2:
                        if tree_parts[0] == first_focus_parts[0] and tree_parts[1] == first_focus_parts[1]:
                            tag = tree_parts[0]
                            name = tree_parts[1]
    except Exception as e:
        messagebox.showerror("读取国策树文件失败", str(e))
    return tag, name, ids

def parse_id_lines(id_lines):
    parsed = []
    for line in id_lines:
        line = line.strip()
        if not line:
            continue
        if line.endswith('#'):
            parsed.append((line[:-1].strip(), True))
        else:
            parsed.append((line, False))
    return parsed

def generate_sprite(tag, id_):
    return f'''    SpriteType = {{
        name = "GFX_focus_goals_{id_}"
        texturefile = "gfx/icons/goals/{tag}/{id_}.png"
    }}
'''

def generate_sprite_shine(tag, id_):
    return f'''    SpriteType = {{
        name = "GFX_focus_goals_{id_}_shine"
        texturefile = "gfx/icons/goals/{tag}/{id_}.png"
        effectFile = "gfx/FX/buttonstate.lua"
        animation = {{
            animationmaskfile = "gfx/icons/goals/{tag}/{id_}.png"
            animationtexturefile = "gfx/interface/goals/shine_overlay.dds"
            animationrotation = -90.0
            animationlooping = no
            animationtime = 0.75
            animationdelay = 0
            animationblendmode = "add"
            animationtype = "scrolling"
            animationrotationoffset = {{ x = 0.0 y = 0.0 }}
            animationtexturescale = {{ x = 2.0 y = 1.0 }}
        }}
        animation = {{
            animationmaskfile = "gfx/icons/goals/{tag}/{id_}.png"
            animationtexturefile = "gfx/interface/goals/shine_overlay.dds"
            animationrotation = 90.0
            animationlooping = no
            animationtime = 0.75
            animationdelay = 0
            animationblendmode = "add"
            animationtype = "scrolling"
            animationrotationoffset = {{ x = 0.0 y = 0.0 }}
            animationtexturescale = {{ x = 1.0 y = 1.0 }}
        }}
        legacy_lazy_load = no
    }}
'''

def generate_files(name, tag, id_tuples):
    ids = [id_ for id_, _ in id_tuples]
    goals_lines = ['spriteTypes = {\n']
    shine_lines = ['spriteTypes = {\n']
    for id_ in ids:
        goals_lines.append(generate_sprite(tag, id_))
        shine_lines.append('###############################################################################################\n')
        shine_lines.append(generate_sprite_shine(tag, id_))
    goals_lines.append('}\n')
    shine_lines.append('}\n')
    return ''.join(goals_lines), ''.join(shine_lines)

def generate_localization_file(mod_name, name, tag, id_tuples):
    header = f'''l_simp_chinese: 
 # 注意此为{tag}_{name}国策本地化 请勿在此填写无关内容 
 # 国策的ID为 TAG_FOCUSTREEID_PROJECT_ID 
 
 
 
 # {tag} {name}
'''
    content = []
    for id_, mark in id_tuples:
        mark_str = " #######" if mark else ""
        content.append(f" {id_}: \"\"{mark_str}")
        content.append(f" {id_}_desc: \"\"")
        content.append("")
    return header + "\n".join(content)

def save_file(content, defaultname):
    filepath = filedialog.asksaveasfilename(defaultextension=os.path.splitext(defaultname)[1], initialfile=defaultname)
    if filepath:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        messagebox.showinfo("保存成功", f"文件已保存到:\n{filepath}")

def on_load_localization():
    filepath = filedialog.askopenfilename(filetypes=[("YML/YAML/文本文件", "*.yml *.yaml *.txt"), ("所有文件", "*.*")])
    if filepath:
        entry_loc.delete(0, tk.END)
        entry_loc.insert(0, filepath)
        ids = extract_ids_from_localization(filepath)
        text_ids.delete("1.0", tk.END)
        text_ids.insert(tk.END, "\n".join(ids))
        tag, name = "", ""

        if ids:
            parts = ids[0].split("_")
            if len(parts) >= 2:
                tag_cand = parts[0]
                name_cand = parts[1]
                consistent = all(i.split("_")[:2] == [tag_cand, name_cand] if len(i.split("_")) >=2 else False for i in ids[:5])
                if consistent:
                    tag = tag_cand
                    name = name_cand
        entry_tag.delete(0, tk.END)
        entry_tag.insert(0, tag)
        entry_name.delete(0, tk.END)
        entry_name.insert(0, name)
        entry_mod.delete(0, tk.END)

        filename = os.path.basename(filepath)
        m = re.match(r"([A-Za-z0-9]+)_focus_", filename)
        if m:
            entry_mod.insert(0, m.group(1))
        messagebox.showinfo("提取完成", f"已从本地化文件中提取 {len(ids)} 个ID。")

def on_load_focus_file():
    filepath = filedialog.askopenfilename(filetypes=[("国策树文件", "*.txt *.focus *.yml *.yaml *.json"), ("所有文件", "*.*")])
    if filepath:
        tag, name, ids = extract_ids_from_national_focus(filepath)
        entry_loc.delete(0, tk.END)
        entry_loc.insert(0, filepath)
        entry_tag.delete(0, tk.END)
        entry_name.delete(0, tk.END)
        if tag and name:
            entry_tag.insert(0, tag)
            entry_name.insert(0, name)
        text_ids.delete("1.0", tk.END)
        text_ids.insert(tk.END, "\n".join(ids))

        messagebox.showinfo("提取完成", f"已从国策树文件中提取 {len(ids)} 个ID。" + (f"\nTAG: {tag}, NAME: {name}" if tag and name else "\n未能自动识别TAG和NAME。"))

def on_generate():
    mod_name = entry_mod.get().strip()
    name = entry_name.get().strip()
    tag = entry_tag.get().strip()
    id_lines = text_ids.get("1.0", tk.END).strip().splitlines()
    if not mod_name or not name or not tag or not id_lines or id_lines == ['']:
        messagebox.showerror("参数错误", "请填写所有参数！")
        return
    id_tuples = parse_id_lines(id_lines)
    goals, shine = generate_files(name, tag, id_tuples)
    localization = generate_localization_file(mod_name, name, tag, id_tuples)
    result_goals.delete("1.0", tk.END)
    result_goals.insert(tk.END, goals)
    result_shine.delete("1.0", tk.END)
    result_shine.insert(tk.END, shine)
    result_loc.delete("1.0", tk.END)
    result_loc.insert(tk.END, localization)

def on_save_goals():
    name = entry_name.get().strip()
    save_file(result_goals.get("1.0", tk.END), f"{name}_goals.gfx")

def on_save_shine():
    name = entry_name.get().strip()
    save_file(result_shine.get("1.0", tk.END), f"{name}_goals_shine.gfx")

def on_save_loc():
    mod_name = entry_mod.get().strip()
    tag = entry_tag.get().strip()
    name = entry_name.get().strip()
    save_file(result_loc.get("1.0", tk.END), f"{mod_name}_focus_{tag}_{name}_l_simp_chinese.yml")

root = tk.Tk()
root.title("国策树相关文件自动生成整合工具by@CzXieDdan——czxieddan.top")

tk.Label(root, text="本地化/国策树文件:").grid(row=0, column=0, sticky='e')
entry_loc = tk.Entry(root, width=40)
entry_loc.grid(row=0, column=1, sticky='w', columnspan=2)
btn_loc = tk.Button(root, text="读取本地化", command=on_load_localization)
btn_loc.grid(row=0, column=3, sticky='w')
btn_focus = tk.Button(root, text="读取国策树", command=on_load_focus_file)
btn_focus.grid(row=0, column=4, sticky='w')

tk.Label(root, text="MOD名称缩写:").grid(row=1, column=0, sticky='e')
entry_mod = tk.Entry(root)
entry_mod.grid(row=1, column=1, sticky='w')

tk.Label(root, text="文件编号前缀:").grid(row=2, column=0, sticky='e')
entry_name = tk.Entry(root)
entry_name.grid(row=2, column=1, sticky='w')

tk.Label(root, text="TAG (gfx文件夹名):").grid(row=3, column=0, sticky='e')
entry_tag = tk.Entry(root)
entry_tag.grid(row=3, column=1, sticky='w')

tk.Label(root, text="ID 列表 (自动/手动，每行一个，末尾加#可分隔):").grid(row=4, column=0, sticky='ne')
text_ids = tk.Text(root, height=10, width=40)
text_ids.grid(row=4, column=1, columnspan=4, sticky='w')

tk.Button(root, text="生成", command=on_generate).grid(row=5, column=1, sticky='w')

tk.Label(root, text="goals.gfx 预览:").grid(row=6, column=0, sticky='ne')
result_goals = tk.Text(root, height=10, width=60)
result_goals.grid(row=6, column=1, columnspan=4, sticky='w')
tk.Button(root, text="保存goals.gfx", command=on_save_goals).grid(row=7, column=1, sticky='w')

tk.Label(root, text="goals_shine.gfx 预览:").grid(row=8, column=0, sticky='ne')
result_shine = tk.Text(root, height=10, width=60)
result_shine.grid(row=8, column=1, columnspan=4, sticky='w')
tk.Button(root, text="保存goals_shine.gfx", command=on_save_shine).grid(row=9, column=1, sticky='w')

tk.Label(root, text="本地化yml预览:").grid(row=10, column=0, sticky='ne')
result_loc = tk.Text(root, height=14, width=60)
result_loc.grid(row=10, column=1, columnspan=4, sticky='w')
tk.Button(root, text="保存本地化yml", command=on_save_loc).grid(row=11, column=1, sticky='w')

root.mainloop()
