# 作品集维护说明

## 当前状态与多入口规则（2026-11-27）

- **当前线上版本**：`20261127T095945Z-astra-home`（1,122 个运行文件、34 条页面路由、5 个相对链接、2 条外部跳转 `/where-to-study` 与 `/where-to-study/` → `https://39.96.206.228/`，共 `207,673,232` 字节）。
- **2026-11-27 起作品集与首页由 `scripts/build_home.py` 生成**：两页是二维手绘风的轻量页面，多入口作品在首页和作品集都直接渲染成按钮，不再依赖 `scripts/project_entries.js` 与三维场景。下文关于 `styles/portfolio.css`、作品集三维场景和首页替换脚本的说明只对旧版页面有效；构建顺序与新增作品的做法见 [主站维护入口](../AGENTS.md)。完整发布与运维记录见 [当前运维状态](operations-current.md)。
- **一个作品多个入口按钮**：绑定原稿的作品条目可在「地址：」之后追加两行或更多 `入口：[名称](地址)`。
  - 有入口行的作品在作品集 `/portfolio/` 里渲染为不可整卡点击的 `.portfolio-card`，每个入口是一个带小图标的按钮（`.portfolio-action`）；按钮取代简介显示在标题与设计者之间，沿用 `data-project` 属性计入作品集跳转统计；「心创组内部使用」分区全部卡片（接锅、手语分社统一通行证、心创云盘）左侧图标统一与右侧文字垂直居中对齐。
  - 首页 `/` 对应卡片由独立脚本 `scripts/project_entries.js`（线上 `/assets/project-entries.syl-v1-1-five-games.js`，样式 `styles/project-entries.css`，版本常量 `PROJECT_ENTRIES_VERSION`）在加载后做同样替换。
  - 原稿中的简介与「地址：」保留供作品详情页 `/projects/<id>/` 使用。每个入口的小图标须在 `scripts/build_content.py` 的 `ENTRY_ICONS` 登记，沿用 256px 画布与 13px 灰绿描边。目前「手语分社统一通行证」（通行证主页 `/auth/`、接入与配置中心 `/auth/dev`）、「炸飞机」（主持人端 `/bombplane/host/`、玩家端 `/bombplane/player/`）与「水果炸弹」（主持人端 `/fruitbomb/host/`、玩家端 `/fruitbomb/player/`）采用双按钮入口。

## 页面和内容入口

正式目录为 `/portfolio/`；`/projects`、`/projects/`、`/projects/index.html` 保留 308 跳转。各作品详情仍使用 `/projects/<id>/`，不要把详情地址一并改成目录跳转。

`scripts/build_content.py` 的 `portfolio_page` 生成正式 HTML，`styles/portfolio.css` 维护排版，`scripts/portfolio.js` 后台载入原生三维场景。作品名称、简介、设计者、链接、多入口按钮、分类顺序及鸣谢来自绑定 Markdown（`/Users/wishingcat/ObsidianNotes/AI Study/爱心社/心创组主站-以手予爱.md`），`content-source.md` 为公开副本。

作品集现有 25 个项目（7 个核心创意、11 个手语游戏、3 个心创组内部使用、4 个其他作品）：

| 分类 | 项目 | 正式入口 |
| --- | --- | --- |
| 核心创意 | 以手寻语 SignTrace | `/signtrace/` |
| 核心创意 | 分社手语词典 | `/dict` |
| 核心创意 | 小爱同学的物资小屋 | `/XiaoAi-Warm-Cabin/` |
| 核心创意 | 手语视听说 | `/shouyu-shitingshuo/` |
| 核心创意 | 手小语 | `/shouxiaoyu/` |
| 核心创意 | 2026 手语文化节 | `/2026-sign-language-cultural-festival/` |
| 核心创意 | 2026 手语分社骨干年终总结 | `/2026-year-end-summary/` |
| 手语游戏 | 骷髅牌 | `/skull/` |
| 手语游戏 | 完美一餐 | `/perfectmenu/` |
| 手语游戏 | 奶家麻将 | `/NaiMahjong/`（302 至 `http://39.96.206.228:8444/`） |
| 手语游戏 | 指间趣游 SignPlay | `/signplay/` |
| 手语游戏 | 飞手传书 | `/flyinghands/` |
| 手语游戏 | 传情会意-手语版 | `/chuanqinghuiyi/` |
| 手语游戏 | 炸飞机 | `/bombplane/`（主持人端 `/bombplane/host/`、玩家端 `/bombplane/player/`） |
| 手语游戏 | 水果炸弹 | `/fruitbomb/`（主持人端 `/fruitbomb/host/`、玩家端 `/fruitbomb/player/`） |
| 手语游戏 | 巴巴爸爸 | `/barbapapa/` |
| 手语游戏 | 行动代号 | `/codenames/` |
| 手语游戏 | 雪豹凶杀案 | `/snowleopard/` |
| 心创组内部使用 | 接锅 | `/catchpot/` |
| 心创组内部使用 | 手语分社统一通行证 | `/auth/`（通行证主页）、`/auth/dev`（接入与配置中心） |
| 心创组内部使用 | 心创云盘 | `/drive/` |
| 其他作品 | 去哪自习 | `/where-to-study/`（302 至 `https://39.96.206.228/`） |
| 其他作品 | 拼好课 | `https://pinhaoke.love` |
| 其他作品 | 北大知道 PKU Know | `https://pkuknow.cn` |
| 其他作品 | 清华知道 THU Know | `https://pkuknow.cn/thu` |

