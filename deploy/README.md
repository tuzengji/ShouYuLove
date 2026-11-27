# 主站运行白名单与发布约定

## 当前发布基线（2026-11-27）

- **当前线上版本**：`20261127T095945Z-astra-home`（上一版本 `20261127T095304Z-astra-home`），共 **1,122 个运行文件、34 条页面路由、5 个相对链接、2 条外部跳转**（`/where-to-study` 与 `/where-to-study/` → `https://39.96.206.228/`），总计 `207,673,232` 字节。
- **本轮变更范围**：首页 `/` 与作品集 `/portfolio/` 整体换成由 `scripts/build_home.py --site` 生成的二维手绘风页面（各一个 HTML 文件），新增 `/assets/next-*` 下的字体子集与 25 个图标，Nginx 路由片段与其余 1,090 个文件未变；随后按用户要求把十条较长的作品简介改成一句短话（`20261127T095945Z-astra-home`，文案变化后重新生成 2 个字体子集）；发布前必须最后运行一次 `build_home.py --site`，否则旧版首页和作品集会被重新发布。上一轮变更：在「核心创意」第 4 位接入「手语视听说」（`https://shouyulove.cn/shouyu-shitingshuo/`，设计者李昌昊），按以手予爱家族风格设计柔和彩色视频台词与对话泡图标（`project-logos/20261127-shouyu-shitingshuo/`，同步补齐子站标签页与桌面图标），完整重建覆盖 625 字的中文字体与双套 WebGL MSDF 图集（`syl-v1-1-shitingshuo`），保留全部旧版不可变资源。详见 [当前运维状态](../docs/operations-current.md)。
- **静态资源与子站隔离**：
  - 既有大体积三维与媒体资源经私有 OSS 与 CDN `https://assets.shouyulove.cn/v/20261020-flyinghands/`（`cdn-manifest.json` 311 项）提供；后续增量静态资源（`origin-asset-manifest.json` 739 项）由 ECS 提供。CDN 发布与证书手动续签说明见 [CDN 维护说明](../docs/cdn-oss.md)。
  - 主站发布目录固定为 `/var/www/shouyulove-home`（指向 `/var/www/shouyulove-home-releases/<版本>`），与同机独立维护的手小语（`/var/www/shouyulove-showcase`）、指间趣游（`/var/www/shouyulove-signplay`）、飞手传书（`/opt/flyinghands/current`）、手语分社统一通行证（`/opt/shouyulove-auth/current`）、心创云盘（`/opt/shouyulove-drive/current`）、以手寻语、传情会意、接锅、文化节、年终总结及拼好课严格隔离，互不混用静态目录。

## 发布与回滚规范

1. **维护主机**：统一使用 `ssh shouyulove-aliyun`（`root@101.37.209.227`，ECS `i-bp1hi3u3w5p3vg4owfl0`），严禁使用 `yanyuan-calendar`（北大知道主机 `121.43.143.226`）。腾讯旧机 `49.232.193.175` 过渡路由已于 2026-10-28 退役，不得恢复任何旧机回源或转发配置。
2. **运行白名单导出与校验**：根目录 `runtime-manifest.json` 是唯一公开文件清单。使用 `python3 -B scripts/runtime_snapshot.py verify` 校验工作目录，或使用 `python3 -B scripts/runtime_snapshot.py export output/runtime` 导出纯白名单运行包；严禁将本地工作树、说明文档、研究资料或私有记录整体上传到 `/var/www` 或 OSS。
3. **缓存与版本常量约束**：版本化公共资源采用一年 `immutable` 缓存；任何已发布静态资源内容变化时，必须同步升级对应的 `MODULE_VERSION`、`RUNTIME_VERSION`、`FONT_VERSION`、`BRIDGE_VERSION` 或 `PROJECT_ENTRIES_VERSION`，严禁在旧 `immutable` URL 下原地替换字节。HTML 与页面 payload 维持 `no-cache`。
4. **原子发布与锁机制**：
   - `publish_astra.py` 内部自动获取 `/run/lock/nginx-deploy.lock`，完成逐文件 SHA-256 校验、发布前状态绑定、备份（`/etc/nginx/backups/`）、切换 `/var/www/shouyulove-home`、`nginx -t` 及平滑重载；调用 `publish_astra.py`（或统计安装器、各子站发布器）时**不要**在外层重复持同一把锁。仅在手工修改共享 Nginx 时由操作者显式持锁。
   - `publish_astra.py` 的路由探针自动携带 `Accept: text/html` 与 `User-Agent: ShouYuLove-QA`，既满足词典会话守卫首页导航初始化条件，又不会污染私有访问统计；还会等待 Nginx 重载后新跳转规则（`deploy/project-redirects.json` 与 `deploy/nginx-home.locations.conf` 须保持同步）就绪，失败自动按发布前状态回滚。
   - `deploy/nginx-home.locations.conf` 仅为主站路由片段，不能直接覆盖整台服务器的共享虚拟主机配置（参考快照见 [阿里云维护配置](aliyun/README.md)）。
5. **仅更新维护说明时**：提交并推送经过审查的 Markdown 文档（使用隔离克隆副本，保留本机主工作树历史修改），将文档及哈希同步至服务器私有维护目录 `/opt/shouyulove-maintenance/<日期-主题>/`，核对线上运行白名单未变；不重新构建、不切换网站版本、不重启业务服务。

## 近期主站版本演进索引

