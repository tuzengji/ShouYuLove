# 以手予爱 ShouYuLove 主站

主站入口为 https://shouyulove.cn/，使用没有人物的北京大学未名湖畔高清实拍封面与滚动叙事，视觉参考 [Daylight](https://daylightcomputer.com/)。首页介绍北京大学爱心社手语分社心创组的工作与协作方式，并提供作品入口。右上角为「关于心创组」「手语作品」「燕园服务」三个入口；首页的两个作品分类使用橙色背景，各分类页面突出当前入口。

公开源码仓库：[tuzengji/ShouYuLove](https://github.com/tuzengji/ShouYuLove)。本仓库仅包含主站，三个子站分别维护。

## 本地预览

编译产物已经放在仓库中，直接启动即可，无需先安装 Node 依赖：

```sh
cd /Users/wishingcat/LovingHeart/ShouYuLove/以手予爱主站
python3 -m http.server 8028 --bind 127.0.0.1
```

打开 http://127.0.0.1:8028/ 。应通过 HTTP 预览，`file://` 下浏览器会限制模块和字体加载。

## 当前内容

- **手语作品**（`/sign-projects/`）：以手寻语、手语查询、传情绘意，保持原有顺序；传情绘意显示「创作者：涂增基」。
- **燕园服务**（`/campus/`）：拼好课，入口 https://www.pinhaoke.love/ ，提供北大课程检索、筛选、收藏与课表整理、导出，创作者依据其 README 署名为 Zengji Tu。

首页的快捷入口、横向展陈和目录均引导到这两个独立页面。分类链接在当前标签页打开，各作品在新标签页打开并保留目录。项目名称、用途介绍和已知创作者同时显示；未知作者不猜填。组织介绍只聚焦心创组及其工作与协作方式，不展示报名入口、负责人联系方式或分社架构。

心创组的工作与项目制协作依据本地 2026 秋季心创组介绍整理。未读取或发布骨干联络表、问卷答卷等个人资料，也未将规划中的项目标记为已经上线。介绍位于 `index.html` 的 `#about`，工作方式位于 `#teamwork`。介绍下方补充：「以手予爱 ShouYuLove 是我们心创组推出的作品系列名称，也是我们的愿景。」两段正文沿用同一层级的样式和滚动显现效果。

## 动效与交互

使用 GSAP ScrollTrigger 和 Lenis，依据原站公开浏览器实现与实际截图进行测量：

- 200svh 首屏停驻，同一张未名湖畔黄昏照片通过轻微暖光与蓝调过渡呈现晨光、夕照与夜色。桌面与手机均支持，向上滚动可逆向还原。
- 500svh 介绍，先显露「我们是心创组」标题，再显示归属与职责、作品系列名称与愿景两段正文，随后整体擦除。
- 桌面纵向滚动驱动横向项目展陈，间距 20vw；展示两个作品分类。
- 400svh 整屏纸面转场，暖色出现、缩小、透视倾斜、侧移；同一句介绍随之移动。纸面不再展示照片，鼠标可轻微改变纸面角度。
- 1024px 以下，项目展陈改为纵向。首屏两个分类入口、顶部导航和完整项目目录始终可直接使用。
- 首屏按实际视窗高度排版，不设超出小屏的固定最小高度；矮窗口缩紧标题与留白，手机横屏将首屏文字和入口并排显示。
- 系统减少动态效果、页尾「简洁浏览」、关闭 JavaScript 或动画加载失败时，显示完整的普通文档布局。
- 全站明暗主题、原生键盘链接、浏览器前进后退、项目深链接、目录搜索与分类。
- 大标题使用衬线字体；正文使用苹方优先的系统无衬线字体。展陈介绍桌面 20px、手机 18px，目录与工作方式介绍桌面 18px、手机 17px，采用 500 字重。
- 文案最多两层：简短标题与正文。首页、心创组与项目适度保留介绍；不添加第三层副标题、重复解释、状态标签和装饰小字。

逐段参数与视觉适配边界见 [MOTION.md](docs/research/daylight/MOTION.md)。以原站的动画机制和时序为依据，平板商品画面改成自然摄影、项目图标和纸面；没有将其商品 Canvas 帧和 WebGL 模型放入生产页面。

## 增加项目

仅修改 `projects.json`，然后执行：

```sh
python3 scripts/sync_projects.py
```

必填字段：`id`、`name`、`collection`、`category`、`description`、`url`。`collection` 只能为 `sign`（手语作品）或 `campus`（燕园服务）。`id` 使用小写英文、数字及连字符，不能重复；链接只接受 HTTP(S)。

可选字段为 `icon` 和 `creator`。`icon` 的 ID 来自 `home-assets/icons.svg`，省略时使用箭头；`creator` 是创作者姓名，填写时必须为非空字符串，会显示在所属分类的作品列表，未填写时不显示该行。`name` 作为标题，`description` 作为一段用途介绍；不另加 subtitle、headline 或 detail 等文案字段。分类只供需要时筛选，不重复显示在每条内容上。

生成器同步首页的分类快捷入口、分类展陈和分类目录，并从 `templates/collection.html` 生成 `sign-projects/index.html` 与 `campus/index.html`。单个分类项目大于 6 个时，搜索和用途筛选自动出现。新增项目不需要修改动画数量、滚动距离或 HTML 模板。所有项目均渲染为普通链接，关闭 JavaScript 仍然可用。

运行扩展与输入校验：

```sh
python3 scripts/check_catalog.py
```

测试在临时副本中增加 12 个项目，检查两个页面严格分流、创作者显示、HTML 转义、空目录与错误输入不覆盖三个已生成页面。

## 修改动画

```sh
npm ci
npm run build
```

`home-assets/main.js` 负责轻量交互与动画的渐进加载；`home-assets/motion.js` 是动画时间轴，`daylight-scene.js` 负责首屏 170 帧日光合成；`motion.bundle.js` 是 esbuild 生成的浏览器产物。GSAP、Lenis 和 esbuild 的版本锁定于 `package-lock.json`。修改动画后需重新构建。

## 旧版封存

全部归档位于当前主站目录内：

```text
主站版本归档/
  20260927-193023-单句文案版/
    site/           本次适度恢复标题与介绍之前的版本
    SHA256.json
    恢复说明.md
  20260927-172721-创意小屋版/
    site/           完整源文件、编译产物、原说明与验证资料
    SHA256.json     逐文件 SHA-256
    恢复说明.md
  20260927-172721-创意小屋版.tar.gz
  20260927-190145-湖光完整文案版/
    site/           单句文案与字号调整之前的版本
    SHA256.json
    恢复说明.md
  20260927-184148-Daylight草地版/
    site/           湖光、部组展示和项目顺序调整之前的版本
    SHA256.json     35 个文件的校验记录
    恢复说明.md
```

75 个文件已与改版前原文件及压缩包内容逐个校验。省略可重新安装的 node_modules 和浏览器缓存；保留锁文件，可用 npm ci 恢复依赖。归档源文件中的 room.bundle.js 可直接预览。

```sh
python3 -m http.server 8029 --bind 127.0.0.1 --directory 主站版本归档/20260927-172721-创意小屋版/site
```

## 部署

线上仅需要 `index.html`、`sign-projects/index.html`、`campus/index.html` 和 `home-assets/`。不要上传归档、output、docs、node_modules、源项目问卷或研究素材。

可以创建仅包含上述白名单文件的部署包：

```sh
python3 scripts/package_site.py
```

产物：`output/shouyulove-home-daylight.zip`。Nginx location 示例见 `deploy/nginx-home.locations.conf`，保留 `/signtrace/`、`/chuanqinghuiyi/`、`/dict` 原有配置。当前根主页已上线，服务位置、配置备份和后续更新流程见 [部署记录](deploy/README.md)。

## 研究与素材

- 用户提供的 [ai-website-cloner-template](https://github.com/JCodesMore/ai-website-cloner-template) 用作浏览器测量、样式提取、交互检查与复刻迭代的方法参考，未安装为本机技能。
- 本地结构研究稿：`output/daylight-study/index.html`，仅复刻选定页面结构，并非完整电商网站。
- 动效研究及参数：`docs/research/daylight/`。
- 当前三页截图前缀为 `output/playwright/collections-*`；此前导航与介绍截图前缀为 `output/playwright/portfolio-nav-*` 和 `heart-group-vision-*`，窗口适配检查为 `viewport-*`；此前两层文案为 `two-level-*`，单句版为 `plain-*`，湖光版为 `lake-*`，早期动效研究为 `daylight-*`。
- 页面仅在首屏保留一张照片：星外之神拍摄的北京大学未名湖畔黄昏，原图 **4080×3060**；桌面资源 3840×2880，手机裁切资源 1280×2277。没有人物，未使用生成图或扩图。图片采用 CC BY-SA 4.0，页尾与公开许可文件保留署名、来源和修改说明。旧人物素材保留于本地归档，不进入部署包。详见 `docs/research/daylight/ASSETS.md`。
- 项目展示不使用网站截图，不包含之前的双手捧心主图。