## 已确认的展示方式

顶部只保留「心创组作品集」与首页入口。核心创意、手语游戏和心创组内部使用优先展示，使用明显的分类标题；核心创意（7 项，作品集桌面端两列排布、奇数末项跨列）与手语游戏（11 项，作品集桌面端两列排布、奇数末项跨列）桌面均采用两列排布、手机单列，奇数末项跨列。主要类别保留设计者署名，手机署名按姓名换行。

其他作品紧凑置底，默认不显示设计者；需要单独显示设计者的条目（如「去哪自习」）通过原稿条目中的 `作品集署名：显示` 开启，原稿和其他页面中的署名继续保留。末尾居中显示 12px 小字「鸣谢所有心创组成员」，对应原稿「作品集页面／鸣谢」字段。

图标边缘沿用宽幅不规则渐隐，单入口卡片保留标题悬停的深绿色与 3px 位移（不添加穿过设计者文字的横线）；多入口卡片自身不可整卡点击，由内部按钮响应悬停与跳转。手机「添加到桌面」保留安全区间距与浏览器指引。

## 当前图标和字体

主站使用 [把爱递给你](../project-logos/20261012-主站-把爱递给你/README.md)：浅暖米色手掌、豆沙爱心与灰绿描边。34 条主站页面路由的标签页图标、Apple 触屏图标和作品集安装图标统一从该 SVG 生成，独立缓存版本为 `syl-v1-1-giving-heart`。

项目图标统一采用柔和彩色系列：基础项目使用 [柔和彩色套件](../project-logos/20261012-柔和彩色/README.md)（文化节保留原卡通人物 PNG，年终总结为「谢谢这一年」感谢章，传情会意为「心意小卡」），后续上线项目分别位于 `project-logos/20261015-signplay/`、`20261020-flyinghands/`、`20261110-quna-study/`、`20261113-shouyu-pass/`（含双按钮小图标 `pass-home.svg`、`pass-console.svg`）、`20261114-xinchuang-drive/`、`20261114-shouxiaoyu/`、`20261124-sign-games/`（含双端按钮小图标 `game-host.svg`、`game-player.svg`）、`20261125-skull/`、`20261125-perfectmenu/`、`20261125-naimahjong/`、`20261126-xiaoai-warm-cabin/`（小爱同学卡通形象去背透明 PNG）与 `20261127-shouyu-shitingshuo/`（柔和彩色视频台词与对话泡 SVG/PNG）。首页和作品集共用同一套图像。统一曲线版、卡通试稿、低饱和试稿和旧标识保留为历史材料，当前构建不从试稿选图。

中文继续使用狮尾四季春·加糖，英文标题为 PSTimes，英文正文及轻字重控件为 Helvetica Neue。首屏共用一份字体 CSS，后台场景复用已加载的字体定义，刷新或背景就绪时不切换字体。当前 `syl-v1-1-shitingshuo` 中文子集与双套 WebGL MSDF 图集完整覆盖 625 字（含「视」「听」「影」「台」「复」等全部正文用字），无临时补充字形。

| 构建字段 | 当前值 |
| --- | --- |
| `BRAND_VERSION`（主站图标） | `syl-v1-1-giving-heart` |
| `RUNTIME_VERSION`（图像） | `syl-v1-1-shitingshuo` |
| `FONT_VERSION`（中文 625 字） | `syl-v1-1-shitingshuo` |
| `MODULE_VERSION` | `syl-v1-1-shitingshuo` |
| `STYLE_VERSION` | `syl-v1-1-sign-games` |
| `BRIDGE_VERSION` / `PORTFOLIO_SCENE_VERSION` | `syl-v1-1-shitingshuo` |
| `PROJECT_ENTRIES_VERSION`（首页多入口脚本） | `syl-v1-1-five-games` |

## 加载和隐私规则

作品集的正式 HTML 先可读、可点击；首次绘制至少两秒后，后台加载完整的 Nuxt/WebGL 场景及原模型、鼠标跟随和流体交互。加载失败或关闭 JavaScript 时，正式目录仍可访问；场景不能覆盖列表、重置滚动或改变地址。作品集不初始化、不下载音乐。

