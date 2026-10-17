# 2026-10-17 服务器清理与运行项目

核查与清理目标为阿里云 `101.37.209.227`，维护入口 `shouyulove-aliyun`。按用户要求，只清理确认不再使用的历史副本和容器缓存，并保留必要回滚资料。

## 清理结果

2026-10-17 10:15（北京时间）完成删除。文件系统已用空间从 43,474,432,000 降至 39,339,089,920 字节，实测释放 **4,135,342,080 字节，约 4.14 GB / 3.85 GiB**；使用率从 **36% 降到 33%**，剩余约 **76.1 GiB**。净变化以 `df` 为准，包含正常日志写入和文件系统开销，不相加 Docker 的重叠分类。

| 清理项 | 依据与处理 |
| --- | --- |
| Docker 构建缓存 | 43 项均约四周未用，全部标为可回收；无容器、镜像标签或数据卷依赖。通过 Docker 自身命令清理，最终构建缓存为 0；工具报告原缓存约 3.36 GB |
| 主站迁移解压副本 | 删除 `/var/backups/shouyulove-migration/20261015/stage-candidate/` 下的 `apps` 和 `state`。11,063 个文件逐一匹配保留的原始迁移包，另有 4 个空 WAL／临时 SHM；文件块约 607.7 MiB |

删除前检查了文件类型、大小、inode、时间戳和 SHA-256，并排查进程打开文件、工作目录、内存映射、部署链接、Nginx/systemd/定时任务引用。副本没有运行依赖，原始压缩包通过完整性检查；凭据目录保持原样。

Docker 第一遍按一周未使用过滤，释放 15 项缓存；随后确认余下 28 项全部来自同一份已核验清单，且仍无使用者，再由 Docker 清理。没有手工删除 Docker/containerd 存储目录。

## 保留的恢复资料

- 以手予爱初始完整包 `bundle.tar.gz`、最终 `delta.tar.gz`、`final-apply`、配置及审计记录；需要恢复解压副本时使用这些包，先在隔离目录验证，避免覆盖迁移后的业务写入。
- PKUKnow 的 2026-10-15 完整迁移快照、受保护历史资源、人大停止运营最终归档、API 拆分检查点与最后回退版本。它们包含恢复用途或独有历史资料，本次保留。
- 各项目当前数据、全部发布目录、词典视频与备用工程、TLS/ACME、SSH、用户项目目录和日志。

## 当前提供服务的项目

以下为 2026-10-17 10:16 的现场状态；网站共有七个本机后台进程服务，此外有静态页面、词典转接和运维任务。

| 项目 | 当前运行方式 |
| --- | --- |
| 以手予爱主站、心创组作品集 | Nginx 静态站；`/`、`/portfolio/` |
| 以手寻语 SignTrace | `signtrace.service`，回环 8018 |
| 传情会意·手语版 | `shouyu-game.service`，回环 8019 |
| 接锅 | `jieguo.service`，回环 8040 |
| 2026 手语文化节 | `sign-language-festival.service`，回环 8041 |
| 2026 手语分社骨干年终总结 | `sign-year-end-summary.service`，回环 8042 |
| 指间趣游 SignPlay | Nginx 静态页面和 `signplay-bank.service` 题库后台，回环 8765 |
| 分社手语词典与历史论坛 | Nginx 使用本机 18080/18081 的 CLab 通道；视频优先读取 `/var/lib/shouyu/videos/`，缺失时回源 |
| 全站私有访问统计 | `shouyulove-stats.service`，Unix socket，仅服务器管理 |

`zhuxingye` 用户下的 `shouyu-syl-fallback-monitor`、`shouyu-alert-mailer` 正在运行，`shouyu-deployment-check.timer` 已排程。本机 `shouyu-web` 与 `shouyu-synonym-worker` 当前未启动，备用工程保留，不能按缓存删除。Mihomo、阿里云备份与云监控也在运行。Docker 守护进程保留，目前没有容器。PKUKnow 和微信公众号 API 已迁往 `121.43.143.226`，本机保留其恢复资料，不运行其业务服务。

现场发布链接：主站 `20261014T162210Z-astra-home`，SignPlay `20261017T021302Z-signplay`，SignTrace `20261016-acceptance-535b37a`，接锅 `20261017T020659Z`；这些链接在清理前后保持一致。

## 验收与记录

清理前后比较的 14 个系统服务、两个词典用户服务 PID/状态、发布链接和 Nginx 配置摘要一致；未重启或 reload。Nginx 语法检查通过，系统无失败服务，九个公开入口均返回 200。请求使用 `ShouYuLove-QA`，避免写入正式访问统计。本次检查覆盖入口、进程和配置，没有重跑各项目完整业务测试。

本机私有证据在 `output/deployment/server-cleanup-20261017/`；服务器在 `/var/backups/shouyulove-cleanup/20261017/` 保存删除清单、缓存回执、保留包摘要和空间变化。公开仓库只保存本说明与状态索引，私有文件清单不入库。说明同步到 `/opt/shouyulove-maintenance/20261017-storage-cleanup/`，不切换网站运行版本。
