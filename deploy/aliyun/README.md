# 阿里云部署与现行配置边界

## 当前配置与主机状态（2026-11-16）

[当前运维状态](../../docs/operations-current.md) 是本目录的总索引。`shouyulove.cn` 主站、全部同域子项目与拼好课当前统一运行于阿里云杭州 ECS `i-bp1hi3u3w5p3vg4owfl0`（`101.37.209.227`，维护入口 `ssh shouyulove-aliyun`）。

- **腾讯旧机兼容已退役（2026-10-28）**：腾讯 `49.232.193.175` 已重装为纯净 Ubuntu 22.04.5；本站 vhost 已移除对旧 IP 的代理信任、SignTrace `28018` 旧任务回源及年终总结 `28042` 会话分流，迁移隧道与全部 `280xx` 转发端口已停用销毁，词典经本机 `18080/18081` 直连 CLab。`compat/` 目录仅作为 2026-10-15 迁移期历史留存，**严禁**重新部署。
- **现网增量与局部更新原则**：本目录中的 `live-config-manifest.json` 与 `nginx/` 保存迁移及后续关键变更的非秘密配置基线。线上共享 Nginx 另外包含近期上线的 `shouxiaoyu.conf`、`shouyulove-drive.conf`、`shouyulove-auth.conf`、`flyinghands.conf`、去哪自习外部跳转统计、词典视频缓存及独立站点 `pinhaoke`、`tuzengji.com` 配置；日常发布只按项目差异更新对应片段，**严禁**将本目录整体覆盖到服务器 `/etc/nginx/`。共享 Nginx 的备份、修改、`nginx -t`、平滑 reload 与回滚统一持有 `/run/lock/nginx-deploy.lock`。
- **PKUKnow 旧代理退役与共用设施保护**：`101.37.209.227` 上的 `/etc/nginx/conf.d/yanyuan-calendar.conf` 仅保留退役响应（HTTP 410、拒绝 TLS 握手、无 upstream），不得恢复旧反代；以手予爱仍复用现有 SSH 身份、共用 `/etc/letsencrypt/accounts/` 与全局 `certbot.timer`，不得误删。

## 目录内容说明

- `nginx/shouyulove.server.conf`：本站独立虚拟主机基线（含真实地址信任、ACME 验证路径、词典会话限流及各子站片段引用；签名密钥 `/etc/shouyulove/dict-guard-signing.conf` 仅留服务器，不入库，详见 [词典访问保护](../../docs/dictionary-campus-access.md)）。
- `nginx/conf.d/`：本站限流区、HTML 私有访问统计格式（`shouyulove-visit-format.conf`）、词典 upstream；`nginx/snippets/` 保存主站、作品集点击（`shouyulove-portfolio-click.conf`）及部分子站路由快照。
- `systemd/system-shouyulove.slice`：为同域后台服务设置共享资源预算（CPUQuota 200%、MemoryHigh 2G、MemoryMax 3G；当前涵盖 `signtrace`、`shouyu-game`、`jieguo`、`sign-language-festival`、`sign-year-end-summary`、`shouyulove-stats`、`signplay-bank`、`flyinghands`、`shouyulove-auth`、`shouyulove-drive`、`shouyulove-drive-fb` 共 11 个活跃单元）。传情会意无独立 Git 仓库，其 unit 保留在本目录；其余子项目 unit 在各自仓库维护。
- `ssh/90-wishingcat-password.conf` 与 `sudoers/90-wishingcat`：所有者账号 `wishingcat` 专用密码登录片段与免密 sudo 规则（`root:root`、`0440`，配合 `docker` 组权限；服务器不存明文凭据于仓库，验收与撤销步骤见 [当前运维状态](../../docs/operations-current.md)）。
- 私有统计源码与安装器位于 `../private_stats/`（统计口径见 [后台统计说明](../../docs/private-statistics.md)）；数据库、HMAC 密钥、账户、查询记录与个人报告永不入库。

## 根域与 www 证书续期

Certbot 本域 lineage 为 `/etc/letsencrypt/live/shouyulove.cn`，通过 `/var/lib/shouyulove-acme` 的 HTTP webroot 验证。`certbot.timer` 自动调度续期，`renew_hook` 指向 `/usr/local/sbin/shouyulove-cert-deploy.py`（源码在 `tls/`）：先私密备份，再复制到 `/etc/shouyulove/tls/` 并持 `/run/lock/nginx-deploy.lock` 执行 `nginx -t` 与平滑 reload。

单独演练本域续期（不改动现网证书）：

```sh
ssh shouyulove-aliyun 'certbot renew --cert-name shouyulove.cn --dry-run --no-directory-hooks'
```

注：CDN 资源域名 `assets.shouyulove.cn` 使用独立 DNS-01 证书（到期日 `2027-01-16`），不在上述自动续期覆盖范围内，须按 [CDN 说明](../../docs/cdn-oss.md) 手动续签并上传。