| 日期 | 主站发布版本 | 文件 / 路由 / 规模 | 核心变更 |
| --- | --- | --- | --- |
| 2026-11-27 | `20261127T095945Z-astra-home` | 1,122 文件 / 34 路由 / `207,673,232` B | 十条较长的作品简介改成一句短话（奶家麻将保持原文），首页与作品集随之重建，新增 2 个字体子集 |
| 2026-11-27 | `20261127T095304Z-astra-home` | 1,120 文件 / 34 路由 / `207,466,306` B | 首页与作品集整体换成二维手绘风的轻量页面（`scripts/build_home.py`），新增 3 个字体与 25 个图标（`/assets/next-*`），其余文件与路由不变 |
| 2026-11-27 | `20261127T094624Z-astra-home` | 1,092 文件 / 34 路由 / `206,849,407` B | 「核心创意」第 4 位接入「手语视听说」（`/shouyu-shitingshuo/`，设计者李昌昊），设计柔和彩色图标并同步子站 favicon，重建 625 字中文字体与 MSDF 图集（`syl-v1-1-shitingshuo`） |
| 2026-11-26 | `20261126T152545Z-astra-home` | 1,021 文件 / 33 路由 / `198,789,310` B | 「核心创意」第 3 位接入「小爱同学的物资小屋」（`/XiaoAi-Warm-Cabin/`，设计者黄庭逸），重建 612 字中文字体与 MSDF 图集（`syl-v1-1-xiaoai-cabin`） |
| 2026-11-26 | `20261126T150007Z-astra-home` | 951 文件 / 32 路由 / `190,830,502` B | 移除 `/games/` 中缀，主站「骷髅牌」「完美一餐」改为顶层路径 `/skull/`、`/perfectmenu/`（`syl-v1-1-top-routes`） |
| 2026-11-25 | `20261125T061159Z-astra-home` | 949 文件 / 32 路由 / `190,665,793` B | 「手语游戏」第 3 位接入「奶家麻将」（`/NaiMahjong/`，设计者王宁静），重建 608 字中文字体与 MSDF 图集（`syl-v1-1-naimahjong`） |
| 2026-11-25 | `20261125T053315Z-astra-home` | 880 文件 / 31 路由 / `182,903,784` B | 润色精炼全部 10 款手语游戏单句简介，升级数据桥与场景至 `syl-v1-1-games-copy` |
| 2026-11-25 | `20261125T052701Z-astra-home` | 878 文件 / 31 路由 / `182,796,703` B | 将「完美一餐」调至「手语游戏」第 2 位（与「骷髅牌」并列首行），升级数据桥与场景至 `syl-v1-1-perfectmenu-v2` |
| 2026-11-25 | `20261125T051617Z-astra-home` | 876 文件 / 31 路由 / `182,631,025` B | 「手语游戏」接入「完美一餐」（`/games/perfectmenu/`，设计者黄雨琦），重建 621 字中文字体与 MSDF 图集 |
| 2026-11-25 | `20261125T035923Z-astra-home` | 808 文件 / 30 路由 / `174,829,536` B | 「手语游戏」首位接入「骷髅牌」（`/games/skull/`，设计者黄庭逸），重建 615 字中文字体与 MSDF 图集 |
| 2026-11-24 | `20261124T091501Z-astra-home` | 741 文件 / 29 路由 / `167,147,840` B | 「手语游戏」接入炸飞机、水果炸弹、巴巴爸爸、行动代号、雪豹凶杀案五款游戏，重建 607 字中文字体与 MSDF 图集 |
| 2026-11-24 | `20261124T075334Z-astra-home` | 666 文件 / 24 路由 / `158,764,324` B | 首页与作品集在「核心创意」下方新增「手语游戏」栏目（收录指间趣游、飞手传书、传情会意-手语版） |
| 2026-11-16 | `20261116T055144Z-astra-home` | 663 文件 / 24 路由 / `158,647,863` B | 作品集与首页「手语分社统一通行证」同步改为双入口按钮，「心创组内部使用」图标垂直居中 |
| 2026-11-14 | `20261114T123404Z-astra-home` | 662 文件 / 24 路由 / `158,632,740` B | 「手小语」接入首页与作品集核心创意第 3 行（与传情会意并列，共 15 个项目） |
| 2026-11-14 | `20261114T051119Z-astra-home` | 538 文件 / 23 路由 / `144,466,376` B | 「心创云盘」（`/drive/`）接入首页与作品集内部使用分区（共 14 个项目） |
| 2026-11-13 | `20261113T044411Z-astra-home` | 477 文件 / 22 路由 / `137,472,614` B | 「手语分社统一通行证」接入首页与作品集内部使用分区（共 13 个项目） |
| 2026-11-11 | `20261111T013217Z-astra-home` | 415 文件 / 21 路由 / `128,810,103` B | 「去哪自习」改为站内固定入口 `/where-to-study/` 302 跳转（共 12 个项目） |
| 2026-10-20 | `20261020T123649Z-astra-home` | 354 文件 / 20 路由 / `121,884,115` B | 「飞手传书」（`/flyinghands/`）上线并启用 CDN 前缀 `/v/20261020-flyinghands/` |
| 2026-10-18 | `20261018T084902Z-astra-home` | 296 文件 / 19 路由 / `115,101,198` B | 静态资源接入 `assets.shouyulove.cn` CDN + 私有 OSS，保留三维两路下载队列 |
| 2026-10-14 | `20261014T162210Z-astra-home` | 255 文件 / 19 路由 / `111,756,084` B | 「指间趣游 SignPlay」（`/signplay/`）上线，次日完成阿里云流量切换 |

2026-10-10 至 10-12 期间关于轻量作品集、私有后台统计、原生加载界面、字体稳定化与柔和彩色图标的早期单步发布记录归档于 [验证记录](../VALIDATION.md) 与 [当前运维状态](../docs/operations-current.md)。
