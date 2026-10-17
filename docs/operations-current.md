# 当前运维状态与记录索引

最近核对：2026-10-17，北京时间。当前项目与备份状态见 [服务器清理与运行项目记录](server-cleanup-20261017.md)。下文 10 月 15 日的迁移交接和历史快照继续保留，后续变化以上述新记录为准。

2026-10-17 清理 43 项闲置 Docker 构建缓存，以及与完整迁移包一致的 `stage-candidate/apps`、`stage-candidate/state` 解压副本，实测释放 4,135,342,080 字节，磁盘占用从 36% 降至 33%。原始迁移包、最终增量、回滚版本、PKUKnow 迁移快照、受保护历史资源和人大最终归档保留。

当前有七个本机网站后台服务，包含新增的 `signplay-bank`；主站与作品集由 Nginx 提供静态内容。词典当前使用本机 `18080/18081` 的 CLab 通道，视频优先从 `/var/lib/shouyu/videos/` 提供；`zhuxingye` 的故障切换监控、告警服务和定时检查已运行。本轮保留这些数据、服务和旧兼容隧道。

## 三台服务器的职责

| 服务器 | 当前职责 | 维护入口 |
| --- | --- | --- |
| 阿里云 `101.37.209.227` | 以手予爱主站、同域子项目和全站私有统计 | `ssh shouyulove-aliyun` |
| 阿里云 `121.43.143.226` | 已迁出的 PKUKnow 与公众号服务，由其项目独立维护 | `ssh yanyuan-calendar` |
| 腾讯云 `49.232.193.175` | 词典转接与备用、旧地址/会话/任务兼容，以及燕园图寻、时间秘书 | `ssh ubuntu@49.232.193.175` |

以手予爱目标 ECS 为杭州 `i-bp1hi3u3w5p3vg4owfl0`，公网带宽保持 5 Mbps。本轮只迁移 `shouyulove.cn` 下的项目，拼好课不在迁移范围内；主站仍保留北大知道、清华知道和拼好课的外链。

## 部署协作账号

2026-10-15 按用户最终确认，在阿里云 `101.37.209.227` 创建 `zhuxingye`，授予完整、免密码的 sudo 权限。登录命令为 `ssh zhuxingye@101.37.209.227`，项目目录为 `/home/zhuxingye/projects`，登录后可用 `sudo -i` 进入管理员 shell。

登录沿用旧腾讯同名账号最近使用的 SSH 公钥；未复制其 CLab 和其他设备公钥。账号密码锁定，服务器继续关闭密码登录。sudo 规则位于 `/etc/sudoers.d/90-zhuxingye`，仅 root 可写。新增账号未改动原 SSH/Nginx 配置、现有发布链接或服务进程。

已检查目录与公钥文件权限、`visudo -c`、`sshd -t`，并以该用户执行 `sudo -n id -u` 得到 `0`；SSH 公钥探测确认服务器接受已配置的公钥。实际签名登录需账号持有人使用自己的私钥完成，维护过程未索取私钥。

后续修改共用 Nginx 时继续使用 `/run/lock/nginx-deploy.lock`，先验证配置再 reload。账号配置与验收记录在本机 `output/deployment/zhuxingye-account-20261015/`，服务器回执为 `/var/backups/shouyulove-migration/20261015/zhuxingye-account-result.json`；本次维护说明同步至 `/opt/shouyulove-maintenance/20261015-zhuxingye-account/`。

## 迁移交接时的发布与服务（2026-10-15）

主站 `/var/www/shouyulove-home` 指向 `20261014T162210Z-astra-home`，SignPlay `/var/www/shouyulove-signplay` 指向 `20261015T020134Z-signplay`。主站清单为 **255 个文件、19 条页面路由、5 个相对链接、111,756,084 字节**，作品集共 **10 个项目**：六个核心创意、一个内部工具、三个其他作品。

图像、模块、字体和数据桥均为 `syl-v1-1-signplay`；主站品牌图标仍为 `syl-v1-1-giving-heart`。中文子集和图集覆盖 511 字，字体源在 `output/deployment/signplay-20261015/font-source/`。SignPlay 图标源在 `project-logos/20261015-signplay/`，其他已选图标继续沿用原素材。

