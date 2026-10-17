# 全站后台访问统计

## 2026-10-17 项目汇总与采集观测

统计范围按用户确认，覆盖当前服务器上 `shouyulove.cn` 的全部项目；不合并其他服务器上的北大／清华知道或拼好课。新增按项目汇总、逐日项目明细和每个项目的采集状态。原访问记录和 HMAC 去重密钥保持，升级前已有的页面记录也能直接汇总到项目。

当前识别主站、作品集、SignTrace、词典、传情会意、接锅、文化节、年终总结、SignPlay，以及手语／爱心社两份历史论坛资料。`/vocab` 旧入口归入 SignTrace；`/projects/作品名/` 是主站介绍页，归入主站。新项目无需登记才能计数：未知路径按第一级目录自动形成项目，如 `/new-app/a` 与 `/new-app/b` 同属 `/new-app`，以后可补友好名称。

最早保存的统一统计日期为 2026-10-11，2026-10-15 10:42 起才扩展到全部子页面。查询最近一个月时，早期缺失记录不补成零；不同项目的历史覆盖时段也可能不同。报表给出请求日期范围和数据库最早／最近记录日期。

## 2026-10-15 迁移后的查看入口

现在登录 `ssh shouyulove-aliyun`（`101.37.209.227`）后运行下方报表命令。腾讯旧采集器已停止并禁用；新机保留原密钥，将冻结的 1,528 次历史访问一次导入并继续采集。导入标记为 `tencent-to-aliyun-20261015-final-history`，不能重复回放旧库或重新开启旧采集器。

迁移最终库、备份与执行记录在新机 `/var/backups/shouyulove-migration/20261015/`。下文 10:42 升级备份属于旧腾讯服务器上的历史位置，不能误当作新机当前数据库。当前主机和依赖见 [运维状态](operations-current.md)。

从北京时间 2026-10-15 10:42 起，统计按页面响应自动覆盖 `shouyulove.cn` 和 `www.shouyulove.cn` 下的主站、作品集、项目详情及子站。新增静态页、反向代理页面和多层路径不需要再添加名单。独立域名上的北大知道、拼好课等不属于这个统计范围。

原统计数据和去重密钥继续保留；此前没有记录的子站访问不会自动补回。调整当天的新旧统计范围有差别，比较历史数据时需注意这一点。

## 查看方式

登录网站服务器后执行：

```sh
sudo shouyulove-stats --days 30
sudo shouyulove-stats --days 30 --pages
sudo shouyulove-stats --days 30 --projects
sudo shouyulove-stats --days 30 --health
sudo shouyulove-stats --days 30 --json
```

第一条显示每日访问次数、访客数、历史累计和所选时间段合计。`--pages` 加上逐日逐页明细；`--projects` 显示项目合计和逐日项目明细。JSON 另含 `projects`、`project_days`、`coverage` 和 `project_collector`；原 `days`、`pages`、`period`、`total`、`collector` 保持兼容。`total` 为历史累计，`period` 为选定天数内的合计。

访客用网络地址的 HMAC 去重，同一地址在不同页面和日期间可归并。它是访客估算：共用网络的人可能合为一个，换网络的人也可能被算作多个。全站去重访客不能用各页面访客直接相加。

项目访客也在同一项目的所有页面、全部查询日期之间去重，不能把页面或每日访客直接相加。项目访问次数可以相加得到全站访问次数。已知项目即使查询期内没有记录也显示在项目列表中。

`--health` 用于核对采集链路：每个项目显示候选 HTML 数、其中计入的访问数、首次／最近接收时间和最近计入时间。这里的候选包含测试与机器人，只从本次升级后开始，不能当成历史 PV；普通访问量仍排除这些请求。没有新候选只能说明近期未接收到页面事件，不能单凭它判断项目故障。

## 哪些访问会计入

计入成功的 HTML／XHTML 页面 GET 请求，包括 200 和能够识别为页面的 304 缓存校验。刷新或重新打开并向服务器请求页面，会增加访问次数。浏览器内部切换路由、返回缓存页或纯离线打开时，如果没有页面请求，就不会增加；这个后台口径不测量停留时长。

脚本、图片、音频、字体、JSON 接口、HEAD、重定向、错误响应、带预取标记的请求和已识别的机器人不计入。机器人过滤依据用户代理及请求标记，不能保证识别所有自动流量。验证请求必须使用 `ShouYuLove-QA`，不会进入访问数据。

记录用户请求的原始页面路径，先移除查询参数，再统一 `/index.html`、`/index.htm` 与所在目录。即使 Nginx 将 `/new/deep/page` 内部改写到入口文件，仍按原页面路径统计，避免不同页面全部并入首页。中文和其他非英文路径也可记录。

## 隐私与运行位置

采集器只接收本机 Unix 数据报，没有 HTTP 服务。数据库在 `/var/lib/shouyulove-stats/visits.sqlite`，密钥在同目录的 `secret.key`；目录权限 0700，数据与密钥 0600。访问记录只保留日期、HMAC 访客标识、页面路径和计数；采集状态另存项目、计数及时间，不保存查询参数、原始网络地址或浏览器标识。原始地址只在采集时用于计算 HMAC。

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

2026-10-17 的八项回归（含独立 Nginx 实例）全部通过。11 类正式入口用 `ShouYuLove-QA` 逐一验证，均返回 200，并在各自项目采集状态中读到事件；本次验证没有增加访问量。历史行未减少、数据库完整性通过、密钥文件保持，其他业务服务与 Nginx 配置未改动。

重启采集器后，Nginx 原 Unix 数据报连接可能有一次失效重连，应先执行 QA 探针并用 `--health` 确认各项目接收。本次首个主页探针遇到该情况，复验成功且未污染访问量；采集状态记录的是复验结果。

`install.py` 用于首次安装或核验相同版本，发现已有文件不同会停止。升级前备份脚本、格式配置和 SQLite，原密钥保留；校验新配置后重载 Nginx、重启统计服务，再检查旧数据没有减少。回退只恢复采集代码与配置，不用旧数据库覆盖升级后已收到的访问。

10:42 升级的历史备份保留在腾讯旧机 `/var/backups/shouyulove-stats/20261015T024204Z-all-pages/`。本机执行与验收记录在 `output/deployment/shouyulove-stats-all-pages-20261015/`，不进入公共运行清单。

本次升级的代码和 SQLite 备份、回执及测试结果在阿里云 `/var/backups/shouyulove-stats/20261017-projects/`，本机记录在 `output/deployment/stats-projects-20261017/`。报表和逐页数据只留私有目录，不加入 Git 或公开静态站。回退恢复 `visits-before.py` 后重启统计服务，保留新数据库，避免丢失升级后已收到的访问。
