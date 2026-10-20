# 主站 CDN 与 OSS（2026-10-18）

## 2026-10-20 飞手传书上线

「飞手传书」（王宁静设计）已加入核心创意，地址为 https://shouyulove.cn/flyinghands/ 。主站版本 `20261020T123649Z-astra-home`，354 个文件、20 条页面路由、11 个项目；资源使用 CDN 新前缀 `/v/20261020-flyinghands/`。发布与回滚信息见 [当前运维状态](operations-current.md)。

## 当前配置

| 项目 | 值 |
| --- | --- |
| 加速域名 | `assets.shouyulove.cn`，中国内地节点 |
| DNS | `assets` CNAME → `assets.shouyulove.cn.w.kunlunaq.com` |
| OSS | `shouyulove-static-20261018`，杭州、标准存储、LRS |
| 访问控制 | 私有 Bucket，阻止公共访问开启 |
| 回源 | OSS 域名类型、HTTPS 443、同账号 STS 回源 |
| 资源前缀 | `https://assets.shouyulove.cn/v/20261018-1/` |
| 资源规模 | 255 文件，113,135,193 字节；见根目录 `cdn-manifest.json` |
| 缓存 | `/v/` 缓存 365 天，客户端跟随；实测 `Cache-Control: max-age=31536000` |
| 传输 | HTTPS、HTTP/2、TLS 1.2/1.3、Gzip、Brotli |
| 跨域 | `Access-Control-Allow-Origin: *`；仅公开静态文件，无凭据请求 |
| 防盗链 | 允许主域及其子域、localhost、127.0.0.1、空 Referer；其他来源返回 403 |

根域及 www 仍指向 `101.37.209.227`，公网带宽维持 5 Mbps。子项目的应用资源、词典图片与视频没有迁到这个 Bucket；不能把本次效果写成所有子项目均已获得 CDN 加速。页面仍由 ECS 返回，因此原私有页面统计继续采集；CDN 的资源请求数量不与页面 PV 相加。

RAM 角色 `AliyunCDNAccessingPrivateOSSRole` 只信任 `cdn.aliyuncs.com`。已用自定义策略 `ShouYuLoveCDNReadPublishedAssets` 替换默认的全 Bucket 只读策略，权限为：

```json
{"Version":"1","Statement":[{"Effect":"Allow","Action":"oss:GetObject","Resource":"acs:oss:*:*:shouyulove-static-20261018/v/*"}]}
```

实测 CDN 回源为 `x-oss-cdn-auth: success`，直接匿名访问 OSS 返回 403。此次没有创建 AccessKey，也没有向 CDN 上传用户数据、后台目录或数据库。

## 费用与证书

已购买中国内地 CDN/DCDN 下行流量包 **100 GB / 1 年，14 元**，2026-10-18 15:00 起生效，至 2027-10-18 15:00。它是累计额度，不是每月 100 GB。超额流量、OSS 存储与回源、超出免费额度的 HTTPS 请求按实际用量计费；没有购买存储包、证书套餐或付费图片处理。资源包余量与实际账单以控制台更新后的记录为准。

专用 Let's Encrypt 证书覆盖 `assets.shouyulove.cn`，已获用户明确同意后上传至 CDN，名称 `assets-shouyulove-20261018`，有效至 **2027-01-16 15:09:33（北京时间）**。原件保存在 ECS `/etc/letsencrypt/live/assets.shouyulove.cn/`；本机临时上传副本已删除，私钥不得进入仓库、日志或网站目录。

**这张资源域名证书目前需要手动续签和重新上传。** 本次使用 DNS-01 手动验证，未设置 DNS 验证 hook 或 CDN 自动部署凭据。应在 2026-12-17 前安排续签，并在到期前确认 CDN 返回新证书。只针对 `assets.shouyulove.cn` 的 lineage 操作；根域与 www 的现有自动续期不变。不要把原站续期演练成功误写成 CDN 证书已支持自动续期。

