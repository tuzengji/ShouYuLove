# 当前运维状态与记录索引

## 2026-10-23 DeepSeek 主用和备用凭据

SignTrace、北大知道 / 清华知道、公众号文章处理、海王求职、Poetalent-v2、HAICA 和时间秘书已更新主用凭据，并加入备用凭据。模型继续使用官方 `deepseek-flash`。HAICA 与时间秘书旧 Key 已失效，按所有者确认使用 SignTrace 的有效旧 Key 备用；其余服务器服务保留各自有效旧 Key。真实主用调用和模拟主用被拒绝后的备用调用均已核验。

HAICA 保留线上 V2.1、现有静态页面、账号和历史数据。部署、测试和回滚边界见 [本次记录](deepseek-key-failover-20261023.md)。本节替代下方 2026-10-20 记录中的当前密钥状态，历史记录保留。

## 2026-10-21 wishingcat 完整管理员与 Docker 权限

按用户追加要求，`wishingcat` 现有完整的免密码 sudo 权限：`wishingcat ALL=(ALL:ALL) NOPASSWD: ALL`，规则位于 `/etc/sudoers.d/90-wishingcat`，属主 root、权限 0440。执行 `sudo -i` 可进入 root 登录 shell；无需再次输入账号密码。

该账号已加入 `docker` 组，可直接管理 Docker。已有 SSH 会话需要退出后重新登录，才能取得新增组权限。实际以密码新建 SSH 会话后，`sudo -n -i id -u` 返回 0，直接执行 `docker info`、`docker ps` 均成功；原有 root 密钥登录也通过。

本次只追加该账号的 sudo 规则与 Docker 组成员资格。SSH 配置、各账号登录密码、其他组成员，以及十一个网站与 Docker 服务的 PID 和运行状态保持。没有重启 Docker 或网站服务。

服务器回执位于 `/var/backups/shouyulove-maintenance/wishingcat-admin-20261021/20261021T023359Z/`；非秘密维护记录位于 `/opt/shouyulove-maintenance/20261021-wishingcat-admin/`。撤销本次追加权限时，移除该 sudoers 片段并验证 `visudo -c`，再撤销账号的 Docker 组成员资格；账号原有 sudo 组权限和 SSH 登录入口仍保留。

## 2026-10-21 站点所有者密码登录账号（首次开通）

按用户确认新增 `wishingcat` 管理员账号，可在其他电脑执行 `ssh wishingcat@101.37.209.227`，端口为 22。账号加入现有 `sudo` 组，执行 `sudo -i` 时使用该账号自己的密码；工作目录为 `/home/wishingcat/projects`。

新增 `/etc/ssh/sshd_config.d/90-wishingcat-password.conf`，通过 `Match User wishingcat` 仅为新账号开启密码登录。45 个原有账号的有效 SSH 配置逐一比对一致，原有 SSH 文件、公钥文件和账号密码状态保持。没有修改 `root` 或 `zhuxingye` 的登录方式。

密码认证登录、需密码的 sudo 提权、原有 root 密钥重新登录均已通过；`sshd -t` 和 `visudo -c` 通过。仅重载 SSH，十个既有网站相关服务的 PID 与运行状态未变，首页与作品集返回 200，主站发布仍为 `20261020T123649Z-astra-home`。

凭据仅私下交付，不进入仓库或网页。服务器验收回执位于 `/var/backups/shouyulove-maintenance/wishingcat-account-20261021/20261021T022241Z/`；非秘密说明同步至 `/opt/shouyulove-maintenance/20261021-wishingcat-account/`。撤销此入口时先移除该账号专用 SSH 片段、验证并重载 SSH，再锁定该账号及撤销其 sudo 组成员资格；保留既有账号和工作数据。

## 2026-10-20 飞手传书上线

新增核心创意「飞手传书」，设计者为王宁静，正式地址为 https://shouyulove.cn/flyinghands/ 。首页、作品集和项目详情共用手掌送出纸飞机的彩色图标。正文先更新绑定 MD，再同步构建快照；原稿没有的作品集鸣谢不再额外生成。

主站发布为 `20261020T123649Z-astra-home`，运行白名单 354 个文件、20 条页面路由、5 个相对链接，共 121,884,115 字节，作品集共 11 个项目。CDN 前缀为 `https://assets.shouyulove.cn/v/20261020-flyinghands/`，311 个对象已通过逐项哈希、大小、CORS、缓存和脚本类型检查。原站保留上一版资源，旧页面的延后请求仍可使用。

