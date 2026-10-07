# 主站中文字体候选

现有 12 个对照项：在原 6 款基础上，新增 5 种字体与源云明体 Medium 字重。当前主站使用 09 狮尾四季春·加糖（简体版 Regular）；英文保持原版 PSTimes。完整 OTF/TTF、授权与来源均保存在各编号子文件夹。

## 如何挑选

直接打开服务器[字体对比页](https://shouyulove.cn/assets/font-preview-v1-1-2/index.html)，或从主站目录启动本地预览：

```sh
python3 serve.py --port 8041 --directory 字体候选
```

打开 http://127.0.0.1:8041/ 。可切换字体、点击“放大预览”并调整字号；第二屏原文连续左对齐，英文始终不变。告诉我编号或名称即可。

建议先看 **12 源云明体 Medium**（保留现有风格、笔画较厚）、**09 狮尾四季春·加糖**（简洁温润）、**07 源样明体**（传统而端正）。这些是本项目的视觉取向建议。

| 编号 | 字体 | 对比方向 | 版本与作者来源 |
| --- | --- | --- | --- |
| 01 | 原版思源宋体（Noto Serif） | 替换前主站的中文基准，规整、对比鲜明。 | [2.003](https://github.com/notofonts/noto-cjk/tree/main/Serif) |
| 02 | 朱雀仿宋 | 清秀舒展的仿宋，书卷气较强。 | [0.212](https://github.com/TrionesType/zhuque) |
| 03 | 霞鹜新致宋 | 传统宋体骨架，字面规整，适合阅读。 | [1.067](https://github.com/lxgw/LxgwNeoZhiSong) |
| 04 | 寒蝉锦书宋 | 在宋体结构中加入圆角，温润柔和。 | [1.700](https://github.com/Warren2060/ChillJinshuSong) |
| 05 | 源流明体 | 较修长、笔画末端细腻，带有铅字感。 | [2.100](https://github.com/ButTaiwan/genryu-font) |
| 06 | 源云明体 | 笔画交接圆润，有墨晕般的温暖质感。 | [2.100](https://github.com/ButTaiwan/genwan-font) |
| 07 | 源样明体 | 传统印刷明体，端正雅致，适合与原英文字体搭配。 | [2.100](https://github.com/ButTaiwan/genyo-font) |
| 08 | 一点明体 | 旧书铅字风格，横竖对比鲜明，适合大标题。 | [8.100](https://github.com/ichitenfont/I.Ming) |
| 09 | 狮尾四季春·加糖 | 简化宋体装饰，并加厚横笔，清新柔和。 | [1.061](https://github.com/max32002/swei-spring) |
| 10 | 霞鹜文楷 | 带手写气息的楷体候选，更亲切，适合公益叙述。 | [1.522](https://github.com/lxgw/LxgwWenKai) |
| 11 | 站酷小薇体 | 紧凑的宋楷风格，转折活泼，适合简短标题。 | [1.000](https://github.com/google/fonts) |
| 12 | 源云明体·Medium | 源云明体的较厚字重，可对照细笔画的清晰度。 | [2.100](https://github.com/ButTaiwan/genwan-font) |

## 文件与重建

`fonts.json` 保存固定版本及下载地址，`manifest.json` 保存完整字体 SHA-256、实际版本和文案字符覆盖结果。运行 `python3 字体候选/prepare_preview.py` 可重做预览字库与对比页。目前每款覆盖当前 Markdown 的 310 个非 ASCII 字符，原字体文件保持不变。

07–11 为新增字体，12 为现有源云明体的字重对照。10 霞鹜文楷是手写楷体风格；07、08、12 使用传统印刷字形，用于与现代宋体比较。

## 授权与应用

03 霞鹜新致宋、08 一点明体使用 IPA Font License 1.0，对比页使用未改动的原始 TTF，优先调用本机原始 IPA 字库；各卡片提供恢复原字库的指引。其余附 SIL OFL 1.1；中文 WOFF2 预览子集使用独立名称，完整原字体与版权信息保留。各卡片链接到作者来源和授权原文。

服务器仅发布预览所需字库与授权，不发布整个本地字体收藏。选定后再重建主站中文浏览器字体及 WebGL 图集，继续保留英文、网页结构和动效。