新机 `signtrace`、`shouyu-game`、`jieguo`、`sign-language-festival`、`sign-year-end-summary`、`shouyulove-stats` 六个服务均为 `active`、`enabled`。五个动态应用的 current 均指向各自 `releases/20261015-aliyun-candidate`；这是已经接管正式流量的版本名，不是仍待发布的候选。代码、状态和服务对应表见 [迁移与维护](../迁移与维护.md)。

六服务仍使用 `system-shouyulove.slice`：CPUQuota 200%、CPUWeight 20、MemoryHigh 2G、MemoryMax 3G；SignTrace 保留两检索 worker 和四核亲和性。PKUKnow 迁出不自动改变这些参数。本次只更新说明，没有调大资源、重建网页或重启服务。

## 迁移、统计和证书

- 2026-10-15 15:51:40–41，根域与 www 解析切到新 ECS；两台权威 DNS 均核对通过。最终数据同步约 24 秒，临时 gate 排队和错误均为 0。gate 已退出，当前 unit 为 `inactive`，Nginx 直连新机服务。
- 旧统计的 1,528 次页面访问一次导入，固定去重密钥保留；新机持续接收新访问。源端采集器已停止并禁用，不能重新开启造成重复统计。统计范围、查看命令见 [后台统计说明](private-statistics.md)。
- 迁移验收共 190 项最终通过；其中一项首次 TLS 连接失败，独立复验两次均通过，原始结果保留。1440px 桌面和 390px 手机的首页、作品集已验证，完整 WebGL、延后场景和导航保持。
- 新证书覆盖根域和 www，有效至 2027-01-13。Certbot webroot、专属 hook、timer 及仅本域的续期 dry-run 均通过；后续运维命令见 [阿里云配置说明](../deploy/aliyun/README.md)。

## 腾讯中转交接记录（2026-10-15）

下列端口均只监听阿里云回环地址，流量经同一条 SSH 反向隧道进入腾讯旧机：

| 阿里云端口 | 用途 | 当前处理 |
| --- | --- | --- |
| `28080` | 词典动态页面/API，经旧机 `18082` 复用原主备 upstream | 仍被引用；保留 |
| `28081` | 词典视频和 BBS | 仍被引用；保留 |
| `28018` | 旧 SignTrace job 和原页面令牌兼容 | 仍被引用；退役前核对旧任务 |
| `28042` | 年终总结旧进程内存会话 | 仍被引用；新登录始终到阿里云 |
| `28019`、`28040`、`28041` | 迁移时的游戏、接锅、文化节旧服务入口 | 已无本站 Nginx 引用，gate 已停；转发条目尚未移除 |

年终总结旧会话最长 12 小时；以 15:51 完成全站切换为保守起点，最早在 **2026-10-16 03:51 后**再核对退役条件。时间到达不等于自动删除兼容路由。本次没有执行隧道收缩、旧进程停机或 CLab 直连。

闲置端口和词典共用隧道，不能为关闭三个闲置端口而停整条 relay。词典应用、主要数据库、视频和 BBS 仍在 CLab；取得其已授权管理入口后才能把新 ECS 改成直接转接。

腾讯旧机还保存词典备用工程约 **5.50 GB**，其中 data 约 **3.82 GB**。备用数据库不是 CLab 的实时副本，未来退役要先核对故障期间写入。监测、定时检查和告警服务属于词典维护账户的 **用户级 systemd**，用 ubuntu 或系统级 `systemctl` 查询不到不能判定它们已停止。

旧机公网 80/443/8018 仍转发新机。`shouyulove-legacy-8018.service` 的停止动作会撤销端口重定向，不能单独停用后让旧查询进程重新接受公开写入。

## 腾讯旧机的其他内容

