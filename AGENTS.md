# 以手予爱主站维护

## 当前运行状态（2026-11-24）

- **当前线上版本**：`20261124T091501Z-astra-home`（上一版本 `20261124T075334Z-astra-home`，741 个运行文件、29 条页面路由、5 个相对链接、2 条外部跳转 `/where-to-study` 与 `/where-to-study/` → `https://39.96.206.228/`，共 `167,147,840` 字节）。完整变更脉络见 [当前运维状态](docs/operations-current.md)。
- **作品集规模与多入口卡片**：作品集共 20 个项目，分为四个栏目（5 个核心创意、8 个手语游戏、3 个心创组内部使用、4 个其他作品）。
  - 首页顺序为「核心创意 → 手语游戏 → 其他作品 → 心创组内部使用」；作品集 `/portfolio/` 顺序为「核心创意 → 手语游戏 → 心创组内部使用 → 其他作品」。「手语游戏」收录 8 项（指间趣游 SignPlay、飞手传书、传情会意-手语版、炸飞机、水果炸弹、巴巴爸爸、行动代号、雪豹凶杀案），桌面端 4 行两列平衡排布。
  - 「心创组内部使用」分区包含「接锅」「手语分社统一通行证」「心创云盘」，三张卡片左侧图标统一与文字垂直居中对齐。
  - **多按钮入口机制**：绑定原稿条目可在「地址：」后追加两行及以上 `入口：[名称](地址)`，并在 `scripts/build_content.py` 的 `ENTRY_ICONS` 登记小图标。作品集生成不可整卡点击的 `.portfolio-card`，由各 `.portfolio-action` 按钮取代简介展示在标题与署名之间（仍带 `data-project` 计入作品集点击统计）；首页由独立脚本 `scripts/project_entries.js`（线上 `/assets/project-entries.syl-v1-1-five-games.js`，样式 `styles/project-entries.css`，版本常量 `PROJECT_ENTRIES_VERSION`）在渲染后做同样替换；原稿简介保留供作品详情页使用。当前支持多按钮的项目为「手语分社统一通行证」（通行证主页 `/auth/`、接入与配置中心 `/auth/dev`）、「炸飞机」（主持人端 `/bombplane/host/`、玩家端 `/bombplane/player/`）与「水果炸弹」（主持人端 `/fruitbomb/host/`、玩家端 `/fruitbomb/player/`）。
- **当前资源版本**：
  - 主站品牌图标 `BRAND_VERSION = syl-v1-1-giving-heart`（`project-logos/20261012-主站-把爱递给你/shouyulove.svg`）；
  - 图像 `RUNTIME_VERSION`、字体 `FONT_VERSION`（中文完整覆盖 607 字，已移除先前「配」字临时补充字形）、运行模块 `MODULE_VERSION`、多入口脚本 `PROJECT_ENTRIES_VERSION`、数据桥 `BRIDGE_VERSION` 与作品集场景 `PORTFOLIO_SCENE_VERSION` 均为 `syl-v1-1-five-games`；
  - 首页定制样式 `STYLE_VERSION = syl-v1-1-sign-games`；
  - CDN 资源继续使用 `https://assets.shouyulove.cn/v/20261020-flyinghands/`（`cdn-manifest.json` 311 项），后续增量资源（`origin-asset-manifest.json` 368 项）由 ECS 直接提供。

## 服务器与基础设施边界

- **唯一维护入口**：`ssh shouyulove-aliyun` → `root@101.37.209.227`（ECS `i-bp1hi3u3w5p3vg4owfl0`）。**禁止**使用北大知道的 `yanyuan-calendar`（`121.43.143.226`）发布或维护以手予爱项目。
- **已退役兼容清理边界**：
  - 腾讯轻量服务器 `49.232.193.175` 已于 2026-10-28 重装为纯净 Ubuntu 22.04.5，旧 SignTrace `28018` 回源、旧年终总结 `28042` 会话分流及全部 `280xx` 迁移隧道均已移除，不得恢复任何腾讯旧机兼容配置。
  - 阿里云上的旧 PKUKnow vhost 已退役（HTTP 410、拒绝 TLS 握手、无代理），不得恢复旧反代；本站仍复用现有 SSH 身份、共用 ACME 账户和 `certbot.timer`，不得误删。
