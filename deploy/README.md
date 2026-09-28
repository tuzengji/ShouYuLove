# 主站部署记录

2026-09-28 已更新到 https://shouyulove.cn/，名称为「以手予爱 ShouYuLove」。HTTP 与 HTTPS 根路径均提供主站。源码仓库为公开的 [tuzengji/ShouYuLove](https://github.com/tuzengji/ShouYuLove)。

## 当前部署

- 主机：`ubuntu@49.232.193.175`。
- 公开目录：`/var/www/shouyulove-home`，为当前发布目录的符号链接。
- 当前发布：`/var/www/shouyulove-home-releases/20260928T135914Z-naturecreators12`。
- 上一版：`/var/www/shouyulove-home-releases/20260928T133410Z-singlephoto11`，保留可直接回退。
- 本次配置备份：`/etc/nginx/backups/shouyulove-home-20260928T135914Z-naturecreators12`，包含站点配置、主页 snippet 和上一版路径。
- 站点配置：`/etc/nginx/sites-available/shouyulove`，由 `sites-enabled/shouyulove` 引用。
- 主页配置：`/etc/nginx/snippets/shouyulove-home.conf`，只接管 `location = /` 与 `/home-assets/`。
- 切换前配置：`/etc/nginx/backups/shouyulove-home-20260927T111544Z-plain5/shouyulove.conf`。

以手寻语 `/signtrace/`、词典 `/dict` 和游戏 `/chuanqinghuiyi/` 的既有代理保留，后端应用未重启。

## 更新流程

1. 执行 `npm run build` 和 `python3 scripts/check_catalog.py`，检查浏览器中的桌面、手机与减少动态效果模式。
2. 执行 `python3 scripts/package_site.py`，仅上传 ZIP 中的 `index.html` 与 `home-assets/`。
3. 在远端创建新的发布目录，校验传输后的文件和权限，再原子切换 `/var/www/shouyulove-home` 符号链接；保留旧发布供回退。
4. 若改 nginx，先读取线上最新配置，将备份放在 `/etc/nginx/backups/`，通过 `nginx -t` 后 reload。
5. Reload 返回时新 worker 可能尚未接管请求；应进行有时限的内容就绪检查，再验证公网根页面、资源与三个子站。

不得把 `主站版本归档/`、`output/`、`docs/`、源项目数据或私密资料上传到公开目录。变更共享 CSS、JS 或字体时递增 `index.html`、CSS 和动态模块入口中的缓存版本，当前为 `creators-nature-12`。

## 恢复切换前的根入口

将上述备份配置复制回 `/etc/nginx/sites-available/shouyulove`，执行 `sudo nginx -t`，通过后 `sudo systemctl reload nginx`。根入口会恢复为此前的 SignTrace 代理；无需停掉任何应用服务。新的静态发布文件可以保留供再次上线。

仅回退主页版本时，改符号链接指向旧的主页发布目录即可，不改子站路由。

## 验证记录

- `output/deployment/naturecreators12-release.json`：当前发布、配置备份及上一版位置。
- `output/deployment/naturecreators12-online-checks.json`：18 个公开文件的 SHA-256 与三个子站状态。
- `output/playwright/nature-creators-live-*.png`：线上手机首屏和桌面心创组介绍；本地桌面展陈、手机及减少动态效果模式截图前缀为 `nature-creators-*`。
- 公网 HTTP/HTTPS 主页、CSS、JS、字体和图片与本地文件逐字节相同；三个子站 GET 均返回 200。
- `output/deployment/activate_home.py` 是带原配置哈希保护的一次性切换记录，后续更新须重新检查现状，不直接重跑该脚本。

本次发布将封面换为人物占比较小的树下牵手远景，作品集列表与横向展陈支持创作者字段，传情绘意显示「创作者：涂增基」。其他作品作者待用户提供，未猜填。只切换静态发布目录；没有修改 nginx 配置或重启应用。历史验证记录保留在本地 `output/`。