三维网络资源通过共用队列限制为两路下载；页面隐藏后暂停新增请求，已开始的请求继续完成，返回后续载。原生解码器也走同一队列，具体接入与验证见 [后台资源加载](background-loading.md)。

首页、心创组和作品详情保留原生 0–100 加载界面。已移除的临时巨型文字页不恢复。首页只预载当前场景，其他场景按需加载；版本化公共资源缓存一年，HTML 和 payload 使用 no-cache。

访问统计在服务器后台按 HTML 页面响应自动覆盖主站和所有同域名子站（并采集 `/where-to-study/` 外部跳转与作品集点击 `portfolio_clicks`），按北京时间分天汇总；验证请求使用 `ShouYuLove-QA` 用户代理，避免计入访问量。查看与维护见 [后台统计说明](private-statistics.md)。子站账户、照片、会话和统计资料不进入主站运行白名单。

## 主要发布记录

运行白名单见 [runtime-manifest.json](../runtime-manifest.json)，发布与回滚流程遵循 [部署说明](../deploy/README.md)。

| 工作 | 仓库提交 | 主站发布目录名称 |
| --- | --- | --- |
| 九项目图文目录与年终总结 | `e685832` | `20261011T155351Z-astra-home` |
| 柔和彩色图标与「心意小卡」 | `57cede1`、`028e2c9` | `20261012T025514Z-astra-home` |
| 鸣谢、传情会意更名与「把爱递给你」主站标识 | `1eb470d`、`14770c0` | `20261012T142201Z-astra-home` |
| 指间趣游加入首页与作品集 | `4484dd6` | `20261014T162210Z-astra-home` |
| 作品集跳转统计与三维下载队列 | `e6b884e`、`e02b838` | `20261017T162339Z-astra-home` |
| CDN + 私有 OSS 加速上线 | `c85210a` | `20261018T084902Z-astra-home` |
| 飞手传书加入首页与作品集 | `c61c2fb` | `20261020T123649Z-astra-home` |
| 去哪自习接入与站内固定入口 | `53fc7fa`、`eb56f34` | `20261111T013217Z-astra-home` |
| 手语分社统一通行证接入主站与作品集 | `syl-v1-1-shouyu-pass` | `20261113T044411Z-astra-home` |
| 心创云盘接入主站与作品集 | `syl-v1-1-xinchuang-drive` | `20261114T051119Z-astra-home` |
| 手小语接入主站与作品集（第 3 行并列） | `135f6d4` | `20261114T123404Z-astra-home` |
| 手语分社统一通行证作品集与首页双入口按钮 + 内部图标居中 | `7e3f2c7`、`3cb077f`、`2590e43` | `20261116T055144Z-astra-home` |
| 首页与作品集新增「手语游戏」栏目（收录指间趣游、飞手传书、传情会意-手语版） | `e40d3e7` | `20261124T075334Z-astra-home` |
| 「手语游戏」接入炸飞机、水果炸弹、巴巴爸爸、行动代号、雪豹凶杀案（重建 607 字字体） | `3ba67d4` | `20261124T091501Z-astra-home` |
| 「手语游戏」首位接入「骷髅牌」（设计者黄庭逸，重建 615 字字体） | `a9bb48a` | `20261125T035923Z-astra-home` |
| 「手语游戏」接入「完美一餐」（设计者黄雨琦，重建 621 字字体） | `112071d` | `20261125T051617Z-astra-home` |
| 将「完美一餐」调至「手语游戏」第 2 位（与「骷髅牌」并列首行） | `44a57d5` | `20261125T052701Z-astra-home` |
| 润色精炼全部 10 款手语游戏单句简介（`syl-v1-1-games-copy`） | `2026-11-25` | `20261125T053315Z-astra-home` |
| 「手语游戏」第 3 位接入「奶家麻将」（`/NaiMahjong/`，重建 608 字字体） | `1474ed9` | `20261125T061159Z-astra-home` |
| 移除 `/games/` 中缀，「骷髅牌」「完美一餐」改用顶层路径 `/skull/`、`/perfectmenu/`（`syl-v1-1-top-routes`） | `4d7eea4` | `20261126T150007Z-astra-home` |
| 「核心创意」第 3 位接入「小爱同学的物资小屋」（`/XiaoAi-Warm-Cabin/`，重建 612 字字体） | `401eb09` | `20261126T152545Z-astra-home` |
| 「核心创意」第 4 位接入「手语视听说」（`/shouyu-shitingshuo/`，重建 625 字字体） | `2026-11-27` | `20261127T094624Z-astra-home` |

后续改文案先改绑定 Markdown；改图标同步首页、作品集及涉及的子站，并更新对应缓存版本；改排版或加载逻辑须在无头浏览器完成 1440／390／320px 及延迟／失败分支检查。
