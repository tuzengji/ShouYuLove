# 以手予爱 ShouYuLove 主站

北京大学爱心社手语分社心创组的作品与介绍。公开入口 https://shouyulove.cn/ ，源码仓库 [tuzengji/ShouYuLove](https://github.com/tuzengji/ShouYuLove)。原生 HTML、CSS、JavaScript；使用现有 GSAP、Lenis 与 esbuild，采用 Immersive Garden 参考站的浮雕渲染器与本地模型。

新版参考 [Immersive Garden](https://immersive-g.com/) 的灰色石膏空间、十二列排版、错落展陈、指针流场和明暗过渡。参考首页的独立复刻保存在本地 `output/immersive-clone/`，原工作室图片、模型、视频、字体与音频仅用于该研究稿，不放入公开主站。

## 预览与构建

仓库包含构建产物，直接预览无需安装依赖：

```sh
python3 -m http.server 8028 --bind 127.0.0.1
```

打开 http://127.0.0.1:8028/ 。修改代码后：

```sh
npm ci
npm run build
python3 scripts/check_catalog.py
python3 scripts/package_site.py
```

构建更新 `home-assets/garden.bundle.js` 与 `reference-relief.bundle.js`。装饰场景故障时正文仍可阅读；不需要服务端 JavaScript。

## 内容来源

公开内容以用户整理的 Obsidian 文档为依据：

`/Users/wishingcat/ObsidianNotes/AI Study/❄️进行中/心创组主站-以手予爱.md`

`content-source.md` 保存本次导入的原文快照；`site-content.json` 保存介绍、梦想、愿景、协作、边界及分类介绍；`projects.json` 是项目记录的唯一数据来源。导入只读取原文，不修改 Obsidian 文件：

```sh
python3 scripts/import_content.py
npm run build
python3 scripts/check_catalog.py
```

导入器识别现有四件作品。增加作品时，先补齐源文档与导入器中的项目元数据，再导入；也可单独维护 `projects.json`，同时相应更新内容快照与检查。不得猜填作者、功能或未经确认的项目。

首页介绍心创组、呈现四件作品，并链接两个独立分类页：

| 页面 | 作品 | 设计者 |
| --- | --- | --- |
| `/sign-projects/` 核心创意 | 以手寻语 SignTrace | 涂增基 朱星烨 王宁静 黄庭逸 |
| 同上 | 分社手语词典 | 朱星烨 涂增基 |
| 同上 | 传情绘意-手语版 | 涂增基 |
| `/campus/` 其他作品 | 拼好课 | 涂增基 |

作品外链在新标签页打开；分类页在当前标签页打开。四件作品保留名称、用途介绍与设计者，关键信息不用悬停才能看到。只介绍心创组工作与协作，不增加招新、联系方式或分社架构。

模板为 `templates/base.html`、`home.html`、`collection.html`。生成器先校验全部记录和模板，再更新三页；项目必填 `id`、`name`、`collection`、`category`、`description`、`url`，可选 `creator`、`icon`。空分类显示空状态。

## 交互与访问

- 原始浮雕场景随指针、滚动和页尾明暗变化；作品卡片保留轻微视差、悬停液态形变和文字显现。
- 顶部只保留「关于心创组」「作品集」两个入口；作品集锚点按「核心创意」「其他作品」分组，并提供各自目录页。
- 手机采用低模浮雕与原生触控滚动；减少动态效果时保留完整正文和静态浮雕回退。页面离开释放场景资源。

动效参数、测量边界及参考的有意区别见 [设计与动效记录](docs/research/immersive-g/MOTION.md)。

## 素材

首页不再单独展示照片；背景使用本地浮雕模型、纹理与 Draco 解码器。四件作品的海报为文字与几何排版；没有 AI 生成人物、外国人物封面或网站截图。标题字体是 Noto Serif SC 的本地 OFL 子集；正文为系统无衬线字体。GSAP、Lenis、Three.js、参考站素材说明、字体和图标许可位于 `home-assets/licenses/`。

## 旧风格归档

本次更换前完整存档：

`主站版本归档/20260929-012636-Daylight双分类高清湖光版/`

含 `site/`、`SHA256.json`、`恢复说明.md`，另有同名 tar.gz。37 个源文件及编译产物已逐文件与归档、压缩包校验。旧提交 `015c6554c6838da6d9720270a0096e96f263e65e` 仍在 Git 历史中。归档保留旧版 Daylight 湖光动效、两类目录、高清封面与部署资料；可独立用 Python HTTP 服务打开。

## 发布

执行 `python3 scripts/package_site.py` 得到 `output/shouyulove-home-relief.zip`。只发布 `index.html`、`sign-projects/index.html`、`campus/index.html` 和 `home-assets/`；不发布源码笔记、研究复刻、归档或 node_modules。

部署到用户服务器。部署、校验与回退参见 [deploy/README.md](deploy/README.md)。不得部署到 chatgpt.site，三个既有子站保持独立。
