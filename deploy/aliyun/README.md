# 阿里云部署与兼容配置

## 2026-10-21 所有者密码登录

`ssh/90-wishingcat-password.conf` 是新增所有者账号 `wishingcat` 的 SSH 片段，仅开放该账号的密码认证。原有账号与密钥登录保持；账号和密码在服务器私下创建，仓库不保存凭据。完整验收与撤销方式见[当前运维状态](../../docs/operations-current.md)。

## 2026-10-17 词典校园网会话限流

`shouyulove.server.conf` 已从当晚现场配置更新，保留已有 CLab 直连、视频本地优先和独立报告入口。本次发布只修改词典区块并增加私有耗时日志，不替换主备 upstream 文件。新增会话限流片段、守卫服务和测试见 [词典访问保护](../../docs/dictionary-campus-access.md)。原 `shouyulove-limits.conf` 保持不变，继续供其他路由使用。

密钥及生成的 `/etc/shouyulove/dict-guard-signing.conf` 不在仓库内；不能直接用本目录覆盖全机配置。

## 2026-10-17 作品集跳转统计配置

本次更新 `shouyulove-visit-format.conf`、`shouyulove-home.conf`，新增 `shouyulove-portfolio-click.conf`；对应清单项已更新哈希并标注日期。其余条目仍是下文所述迁移快照，不能作为全机当前配置整体恢复。新片段提供只写的跳转接收入口，报表仍只经 SSH 查看。详见 [后台统计说明](../../docs/private-statistics.md)。

## 2026-10-15 配置快照与共用设施

[当前运维状态](../../docs/operations-current.md) 是本目录的使用索引。`live-config-manifest.json` 保存的是迁移完成时的 15 份本站配置哈希，本次说明刷新核对这些文件后保留原快照；它不包含其他项目的 vhost，也不是全机恢复包。

`101.37.209.227` 上的 PKUKnow vhost 已改为退役响应（HTTP 410、拒绝 TLS 握手、无 upstream），不能恢复旧反代。以手予爱仍使用现有 SSH 身份、原 ACME 账户和 `certbot.timer`；清理 PKU 项目时不得连同这些共用设施删除。

28080/28081、28018/28042 仍被本站路由引用；28019/28040/28041 已无本站 Nginx 引用但尚未收回。它们共用 SSH 隧道，不能直接停整条 relay。自动续期 dry-run 已在迁移当天通过，本次说明更新不再触发签发或续期。

2026-10-15，shouyulove.cn 的主站和子项目已切到 `101.37.209.227`，维护入口为 `ssh shouyulove-aliyun`。完整服务、状态目录和验收记录见 [迁移与维护](../../迁移与维护.md)。

本目录保存迁移后的非秘密配置。`live-config-manifest.json` 给出新机原路径和逐文件 SHA-256；`nginx/` 是退出临时 gate 后的配置快照，源配置中带日期的旧注释保留用于追溯。普通项目发布只更新各自片段，不能批量覆盖这里所有文件。共享 Nginx 的预检、修改、重载和回滚统一持有 `/run/lock/nginx-deploy.lock`。

## 新机

- `nginx/shouyulove.server.conf` 对应本站独立 vhost，包含真实地址信任、ACME 路径、子站与旧 SignTrace job 的兼容路由。
- `nginx/conf.d/` 保存本站限流区、HTML 访问统计、词典 upstream 和年终总结会话分流；`nginx/snippets/` 保存各子站当前路由。
- `systemd/system-shouyulove.slice` 为六个应用设置共同资源预算；各项目的 unit 在所属仓库维护。传情会意没有 Git，本目录保留其 unit。
- 统计源码、unit 和安装器仍在 `../private_stats/`。统计数据库、固定 HMAC 密钥、账户、查询记录及个人报告不进入仓库。

## 证书

Certbot 本域 lineage 为 `/etc/letsencrypt/live/shouyulove.cn`，通过 `/var/lib/shouyulove-acme` 的 HTTP webroot 验证。已有 `certbot.timer` 调度续期，保存的 `renew_hook` 指向 `/usr/local/sbin/shouyulove-cert-deploy.py`，源码在 `tls/`。

hook 只处理根域和 www，先私密备份证书，再复制到实际服务目录 `/etc/shouyulove/tls/`，持共享锁执行 `nginx -t` 与平滑重载。它不更改 Nginx 配置。不要把证书私钥、ACME 账户文件或一次性签发资料提交到仓库。

单独演练本域续期：

```sh
ssh shouyulove-aliyun 'certbot renew --cert-name shouyulove.cn --dry-run --no-directory-hooks'
```

## 旧机过渡

`compat/` 只适用于旧腾讯服务器 `49.232.193.175`。80/443 与旧公开 8018 都转入新机，缓存旧 DNS 或使用旧地址的访问仍可继续。8018 的规则由独立 oneshot unit 维护，不能单独停用该 unit，否则旧写入入口会重新开放。

目标 28080 经旧机 18082 复用 CLab 词典的主备链路，28081 承接视频和 BBS；词典尚未改为直连 CLab。旧年终总结会话经 28042 继续到旧进程，最长 12 小时，新登录始终进入新机。旧 SignTrace job 经 28018 验证原页面令牌后读取，新查询由新机处理。

旧机的传情会意、接锅、文化节和独立统计收集器已停用；数据与私有备份保留。词典改为直连、旧会话与任务兼容退出前，不能关闭旧机或整个隧道。回滚也必须先处理新机已产生的写入，不能直接恢复旧数据库作为权威状态。
