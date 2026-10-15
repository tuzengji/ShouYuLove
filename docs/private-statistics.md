# 全站后台访问统计

从北京时间 2026-10-15 10:42 起，统计按页面响应自动覆盖 `shouyulove.cn` 和 `www.shouyulove.cn` 下的主站、作品集、项目详情及子站。新增静态页、反向代理页面和多层路径不需要再添加名单。独立域名上的北大知道、拼好课等不属于这个统计范围。

原统计数据和去重密钥继续保留；此前没有记录的子站访问不会自动补回。调整当天的新旧统计范围有差别，比较历史数据时需注意这一点。

## 查看方式

登录网站服务器后执行：

```sh
sudo shouyulove-stats --days 30
sudo shouyulove-stats --days 30 --pages
sudo shouyulove-stats --days 30 --json
```

第一条显示每日访问次数、访客数、历史累计和所选时间段合计。`--pages` 加上逐日逐页明细；JSON 包含 `days`、`pages`、`period`、`total` 和采集器健康信息。`total` 为历史累计，`period` 为选定天数内的合计。

访客用网络地址的 HMAC 去重，同一地址在不同页面和日期间可归并。它是访客估算：共用网络的人可能合为一个，换网络的人也可能被算作多个。全站去重访客不能用各页面访客直接相加。

## 哪些访问会计入

计入成功的 HTML／XHTML 页面 GET 请求，包括 200 和能够识别为页面的 304 缓存校验。刷新或重新打开并向服务器请求页面，会增加访问次数。浏览器内部切换路由、返回缓存页或纯离线打开时，如果没有页面请求，就不会增加；这个后台口径不测量停留时长。

脚本、图片、音频、字体、JSON 接口、HEAD、重定向、错误响应、带预取标记的请求和已识别的机器人不计入。机器人过滤依据用户代理及请求标记，不能保证识别所有自动流量。验证请求必须使用 `ShouYuLove-QA`，不会进入访问数据。

记录用户请求的原始页面路径，先移除查询参数，再统一 `/index.html`、`/index.htm` 与所在目录。即使 Nginx 将 `/new/deep/page` 内部改写到入口文件，仍按原页面路径统计，避免不同页面全部并入首页。中文和其他非英文路径也可记录。

## 隐私与运行位置

采集器只接收本机 Unix 数据报，没有 HTTP 服务。数据库在 `/var/lib/shouyulove-stats/visits.sqlite`，密钥在同目录的 `secret.key`；目录权限 0700，数据与密钥 0600。数据库只保留日期、HMAC 访客标识、页面路径和计数，不保存查询参数、原始网络地址或浏览器标识。原始地址只在采集时用于计算 HMAC。

统计源码在 `deploy/private_stats/`。线上脚本 `/opt/shouyulove-stats/visits.py` 由 `shouyulove-stats.service` 管理；`/etc/nginx/conf.d/shouyulove-visit-format.conf` 负责生成候选页面事件。主站原有两条普通访问日志保持原状，它们与这份私有聚合数据库是不同的数据。

## 新页面为何能自动加入

`nginx-format.conf` 根据响应类型筛选候选事件，`visits.py` 检查页面类型、请求用途和机器人标记，两处都不再依赖页面路径名单。日志入口位于现有主站 Nginx 的 server 层，同域名下新增 location 默认沿用。

Nginx 的访问日志在请求处理结束的位置写入，内部改写可能改变 `$uri`；统计因此使用去掉查询参数的 `$request_uri` 保留原页面。相关变量和日志行为见 [Nginx 日志模块](https://nginx.org/en/docs/http/ngx_http_log_module.html) 与 [核心变量说明](https://nginx.org/en/docs/http/ngx_http_core_module.html#variables)。

如果新 location 单独设置 `access_log` 或关闭日志，需要在该层同时保留私有日志入口，否则会覆盖继承设置。新页面也应正确返回 `text/html` 或 `application/xhtml+xml`。这两项属于页面服务器的常规配置，不需要在统计程序中登记新路径。

## 维护与验证

```sh
python3 -B -m unittest discover -s tests -p 'test_private_stats*.py' -v
```

普通测试覆盖新增路径、子站、缓存、查询参数过滤、跨页去重、历史数据与密钥保留。安装了 Nginx 的环境还会运行隔离的回环测试，覆盖静态页面、代理页面、内部改写、XHTML 和启动后新增页面。没有 Nginx 时，该项会明确跳过。

`install.py` 用于首次安装或核验相同版本，发现已有文件不同会停止。升级前备份脚本、格式配置和 SQLite，原密钥保留；校验新配置后重载 Nginx、重启统计服务，再检查旧数据没有减少。回退只恢复采集代码与配置，不用旧数据库覆盖升级后已收到的访问。

本次升级备份为 `/var/backups/shouyulove-stats/20261015T024204Z-all-pages/`。本机执行与验收记录在 `output/deployment/shouyulove-stats-all-pages-20261015/`，不进入公共运行清单。
