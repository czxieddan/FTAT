<div align="center">
<!-- Title: -->
  <a href="https://github.com/czxieddan/">
    <img src="https://i.imgur.com/h1Kllvh.png" height="200">
  </a>
  <h1>FTAT - <a href="https://github.com/czxieddan/">CzXieDdan</a></h1>
<p><strong>HOI4 Focus Tree Asset Tool</strong><br>
快速通过国策文件生成图标注册文件和本地化文件，支持简体中文、繁体中文、English 三语界面。</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/License-APERIP-ff3a68?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/github/stars/czxieddan/FTAT?style=for-the-badge&color=ffd700" alt="Stars">
  <img src="https://img.shields.io/badge/Platform-Windows%20|%20Linux-lightgrey?style=for-the-badge" alt="Platform">
  <img src="https://img.shields.io/badge/UI-CustomTkinter-00A3E0?style=for-the-badge" alt="UI">
  <a href="https://github.com/czxieddan/FTAT/releases/download/v1.0.0/FTAT.exe">
    <img src="https://img.shields.io/badge/下载最新版-蓝色?style=for-the-badge&logo=python&logoColor=white&color=0a84ff" alt="Download">
  </a>
</p>

</div>

## 主要功能

- **拖拽支持**  
  支持国策文件直接拖入窗口。

- **直观预览**  
  
  - 实时修改模板热载同步  
  - 输出内容预览分区展示  

- **一键导出 HOI4 标准结构**  
  **保存至MOD**自动在选定模组根目录创建（默认）：
  
  ```
  DEFAULT_PATH_GOALS = "interface/{MOD}/icons/goals/{TAG}/{TAG}_{PROJECT}.gfx"                  → 图标GFX
  DEFAULT_PATH_SHINE = "interface/{MOD}/icons/goals/{TAG}/{TAG}_{PROJECT}_shine.gfx"            → 光效GFX
  DEFAULT_PATH_LOC = "localisation/{LANG}/focus/{TAG}/{MOD}_focus_{TAG}_{PROJECT}_l_{LANG}.yml" → 本地化
  ```

路径可在预设中自由设定。

- **智能导出路径管理**  
  
  - 选择模组根目录（持久记忆）  
  
  - 首次导出可自动使用程序目录或手动选择  
  
  - 实时显示当前导出路径

- **简洁风格UI**  
  基于 CustomTkinter，全系统主题适配，圆角、简洁、现代感十足。

- **完整三语界面**  
  English | 简体中文 | 繁体中文，切换即时生效。智能记忆，下次启动无需再选。

- **完整本地化语言支持**  
  葡萄牙语 (巴西) | 英语 | 法语 | 德语 | 日语 | 韩语 | 波兰语 | 俄语 | 简体中文 | 西班牙语，切换即时生效。智能记忆，下次启动无需再选。

- **预设模板保存读取**  
  
  - 组内合作统一格式
  
  - 符合您的个人习惯
  
  每次打开无需再写，多组工作快速切换。
  您可以在模板中自由加入以下元素：
  
  ```
  {ID}      → 该国策的id
  {ICON}    → 图标GFX
  {TAG}     → 该国策所供使用的tag
  {MOD}     → MOD的缩写
  {PROJECT} → 国策树的编号等
  ```

- **智能提取**  
  
  - 多图标国策支持，一个图标多国策也能生成！（文件名为`{ID}_num.png`)
  
  - 智能提取`{TAG}`和`{PROJECT}`，节省工作时间
  
  - 任意图标使用，完全解绑图标GFX与国策ID，但文件名仍能与图标关联

- **最新版本自动验证**  
  启动静默自检最新版本，新版更新时一键点击即可获取，自动覆盖旧版即时自启动使用。

## 截图展示

<div align="center">
<img src="https://i.imgur.com/lCF1uKx.png?text=主界面+（英文）" alt="主界面（English）" width="48%">
<img src="https://i.imgur.com/4Da48Un.png?text=主界面+（繁体中文）" alt="主界面（繁体中文）" width="48%">
</div>
<br>
<div align="center">
<img src="https://i.imgur.com/9p0gDOG.png?text=光效GFX" alt="光效GFX" width="96%">
</div>
<br>
<div align="center">
<img src="https://i.imgur.com/B22pJVL.png?text=图标GFX" alt="图标GFX" width="48%">
<img src="https://i.imgur.com/ZziOgmK.png?text=主界面+（繁体中文）" alt="主界面（繁体中文）" width="48%">
</div>

> 以上截图均出自v1.0.0，欢迎下载体验！

## 快速开始

```bash
pip install customtkinter requests
python main.py
```

欢迎 ⭐ Star 与 Fork，您的支持是持续更新的动力！

## 特别鸣谢

<div align="center">
        <a class="link-item" title="霜泽图书馆" target="_blank" rel="noopener" href="https://github.com/Paradox-Developer-Foundation/QIUQI-LIBRARY"><img src="https://i.imgur.com/Hjp7UBm.png" height="360"></a>
        <p>霜泽图书馆 &#124; <i>HOI4</i> Modder社区</p>
        <p>&#160;</p>
        <p><a class="YEZI-QQ" title="3268514224" target="_blank" rel="noopener" href="https://ti.qq.com/open_qq/index2.html?url=mqqapi%3a%2f%2fuserprofile%2ffriend_profile_card%3fsrc_type%3dweb%26version%3d1.0%26source%3d2%26uin%3d3268514224"><i>YEZI</i></a> 技术支持</p>
        <p><em>(以上排名均不分先后。)</em></p>
</div>

## AI 生成内容披露

使用AI工具协助制作部分内容。












