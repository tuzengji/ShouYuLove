# 主站部署记录

2026-09-29，Obsidian 新内容、第一届成员缩放总览、项目透明 logo、统一衬线排版、加载进度、文字渐变入场与大片按钮泼墨反馈已上线 https://shouyulove.cn/ 。公开源码仓库为 [tuzengji/ShouYuLove](https://github.com/tuzengji/ShouYuLove)。原风格完整源文件、编译产物与旧部署说明另有本地归档和Git历史。

## 当前部署与回退点

- 主机：`ubuntu@49.232.193.175`。
- 公开符号链接：`/var/www/shouyulove-home`。
- 当前发布：`/var/www/shouyulove-home-releases/20260929T081857Z-mobile-serif-v2`。
- 上版：`/var/www/shouyulove-home-releases/20260929T081234Z-mobile-serif`。
- 本次配置及旧指向备份：`/etc/nginx/backups/shouyulove-home-20260929T081857Z-mobile-serif-v2`。
- 配置：`/etc/nginx/sites-available/shouyulove` 与 `/etc/nginx/snippets/shouyulove-home.conf`。
- 本次两个配置文件逐字节保持不变，仅原子切换静态文件符号链接。没有reload nginx或重启任何后端应用。
- 共享资源版本：`garden-22`。改共享CSS、JS或字体时更新模板、CSS字体及动态模块入口中的版本。

## 发布流程

1. 阅读当前线上配置和发布指向，检查源文案、执行 `npm run build` 与 `python3 scripts/check_catalog.py`，通过桌面/手机/减少动画检查。
2. `python3 scripts/package_site.py` 生成 `output/shouyulove-home-relief.zip`。只允许3页HTML及 `home-assets/`；本版37个文件、12,191,860字节，包含本地中文衬线子集、六个透明项目 logo、单页成员总览、加载进度、手机揭示和大片按钮泼墨反馈。
3. 创建唯一发布目录并校验ZIP、每个提取文件与权限，保留最新配置及旧发布指向备份。仅在旧指向、旧HTML和配置哈希仍匹配时，原子替换公开符号链接。
4. 三个主站页面做有时限的内容就绪检查；失败则恢复旧符号链接。本次配置不变，静态内容更新不需要reload。若后续确需改nginx，备份只能放 `/etc/nginx/backups/`，验证 `nginx -t` 后再reload。
5. 公网逐文件校验，并验证根入口、两目录、三个子站及真实浏览器的加载/链接。不得发布研究复刻、原工作室素材、源笔记、归档、node_modules或子站数据。

`/signtrace/`、`/chuanqinghuiyi/`、`/dict` 始终属于各自应用，不随主页发布。仅部署用户服务器或本地预览，不能使用chatgpt.site。

## 回退

当前和上版共用同一套nginx路由。先确认线上仍指向上述当前发布，再创建指向上版的临时符号链接，用 `os.replace` 原子替换 `/var/www/shouyulove-home`。保留失败版本文件供调查，不重启三个子站。若未来修改过nginx，需同时审查相应备份；不要把本次“无需改配置”的结论套到未来发布。

本地旧风格存档位于 `主站版本归档/20260929-012636-Daylight双分类高清湖光版/`，含 `site/`、`SHA256.json`、`恢复说明.md` 与同名tar.gz。37个文件已校验。

## 验证证据

- `output/deployment/mobile-serif-v2-request.json` 与服务器返回的 `release.json`：本版上线前状态、发布白名单和原子切换结果；公网37个文件哈希已复核，大型浮雕模型采用延长超时的顺序校验。
- `output/deployment/mobile-serif-v2-online-checks.json`：本版37个公网文件哈希、六条入口状态和移动端交互断言。
- 本地浏览器审查见 `output/immersive-research/clone-skill-audit-20260929/`；线上浏览器已核对 1440 桌面、390 手机、加载进度、泼墨 hover 和触控揭示。
- `output/immersive-rebuild-qa/live-*.png`：线上实际截图；本次浏览器复核覆盖 1440×900 桌面与 390×844 手机。
- 一次性发布脚本 `output/deployment/publish_garden.py` 含状态漂移检查、解压校验、配置不变断言及失败回退；重用前必须重新生成最新请求，不直接重跑本次请求。

两目录按3个核心创意项目+3个其他作品分流。六件作品、设计者与12位成员来自最新Obsidian文档；两条新增项目因原文未提供单独简介，卡片使用「心创组成员开发的校园服务工具。」作为明确的栏目级短说明。首页不再单独展示照片；浮雕模型与透明 SVG logo 均随主站白名单发布。原站的 Lottie/sprite 文件没有直接进入公开包，泼墨效果由自托管 SVG 噪声滤镜实现。
