# 当前版本验证（2026-09-29）

- 本地版本已完成 Immersive Garden 原始浮雕、双分类作品集与导航收缩；发布前入口为 https://shouyulove.cn/ ，分类页为 `/sign-projects/`、`/campus/`。
- 原 Daylight 风格37个已跟踪文件及压缩包逐字节校验通过，归档于 `主站版本归档/20260929-012636-Daylight双分类高清湖光版/`。
- Obsidian 源文档逐字导入，身份、品牌含义、梦想、完整愿景、工作/协作和边界未擅自改写；首页四项目、两目录分别3/1，分类名为「核心创意」「其他作品」。
- `npm ci`、`npm run build`、`scripts/check_catalog.py`、部署包白名单均通过。目录检查含扩展记录、HTML转义、空状态、非法输入不覆盖页面、新标签链接、无独立照片及源文案一致性。
- 桌面真实 Chromium 看到本地浮雕与作品卡片，390×844 手机首屏无横溢出；减少动态效果模式 `window.__garden.mode` 为 `reduced`、场景就绪、错误数组为空。
- 首页导航仅含「关于心创组」「作品集」，作品集锚点可滚到两组内容；目录页保留两组切换链接。未保留深色模式、简洁预览、作品集弹层或 secondary menu 场景。
- 本地 Chromium 请求的高/低质量浮雕模型及 Draco 文件均返回200，控制台错误与警告均为0。
- 29个公开文件的部署包校验通过；关键公网文件哈希一致，浮雕高/低模型与 Draco 资源响应头为 200，HTTP 主页、两个目录、SignTrace、词典（转/dict/entries）和游戏均 200。
- 配置部署前后 SHA-256 相同。只原子切换静态目录，nginx -t 通过；未 reload nginx、未重启后端。
- 当前发布：`/var/www/shouyulove-home-releases/20260929T033200Z-relief17`。上版 `/var/www/shouyulove-home-releases/20260929T032800Z-relief16` 保留可回退。
- 机器证据：`output/deployment/relief17-{preflight,request,online-checks,browser-checks}.json`；本地手机截图位于 `output/playwright/`。
- 参考首页单独复刻与风格改编分开验收；原站媒体/模型不会进入公开包。不以参考稿的几何对齐宣称品牌站逐像素一致，尚有差异在参考稿README与QA中注明。本轮未运行Lighthouse，不复用旧版分数。

---

# 历史版本验证（2026-09-28）

- 已上线：https://shouyulove.cn/；手语作品：https://shouyulove.cn/sign-projects/；燕园服务：https://shouyulove.cn/campus/。
- 唯一封面为星外之神拍摄的无人北大未名湖畔黄昏，原图 4080×3060，桌面 3840×2880，手机 1280×2277。网页脚注和公开文件保留 CC BY-SA 4.0 署名、来源及修改说明。
- 顶部为「关于心创组」「手语作品」「燕园服务」。首页突出两个分类，各分类页突出当前页，具有 `aria-current="page"`。
- 手语作品显示以手寻语、手语查询、传情绘意；燕园服务显示拼好课。名称、简介与已知创作者均在列表内，传情绘意为涂增基，拼好课按源项目署名为 Zengji Tu。
- `npm run build`、`scripts/check_catalog.py`、部署包白名单校验通过。检查涵盖两个分类严格分流、增加 12 条记录、HTML 转义、创作者、空目录和非法输入不覆盖已有三页。
- 桌面 1440×900、手机 320×568、横屏 568×320 检查通过。浅色、深色与减少动态效果模式可用。修复首页静态模式树影越出视窗的问题，检查无横向溢出，横屏标题与入口不重叠。
- 两个分类页保持普通文档布局，不加载首页动画。关闭 JavaScript 时项目仍是可点击的原生链接。
- 线上从首页点击进入两个分类页，并实际点击拼好课验证新标签页与原目录保留；无页面错误。
- 21 个公开文件与本地部署包 SHA-256 一致。HTTP 主页、两条分类路由的尾斜杠跳转、原有三个子站及拼好课均通过 GET 检查。
- 先检查最新配置并备份，再新增两个静态目录路由，通过 `nginx -t` 后 reload。父站点配置和三个子站代理不变，未重启后端服务。
- 当前证据：`output/deployment/collections13-{release,request,online-checks}.json`；截图 `output/playwright/collections-*.png`。发布与回退位置见 `deploy/README.md`。

# 历史验证（2026-09-27）

核验日期：2026-09-27。线上入口：https://shouyulove.cn/ 。站名为「以手予爱 ShouYuLove」。

## 项目入口新标签页