价格与计费口径参考：[CDN 与 OSS 加速计费](https://help.aliyun.com/zh/cdn/product-overview/billing-of-oss-content-acceleration)、[静态 HTTPS 请求计费](https://help.aliyun.com/zh/cdn/product-overview/billing-of-https-requests-for-static-content/)。

## 后续构建与发布

1. 按现有流程构建并校验运行白名单；公开正文继续由绑定 MD 维护。为每次资源改动分配新的 `/v/<版本>/`，不要覆盖已缓存的对象。
2. 使用 `prepare_cdn.py`，从经过校验的运行目录生成 `site/`、`upload/`、`manifest.json` 和 `cdn-manifest.json`。工具只导出白名单内的 shared 资源，保留 ECS 原有静态文件字节，避免已打开页面的延迟请求失效。经典排序 Worker 与安装清单继续同源。
3. 将 `upload/` 内的完整目录结构上传专用私有 Bucket。先运行 `verify_cdn.py` 验证所有对象的 SHA-256、大小、模块 MIME、跨域和缓存，再进行浏览器验收。
4. 通过既有 `publish_astra.py` 发布 `site/`。从服务器生成新的 request 与回滚备份；保留上一版，检查 19 条主站页面及子站入口。不要把本地仓库整体上传到 OSS 或 `/var/www`。
5. 仓库同步新的 HTML、`runtime-manifest.json`、`cdn-manifest.json`、脚本和说明。服务器的维护证据只放在私有目录。

示例（路径与版本每次重新选择）：

```sh
python3 -B scripts/prepare_cdn.py \
  --source output/runtime \
  --manifest runtime-manifest.json \
  --destination output/cdn-new-release \
  --base https://assets.shouyulove.cn/v/NEW_RELEASE
python3 -B scripts/verify_cdn.py output/cdn-new-release/cdn-manifest.json \
  --output output/cdn-new-release/verified.json
```

部署前的白名单必须对应实际 source；完整内容重建产生新清单时使用构建生成的清单。两个脚本都不接受任意上传主机，准备工具拒绝覆盖已有输出。资源更新会换路径，通常无需刷新旧 CDN 缓存。

## 验证与性能记录

255 个 CDN 对象全部通过字节与头部校验；两项 CDN 准备回归通过。桌面和 390px 手机检查了首页、作品集、导航、字体与完整背景，无请求失败、脚本异常或横向溢出，作品集音频请求为 0。

本机候选版的手机首页约 4.6 秒进入原生场景，作品集内容约 0.13 秒可读、完整背景约 4.0 秒。候选版 HTML 来自本机，不能与正式网页混用。正式手机首页本轮冷加载为 **6.8 秒**；作品集 **0.60 秒**可读、**5.68 秒**背景就绪。当前测量使用同一台机器、禁用浏览器缓存，CDN 边缘缓存已经预热；不同网络和设备会有差别。

50 个共享公网出口的下载会话，每会话两个并发连接，重放手机首页首屏的 71 个资源，共 **3,550 个请求 / 637,249,650 字节**，全部 200；每会话 **13.58–15.65 秒**，中位 15.19 秒，P95 15.46 秒。该测试使用 HTTP/1.1、TLS 与 Gzip，验证资源下载能力，不包含真实手机渲染、Wi-Fi 争抢或教室出口的带宽限制。

第一次在 ECS 上压测，1,788 个已返回请求均为 200，但出现 17 次读取超时，触发脚本的 15 秒等待上限并中止其余会话；不能算通过，也未删去记录。该次 25.68 秒接收 299.56 MB，约 93 Mbps；尚未独立定位测试机网络链路的限制。随后在本机使用 45 秒单次等待上限复测，全部会话在 15.65 秒以内完成，实际未依赖放宽后的长等待。

正式部署验证 296 文件、19 路由、5 个相对链接，总计 115,101,198 字节。8 个应用服务 PID 与部署前相同，24 份 Nginx 配置哈希相同；词典限流、现有隧道、统计和其他子项目保持。

本机证据：`output/deployment/cdn-oss-20261018/`。服务器证据：`/opt/shouyulove-maintenance/20261018-cdn-oss/`。回滚目录为 `20261017T162339Z-astra-home`，配置备份位于 `/etc/nginx/backups/shouyulove-home-20261018T084902Z-astra-home/`。如需紧急退出 CDN，可按原发布器的锁与回滚流程切回上一版；无需更改根域 DNS 或重启其他应用。
