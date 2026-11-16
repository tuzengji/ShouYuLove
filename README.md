# 以手予爱 ShouYuLove 主站

[以手予爱](https://shouyulove.cn/) 是北京大学学生爱心社手语分社心创组的介绍主页与作品导航，采用 Astra/Nuxt、GSAP 和 WebGL 运行层。

## 当前运行概览（2026-11-16）

- **维护主机与当前版本**：部署于阿里云 `101.37.209.227`（`ssh shouyulove-aliyun`），当前运行发布为 `20261116T055144Z-astra-home`（仓库提交 `2590e43`）。精确运行白名单保存在 [runtime-manifest.json](runtime-manifest.json)：共 **663 个运行文件、24 条页面路由、5 个相对资源链接、2 条外部跳转**（`/where-to-study` 与 `/where-to-study/` 302 至 `https://39.96.206.228/`），合计 `158,647,863` 字节。
- **作品规模（15 个项目）**：包含 8 个核心创意、3 个心创组内部使用与 4 个其他作品；公开文字与多入口配置读取绑定正文源（公开副本为 `content-source.md`）。
- **静态加速与源站分工**：大体积三维、图像与音频对象经私有 OSS 与 `assets.shouyulove.cn/v/20261020-flyinghands/`（`cdn-manifest.json` 311 项）分发；后续增量静态资源（`origin-asset-manifest.json` 300 项及 `project-entries.syl-v1-1-20261116.js`）、HTML 页面、外部跳转和私有访问统计由原 ECS 直接提供。腾讯旧机 `49.232.193.175` 已于 2026-10-28 重装退役，词典经本机直连 CLab。
- **说明文档索引**：[当前运维状态](docs/operations-current.md) 汇总服务器职责与近期全部上线变更；[作品集维护说明](docs/portfolio-maintenance.md) 记录目录排版、图标、字体与多入口按钮约定；[迁移与维护](迁移与维护.md) 说明服务与数据边界；[部署说明](deploy/README.md) 说明白名单发布与回滚流程；[验证记录](VALIDATION.md) 归档各版本验收证据。

## 近期重要更新

- **2026-11-16 手语分社统一通行证重构与双入口按钮**：「手语分社统一通行证」后端与前端统一更名并切换为暖色天光视觉（`/auth/` 版本 `20261116T042852Z`，`/auth/dev` 三视图控制台版本 `20261116T050830Z`）；主站首页 `/` 与作品集 `/portfolio/` 的对应卡片同步取消卡片内简介与整卡点击，改为「通行证主页」（`/auth/`）与「接入与配置中心」（`/auth/dev`）两个带同系列小图标的按钮，「心创组内部使用」三张卡片左侧图标统一与文字垂直居中对齐（主站版本 `20261116T055144Z-astra-home`）。
- **2026-11-14 手小语展示页上线**：「手小语」（涂增基设计）加入首页与作品集「核心创意」第 3 行（与「传情会意-手语版」并列），入口 `https://shouyulove.cn/shouxiaoyu/`；子站源码位于 `核心创意/手小语/`（`tuzengji/shouxiaoyu`），由 `/var/www/shouyulove-showcase`（`20261114T123437Z-shouxiaoyu`）托管 34 张深色手机端脱敏群聊实拍画册。
- **2026-11-14 心创云盘上线并扩至 100 GB**：「心创云盘」（涂增基设计）加入「心创组内部使用」分区，入口 `https://shouyulove.cn/drive/` 为一体化完整云盘工作台（零二级跳转，旧 `/drive/files/` 自动归并跳回 `/drive/`），底层挂载 100 GB 可在线扩容共享存储池 `/srv/drive`，接入统一通行证悬浮窗免跳转登录与三级权限校验。
- **2026-11-13 手语分社统一通行证上线**：独立单点登录基础设施 `shouyulove-auth`（`127.0.0.1:8767`）上线并接入主站与作品集，支持手机号短信自动注册、三级角色体系、同域 `auth_request` / `sdk.js` 悬浮窗与跨站 OAuth 2.0 + OIDC（PKCE / RS256 JWT）。
- **2026-11-10 / 11-11 去哪自习接入与站内固定入口**：新增其他作品「去哪自习」（王宁静设计，单独开启作品集署名），统一通过 `https://shouyulove.cn/where-to-study/` 302 跳转至 `https://39.96.206.228/` 并纳入私有跳转与访问统计。
- **2026-10-20 飞手传书上线**：新增核心创意「飞手传书」（王宁静设计，`https://shouyulove.cn/flyinghands/`），由独立 `flyinghands.service`（`8766`）承载，主站静态资源同步启用 CDN 前缀 `/v/20261020-flyinghands/`。
- **2026-10-15 指间趣游上线与阿里云切换**：新增核心创意「指间趣游 SignPlay」（伍家阳设计，`https://shouyulove.cn/signplay/`），全站流量与可写服务切换至阿里云 `shouyulove-aliyun`。

## 页面结构、图标与加载机制

作品集独立使用轻量 HTML，正式入口为 `/portfolio/`（旧 `/projects/` 308 跳转，详情页 `/projects/<id>/` 保留）。首屏直接展示图标、分类、名称、简介（或多入口按钮）与署名；首次绘制至少两秒后在后台加载完整原生三维场景，且不加载音乐。三维下载共用两路并发名额，页面隐藏后暂停新增下载、返回续载（见 [后台资源加载](docs/background-loading.md)）。首页只预载当前场景，心创组与页脚按需加载；版本化公共资源使用一年 `immutable` 缓存，HTML 和 payload 使用 `no-cache`。

主站标识采用 [把爱递给你](project-logos/20261012-主站-把爱递给你/README.md)（`syl-v1-1-giving-heart`）；15 个项目共用柔和彩色系列图标（`project-logos/20261012-柔和彩色/` 及各新增项目独立图标目录）。中文采用狮尾四季春·加糖（当前 `syl-v1-1-shouxiaoyu-v2` 子集覆盖 565 字，作品集与首页多入口脚本另临时内嵌「配」字补充字形），英文采用 PSTimes 与 Helvetica Neue。

## 验证、恢复与本地预览

只需 Python 3.9+ 和支持相对符号链接的文件系统，无需 npm、pip 或重新构建即可校验并预览当前完整站点：

```sh
python3 -B scripts/runtime_snapshot.py verify
python3 -B scripts/runtime_snapshot.py export output/runtime
python3 -B serve.py --directory output/runtime --port 8038
```

打开 `http://127.0.0.1:8038/`，结束时按 Ctrl-C。导出工具按清单复制文件和链接，校验每个文件并拒绝覆盖已有目录；校验独立导出目录可执行：

```sh
python3 -B scripts/runtime_snapshot.py verify --directory output/runtime --exact
```

当前版本已退出旧 esbuild/garden 工程，不要恢复旧 `package.json`、`home-assets/` 或已退出展示的页面。

## 源码维护与测试

- `scripts/content_source.py` 读取本机 `.content-source-path`（Git 忽略的一行绝对路径）绑定的正文源 MD，构建成功后自动同步仓库 `content-source.md` 副本。
- `scripts/build_content.py` 生成页面、多入口卡片（`ENTRY_ICONS` / `project_entries_script`）与运行资源；`scripts/project_entries.js` 与 `styles/project-entries.css` 维护首页多按钮入口；`styles/shouyulove-v1-1-jieguo.css` 与 `styles/portfolio.css` 维护主站与作品集样式；`scripts/optimize_runtime.py` 应用场景队列、手机纹理和图标遮罩补丁；`scripts/fast_bootstrap.js` 衔接 HTML 与原生视图。
- 完整内容重建除本仓库文件外，还依赖本机保留的 `output/deployment/shouyulove-content-v1/v0-backup.json` 对应 V0 归档、当前字体源与图集、`music/` 音频、`output/deployment/shouyulove-fast-20261009/mobile-textures/`（Khronos KTX-Software 4.4.2）及 `msdfgen` v1.13。当前本机缺失部分历史字体构建目录时，按 [当前运维状态](docs/operations-current.md) 在已校验运行包副本上增量更新。

源码回归测试依赖 Python 3.13 与系统 Cairo（macOS Homebrew 位于 `/opt/homebrew/lib`）：

```sh
python3 -m pip install -r requirements-build.txt
DYLD_LIBRARY_PATH=/opt/homebrew/lib python3 -B -m unittest discover -s tests -v
```

浏览器回归脚本包括 `tests/project_navigation.js`（首页与作品集站内导航、返回及前进后退）、`tests/home_shortcut.js`（作品集手机右下角「添加到桌面」及浏览器安装指引）与 `tests/portfolio_scene.js`（作品集三维背景后置加载）。私有访问与点击统计维护见 [后台统计说明](docs/private-statistics.md)，第三方许可保留在 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