- 首屏快捷入口、项目展陈、项目目录共 9 个项目链接均使用 `target="_blank" rel="noopener"`，由目录生成器统一输出；页内导航仍留在当前页。
- 桌面 1440px 和手机 390px 实际点击三类入口，三个项目均在新标签页打开，原主页 URL 保持不变；测试打开的标签页已关闭。
- 构建与目录扩展检查通过；线上 HTML 与本地一致，主页及三个子站返回 200。验证记录见 `output/playwright/new-tabs-verification.json`、`output/deployment/new-tabs-online-checks.json`。

## 内容与排版

- 文案最多两层：简短标题加一段介绍，不叠加第三层副标题、状态标签或装饰小字。
- 组织介绍只围绕心创组，保留归属与方向，以及「我们做什么」「我们怎样协作」两段；分社架构、其他部组职责和分社长介绍均已移除。
- 大标题使用衬线字体；小字使用苹方优先的系统无衬线字体。项目展陈介绍常规桌面 20px、手机 18px；目录与工作方式介绍桌面 18px、手机 17px，字重 500。
- 手语查询的介绍包含正向和反向查询；三处项目顺序为以手寻语、手语查询、传情绘意。
- 无招新问卷、报名文案和个人姓名。顶部原架构入口已改为「工作方式」，指向 `#teamwork`。
- 湖光首图和早晚变化保留，纸面转场使用一个文案节点，移除了重复的品牌、口号和解释层。

## 本地检查

- `npm run build`、JavaScript 语法检查和 `scripts/check_catalog.py` 通过。
- 15 项临时扩展、转义、非法输入不覆盖已有文件的检查通过。
- HTML ID 唯一；锚点、图标、字体及本地资源有效。
- 320、390、768、1024、1440px 宽度无横向溢出。
- 手机与桌面的心创组工作方式已截图并查看，深色主题可读。
- 减少动态效果与关闭 JavaScript 时，三个项目和两段工作方式均可访问，无 Canvas 和动画布局残留。
- 工作方式初次深链接、刷新与导航点击定位正常；定位前同步 Lenis 尺寸，避免沿用动画初始化前的页面高度。
- 首屏取消固定最小高度；1440×800、1280×600、1024×600、390×667、375×600、320×568、320×480、844×390、568×320 均验证了标题和三个入口的视窗边界，无重叠或横向溢出。
- 矮窗口的心创组介绍和项目文字均在可见区域内；页面可滚至最底部，页尾控件完整可见。
- 横向项目容器改用 `overflow: clip`，修复原生片段定位改变容器横向滚动后与 GSAP 位移叠加的问题。1024×400、1440×1000 的项目深链接和下一项切换均已验证横、纵边界。
- 本轮结果为 `output/playwright/heart-group-verification.json`、`viewport-verification.json` 和 `horizontal-verification.json`，截图前缀为 `heart-group-*`、`viewport-*`。更早两层文案的验证保留于 `two-level-*`。

## 线上检查

- 此前 nginx 配置保持原样，本次只原子切换静态发布目录，没有重启应用服务。
- 公网根页面返回 200，与本地 HTML 逐字节一致，标题正确，缓存策略为 `no-cache`。
- 22 个线上公开文件与本地逐字节一致，包括 CSS、交互脚本、动画包、字体和自然图片；缓存版本为 `heart-group-8`。
- `/signtrace/`、`/dict`、`/chuanqinghuiyi/` 均返回 200，词典跳转到 `/dict/entries`。
- 线上真实浏览器检查桌面工作方式及 320×568 手机首屏通过，三个快捷入口完整可见，没有页面 JavaScript 错误或资源请求失败。
- 按用户补充的「项目切换与页面底部」问题，在独立浏览器检查 1440×700、1024×400、390×667、320×480、568×320：连续切换后三个项目的完整标题与正文均在可见区域，实际鼠标滚轮从首页可滚至页尾，底部控件完整可见；记录为 `output/deployment/viewport-live-wheel-final.json`。
- 线上晨光第 0 帧滚动到夜色第 169 帧，再回滚还原第 0 帧。
- 当前发布与回退位置见 `deploy/README.md`；机器记录见 `output/deployment/release.json`、`heart-group-online-checks.json`、`heart-group-browser-checks.json`。
- 线上截图为 `output/playwright/heart-group-live-*.png`。仅保留一个线上预览 Chrome 窗口，测试上下文已关闭。

## 归档与部署包

此前恢复两层文案之前的单句版本保存在 `主站版本归档/20260927-193023-单句文案版/`，完整文案版为 `主站版本归档/20260927-190145-湖光完整文案版/`。更早的草地版与创意小屋版同样位于主站目录内。本次更新保留远端 `20260927T121205Z-heart-group8` 发布目录用于回退。

当前部署包为 `output/shouyulove-home-daylight.zip`，只包含 `index.html` 和 `home-assets/`，没有归档、研究资料或个人数据。字体与图标许可证保留。

本轮未重跑 Lighthouse，旧性能结果仅对应旧版本。原站效果的适配边界及标题与介绍的时间轴变更见 `docs/research/daylight/MOTION.md`。
