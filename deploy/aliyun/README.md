# 阿里云部署与兼容配置

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