- **子站独立运行边界**：主站发布只管理 `/var/www/shouyulove-home`（版本目录 `/var/www/shouyulove-home-releases/`），不接管同机独立维护的子站：
  - 手小语：纯静态站 `/var/www/shouyulove-showcase`（`core: 核心创意/手小语/site/`，片段 `/etc/nginx/snippets/shouxiaoyu.conf`）；
  - 指间趣游：`/var/www/shouyulove-signplay` + `signplay-bank.service`（`8765`）；
  - 飞手传书：`/opt/flyinghands/current` + `flyinghands.service`（`8766`）；
  - 手语分社统一通行证：`/opt/shouyulove-auth/current` + `shouyulove-auth.service`（`8767`）；
  - 心创云盘：`/opt/shouyulove-drive/current` + `shouyulove-drive.service`（`8768`）+ `shouyulove-drive-fb.service`（`8769`），共享存储池 `/srv/drive`（`100 GB`）；
  - 以手寻语（`signtrace.service` `8018`）、传情会意（`shouyu-game.service` `8019`）、接锅（`jieguo.service` `8040`）、手语文化节、骨干年终总结（`8042`）均纳入 `system-shouyulove.slice`（共 11 个活跃单元）；
  - 分社手语词典 `/dict`：经本机 `18080/18081` 直连 CLab，配合 `shouyulove-dict-guard` 独立签名会话限流（见 [词典访问保护](docs/dictionary-campus-access.md)）。
- **CDN 与证书**：静态资源 CDN 与私有 OSS 流程见 [CDN 说明](docs/cdn-oss.md)。每次资源更新须分配新的 `/v/<版本>/`，先跑 `prepare_cdn.py`、上传并执行 `verify_cdn.py`，再发布 HTML。`assets.shouyulove.cn` 专用证书到期日为 `2027-01-16`，当前需手动续签与上传，不能当作已自动续期；根域与 `www` 证书（`/etc/shouyulove/tls/`）由 `certbot.timer` 自动续期。
- **私有访问与点击统计**：HTML 页面响应自动统计（同域全覆盖，无需登记路径名单，含 `/where-to-study/` 外部 302 入口与 `/drive/files/` 路径脱敏）及 `tuzengji.com` 隔离统计、`portfolio_clicks` 作品集跳转统计统一由 `shouyulove-stats.service` 采集，测试请求须带 `User-Agent: ShouYuLove-QA` 以免污染真实数据。详见 [后台统计说明](docs/private-statistics.md)。

## 构建、发布与日常维护规则

- 用中文交流；先看 Git 状态、README 与 [作品集维护说明](docs/portfolio-maintenance.md)。本机原工作树保留历史修改与删除，提交推送使用隔离克隆副本，避免误提交或清掉本机忽略资产。
- 项目采用 Astra/Nuxt、GSAP、WebGL 的已导出运行时；不要恢复已退出的旧 garden/esbuild 工程。
- **正文文本源**：以 `.content-source-path` 指向的 `/Users/wishingcat/ObsidianNotes/AI Study/爱心社/心创组主站-以手予爱.md` 为唯一正文源；修改文字、成员、作品介绍、署名、链接和 `入口：` 行时，先修改该原稿再构建或同步，`content-source.md` 为公开副本。「其他作品」默认隐藏作品集署名，单独开启署名的条目通过 `作品集署名：显示` 控制；核心创意与心创组内部使用保持显示署名。
- **运行白名单与缓存**：以 `runtime-manifest.json` 保存精确运行白名单，使用 `scripts/runtime_snapshot.py` 校验或导出，发布与同步均逐个核对文件 SHA-256 及 5 个相对符号链接（`assets`、`webgl`、`sounds`、`images`、`lotties`）。版本化公共资源使用一年 `immutable` 缓存（内容变化必须更换对应版本常量），HTML 与 payload 使用 `no-cache`。保留上一版 `immutable` 模块地址，防止已打开页面延迟请求 404。
- **仅修改说明文档时**：提交并推送经审查的文档，同步至服务器私有维护目录 `/opt/shouyulove-maintenance/`，核对线上运行清单未变；说明和验收记录不进入公共运行白名单，不重建或重启网站。
- **字体与加载体验**：
  - 首屏字体定义只保留在 `scripts/build_content.py` 生成的共用首屏字体 CSS 中，通过 `stable_font_rules` 清除重复定义；改动字体后检查冷加载、刷新和三维背景就绪前后的字体渲染及文字位置一致。新增中文用字须更新字体子集与 MSDF 图集并升级 `FONT_VERSION`。
  - 原生页面保持 0–100 加载界面（禁止恢复临时大字文字页）；作品集 `/portfolio/` 静态目录立即可读可点，首次绘制至少两秒后在后台加载完整三维场景且不下载音乐。三维网络下载共用两路并发名额，页面隐藏暂停新增请求、返回续载（见 [后台资源加载](docs/background-loading.md)）。
- **回归与验收**：页面改动须在无头浏览器检查桌面（1440px）、手机（390px）与窄屏（320px），结束时关闭新建浏览器上下文，不干扰用户窗口。导航回归使用 `tests/project_navigation.js`，手机「添加到桌面」（仅在 `/portfolio/` 显示）回归使用 `tests/home_shortcut.js`，场景回归使用 `tests/portfolio_scene.js`。
- **新项目联动要求**：在工作区部署任何新项目时，同一任务必须同步加入主站首页与作品集 `/portfolio/`，完成主站仓库推送、服务器部署及两处入口打开验收。研究稿、账户、会话、部署凭据与内部数据严禁进入公开仓库或静态目录。