| 项目或资料 | 2026-10-15 核查结果 |
| --- | --- |
| 燕园图寻 `yanxun-pku` | 仍运行并开机启用；回环 8920，经 Nginx HTTP 默认站点提供服务 |
| 时间秘书 `wecom-assistant` | 仍运行并开机启用；回环 8790，经默认站点的 relay 片段转发；备份、每日计划、每分钟提醒 timer 仍启用 |
| 旧助手进程 | 另有 8792 监听，未见 Nginx 引用；未在本次停用 |
| `puciology` | 服务已停止并禁用，工程保留 |
| 原游戏、接锅、文化节、独立统计 | 四服务已停止并禁用，代码和私有数据保留 |
| 主站历史发布与备份 | 11 个发布目录约 1.13 GB，主站备份约 3.90 GB |
| SignTrace 旧工程与迁移导出 | 工程约 755 MB，导出包约 429 MB；原查询档案、词典和研究资料保留 |

腾讯磁盘现场显示 40G、已用 22G、使用率 58%。以上目录大小为当日盘点值，不代表可删除容量。词典、燕园图寻和时间秘书仍有实际依赖，不能把旧机整体当作已闲置的备份机。

## PKUKnow 迁出后的边界

北大知道线程报告已清理 `101.37.209.227` 上的指定旧版本、历史库、重复图片及缓存，净释放约 20.16 GB；仍保留当天快照、独有历史资源和最后回退版本。本线程随后只读核实磁盘使用率为 27%，六个以手予爱服务保持运行。

已核实 `/etc/nginx/conf.d/yanyuan-calendar.conf` 仅保留退役响应：HTTP 410、拒绝 TLS 握手、没有 `proxy_pass`。它已不承担到 PKUKnow 新机的转发，后续不要恢复旧代理或旧 PKU/公众号任务。PKUKnow 的当前部署和清理记录由其仓库维护，本仓库不复制其数据库和原始资料。

两个共享依赖仍服务于以手予爱：`shouyulove-aliyun` 使用的现有 SSH 身份，以及新站证书复用的 ACME 账户。清理其他项目时不能删除对应授权、整个 `/etc/letsencrypt/accounts/` 或停用全局 `certbot.timer`。本站活跃证书在 `/etc/shouyulove/tls/`，独立 renewal 配置为 `/etc/letsencrypt/renewal/shouyulove.cn.conf`。

## 仓库与证据索引

以下为迁移维护提交，各远端 main 已回读确认；之后的文档提交以 Git 历史为准。

| 仓库 | 迁移提交 |
| --- | --- |
| ShouYuLove | `d6915f4ec97f7b376dad89e436f1bdfd833aff6f` |
| SignMate | `ce26dd94ce4f0e6d6846dfee325727ef3bac530a` |
| jieguo | `85c53401d6ac3da8deffa21a3a6b206916da9335` |
| Sign-Language-Cultura-Festival | `005f04b1f99e8925d766d0ada2e0de0e22a17fc8` |
| sign-club-year-end-recap-2026 | `4b126ff2b81184a25358c5c5a8f0ef18ba29a2cf` |
| ShouYu-game / SignPlay | `fc846b3ac001707834a8f4dfa1ee66bf139a4a51` |

本机记录在主站 `output/deployment/` 下：

- `shouyulove-aliyun-migration-20261015/`：`migration-result.json`、`verify-final.json`、`final-cutover-events.jsonl`、`source-final-cleanup.json`、`certificate-verification.json`、`repository-publish-results.json` 和浏览器截图。首次失败与复验分开保留。
- `shouyulove-docs-refresh-20261015/`：本次状态核查、文档备份、差异、哈希及推送/服务器同步结果。历史执行 JSON 不回写成新的结果。

新机原迁移资料在 `/var/backups/shouyulove-migration/20261015/`；58 个已核对的维护文件在 `/opt/shouyulove-maintenance/20261015-aliyun-migration/`。SignTrace 三个管理员脚本经 current/scripts 链接到该私有目录，仅 root 可读。不要清理仍被这个链接引用的维护包。

本次说明发布至独立目录 `/opt/shouyulove-maintenance/20261015-docs-refresh/`，旧包继续保留。说明、现场状态、密钥、会话和备份不进入网站静态白名单；部署完成与 Git 提交号记录在对应私有发布结果中。
