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

`content-source.md` 保存本次导入的原文快照；`site-content.json` 保存介绍、梦想、愿景、边界、第一届成员及分类介绍；`projects.json` 是项目记录的唯一数据来源。导入只读取原文，不修改 Obsidian 文件：

```sh
python3 scripts/import_content.py
npm run build
python3 scripts/check_catalog.py
```

导入器识别现有六件作品和 12 位第一届成员。增加作品时，先补齐源文档与导入器中的项目元数据，再导入；也可单独维护 `projects.json`，同时相应更新内容快照与检查。不得猜填作者、功能或未经确认的项目。

首页介绍心创组、呈现六件作品和第一届成员，并链接两个独立分类页：

| 页面 | 作品 | 设计者 |
| --- | --- | --- |
| `/sign-projects/` 核心创意 | 以手寻语 SignTrace | 涂增基 朱星烨 王宁静 黄庭逸 |
| 同上 | 分社手语词典 | 朱星烨 涂增基 |
| 同上 | 传情绘意-手语版 | 涂增基 |
| `/campus/` 其他作品 | 拼好课 | 涂增基 |
| 同上 | 北大知道 | 涂增基 |
| 同上 | 清华知道 | 涂增基 |

作品外链在新标签页打开；分类页在当前标签页打开。六件作品保留名称、用途介绍与设计者，关键信息不用悬停才能看到。成员区采用滚动缩放式连续陈列，不增加招新、联系方式或分社架构。

模板为 `templates/base.html`、`home.html`、`collection.html`。生成器先校验全部记录和模板，再更新三页；项目必填 `id`、`name`、`collection`、`category`、`description`、`url`，可选 `creator`、`icon`。空分类显示空状态。

## 交互与访问

- 原始浮雕场景随指针、滚动和页尾明暗变化；首屏先经过带 0–100 进度的加载层，再以模糊、位移和渐变透明显现文字。
- 顶部导航和左下入口使用参考站同样的大片泼墨反馈：自托管 SVG 噪声经过位移、模糊后从控件边缘扩散；手机点击会短暂揭开浮雕并平滑衰减。
- 第一届成员使用两列大字卡片连续陈列，进入视口时以快速缩放和模糊退场形成原站式总览节奏。
- 顶部导航与左下「查看全部作品」按钮共享参考站式大片泼墨 SVG 反馈；触屏保留可点击状态，并在按下时驱动浮雕揭示。
- 顶部只保留「关于心创组」「作品集」两个入口；作品集锚点按「核心创意」「其他作品」分组，并提供各自目录页。
- 手机采用低模浮雕与原生触控滚动；减少动态效果时保留完整正文和静态浮雕回退。页面离开释放场景资源。
- 页尾沿用原站的沉浸式收束：边界缩为低存在感暗色信息，最后一屏切换为纯黑，只保留居中的「以手予爱 ShouYuLove」。中英文统一使用 PSTimes / 本地中文衬线字体栈，字号和字重负责层级区分。
- 作品集采用连续滚动的紧凑项目卡片；每件作品使用本地透明 SVG logo 与文字说明，不依赖大幅照片或单独作品页。

动效参数、测量边界及参考的有意区别见 [设计与动效记录](docs/research/immersive-g/MOTION.md)。

## 素材

首页不再单独展示照片；背景使用本地浮雕模型、纹理与 Draco 解码器。六件作品使用本地透明 SVG logo；没有 AI 生成人物、外国人物封面或网站截图。全站中英文统一使用 PSTimes 参考字体与本地中文衬线回退，GSAP、Lenis、Three.js、参考站素材说明、字体和图标许可位于 `home-assets/licenses/`。

## 旧风格归档

本轮加载、泼墨与手机揭示版归档：

`主站版本归档/20260929-144410-加载泼墨复刻版/`

对应提交 `468a26e`，含完整 `site/`、逐文件 `SHA256.json`、恢复说明与同名 tar.gz；clone-website Skill 的原站行为审查位于 `output/immersive-research/clone-skill-audit-20260929/`。

本次更换前完整存档：

`主站版本归档/20260929-012636-Daylight双分类高清湖光版/`

含 `site/`、`SHA256.json`、`恢复说明.md`，另有同名 tar.gz。37 个源文件及编译产物已逐文件与归档、压缩包校验。旧提交 `015c6554c6838da6d9720270a0096e96f263e65e` 仍在 Git 历史中。归档保留旧版 Daylight 湖光动效、两类目录、高清封面与部署资料；可独立用 Python HTTP 服务打开。

## 发布

执行 `python3 scripts/package_site.py` 得到 `output/shouyulove-home-relief.zip`。只发布 `index.html`、`sign-projects/index.html`、`campus/index.html` 和 `home-assets/`；不发布源码笔记、研究复刻、归档或 node_modules。

部署到用户服务器。部署、校验与回退参见 [deploy/README.md](deploy/README.md)。不得部署到 chatgpt.site，三个既有子站保持独立。