图片、字体、模块和数据桥版本为 `syl-v1-1-flyinghands`，主站品牌图标版本保持。中文覆盖 539 字，超出原 512 字图集容量，字体图集改为随字符数扩展，并检查全部字形都在纹理范围内。构建素材保存在本机 `output/deployment/flyinghands-20261020/font-source/`。

飞手传书由独立 `flyinghands.service` 提供服务，运行在 `127.0.0.1:8766`，使用独立 Node.js 24.22.0；代码在 `/opt/flyinghands/current`，数据库在 `/var/lib/flyinghands/materials.sqlite`。按用户要求保留公开共建功能，不增加账号或管理口令。子站维护规则见其 `deploy/README.md`。

主站回滚目录为 `20261018T084902Z-astra-home`。本次发布证据在本机 `output/deployment/flyinghands-20261020/` 和服务器私有目录 `/opt/shouyulove-maintenance/20261020-flyinghands/`；备份、数据库和验证记录不放入网站目录。

## 2026-10-20 DeepSeek 配置与密钥轮换

核对作品集十个项目后，当前在线使用 DeepSeek 的项目为 SignTrace、北大知道和清华知道。两校共用的网站后台与独立公众号处理服务分别持有私有凭据；三处服务器配置已替换为本次用户提供的新密钥，均通过官方鉴权检查，并确认可用模型为 `deepseek-flash`。SignTrace 本机私有配置同步更新。

SignTrace 当前发布为 `20261020-deepseek-flash-53b7808`，理解、改写和精排均使用 `https://api.deepseek.com/v1` 的 `deepseek-flash`。两校的摘要、分类、活动提取、翻译、学科与日期复核沿用已部署的官方 Flash 调用，不启用其他供应商回退，也不重新处理历史数据。

本轮只原子替换私有凭据，没有重启业务服务或切换代码发布。SignTrace 每次调用读取配置；两校后台任务启动时读取对应密钥文件。三个服务账号均能读取新凭据，官方模型列表检查返回 200；两套校园后台各两项请求路由回归通过，主站、SignTrace、北大和清华首页正常返回 200。没有发起收费生成或批量评测。

其他项目的核对结果：传情会意、指间趣游、接锅、文化节和年终总结未发现在线模型调用；拼好课网站不调用 DeepSeek，历史翻译脚本保持停用；词典当前配置为 OpenRouter `openai/gpt-5.5`，不属于本次 DeepSeek 凭据轮换范围。主站页面本身不持有模型密钥。

旧凭据备份只留服务器私有维护备份目录；本机备份在仓库外的私有状态目录。密钥、备份及鉴权回执不进入 Git 或公开静态资源。非秘密说明同步至服务器私有维护目录。

## 2026-10-18 CDN 与 OSS 发布

主站发布为 `20261018T084902Z-astra-home`，296 文件、19 路由、5 个链接、115,101,198 字节。255 个公开静态资源经私有 OSS 与 `assets.shouyulove.cn/v/20261018-1/` 提供；根域 DNS、页面统计和子项目运行方式保持。100 GB / 一年流量包已购买 14 元，OSS 按量计费；专用 HTTPS 证书有效至 2027-01-16，当前需要手动续签。

正式手机首页本轮冷加载约 6.8 秒，作品集约 0.60 秒可读、5.68 秒背景完成。50 个同出口下载会话共 3,550 请求全部 200、约 13.58–15.65 秒；这不是 50 台实体手机的渲染测试。第一次 ECS 压测出现读取超时并停止，原记录保留。配置、费用口径、验证条件、后续发布和回滚见 [CDN 维护说明](cdn-oss.md)。8 个后台服务 PID 和 24 份 Nginx 配置哈希保持。

最近核对：2026-10-18，北京时间。当前项目与备份状态见 [服务器清理与运行项目记录](server-cleanup-20261017.md)。下文 10 月 15 日的迁移交接和历史快照继续保留，后续变化以上述新记录为准。

## 2026-10-18 主站并发压测

首页单人首次进入主场景约 17.7 秒，两人约 29.8–36.7 秒，三人约 39.4–55.7 秒；两人复用缓存刷新约 3.4 秒。作品集五人首次同时打开，目录约 1.1–3.3 秒就绪，完整背景约 39.4–53.0 秒。公网下载总速度没有随人数增长，主机 CPU 和内存仍有余量，当前瓶颈主要在资源传输。回环首页 HTML 已测 200 并发全部成功；这不代表 200 人完整冷加载的体验。方法、停止条件和证据见 [压测记录](capacity-20261018.md)。本次未修改运行版本、配置或服务。

## 2026-10-18 后台资源下载

主站发布为 `20261017T162339Z-astra-home`：296 文件、19 页面路由、5 个链接、115,058,644 字节，其中 39 个文件保留上一版模块地址供已打开页面使用。三维下载并发为 2，隐藏后暂停新增请求，回来续载；原生场景和作品集音乐规则保留。词典现有缩略图及近屏加载已核查，本轮未改词典工作树。实现和验证边界见 [后台资源加载](background-loading.md)。

296 个运行文件校验和 19 条页面路由通过；8 个后台服务 PID 与发布前一致，24 份 Nginx 配置哈希保持。首次发布校验缺少 `Accept: text/html`，被词典会话保护按直接资源请求拒绝，发布器自动回退；补齐正常网页请求头后重新发布成功，未放宽防爬规则。回滚版本为 `20261017T024553Z-astra-home`。现场回执在 `/var/backups/shouyulove-maintenance/resource-loading-20261018/20261017T162339Z-astra-home/`，本机记录在 `output/deployment/resource-loading-20261018/`。

## 2026-10-17 清理与统计记录

2026-10-17 清理 43 项闲置 Docker 构建缓存，以及与完整迁移包一致的 `stage-candidate/apps`、`stage-candidate/state` 解压副本，实测释放 4,135,342,080 字节，磁盘占用从 36% 降至 33%。原始迁移包、最终增量、回滚版本、PKUKnow 迁移快照、受保护历史资源和人大最终归档保留。

当前有七个本机网站后台服务，包含新增的 `signplay-bank`；主站与作品集由 Nginx 提供静态内容。词典当前使用本机 `18080/18081` 的 CLab 通道，视频优先从 `/var/lib/shouyu/videos/` 提供；`zhuxingye` 的故障切换监控、告警服务和定时检查已运行。本轮保留这些数据、服务和旧兼容隧道。

同日后台访问统计增加项目合计、逐日项目数据和采集观测，11 类入口验证通过；新项目路径自动归类，原历史数据与去重密钥保留。查看 `sudo shouyulove-stats --days 30 --projects`，采集核对加 `--health`；指标与历史覆盖范围见 [后台统计说明](private-statistics.md)。

同日 10:45，作品集增加按作品、按天的跳转统计，覆盖全部 10 个入口及北大知道、清华知道、拼好课三个外部作品。查看 `sudo shouyulove-stats --days 30 --clicks`；这些是入口点击，和目标页面访问量分开。统计从上线开始，历史跳转没有保存。

当日主站发布为 `20261017T024553Z-astra-home`：257 文件、19 页面路由、5 个链接、111,757,815 字节。仅作品集 HTML 增加统计标识与脚本，另新增 922 字节脚本和公开作品名称表；原字体、样式、场景与其他页面文件保持。私有采集器升级，Nginx 只更新三个统计相关配置；历史记录、固定密钥及其他项目进程保留。部署与回滚回执在 `/var/backups/shouyulove-stats/20261017-portfolio-clicks/attempt-3/`。

## 2026-10-17 晚间词典校园网访问调整

普通词典访问改用独立签名会话额度，公共样式和图标免除低额会话限制，登录及 AI 查询启动另设更严格的配额。新增 `shouyulove-dict-guard` 辅助服务，七个既有网站后台服务继续使用原进程。词典原有 CLab 通道、本地视频、内容权限和报告入口保留。隔离环境的 30、50、100 人同 IP 测试全部通过；具体参数与验收边界见 [词典访问保护](dictionary-campus-access.md)。

私有耗时日志新增在 `/var/log/shouyulove-private/requests.jsonl`，便于后续区分等待上游、传输中断和限流；原访问统计与报告日志格式保持。配置回滚包位于 `/var/backups/shouyulove-maintenance/dict-campus-20261017/`。

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
