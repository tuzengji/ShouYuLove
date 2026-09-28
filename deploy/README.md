# 主站部署记录

2026-09-28 已更新到 https://shouyulove.cn/，名称为「以手予爱 ShouYuLove」。HTTP 与 HTTPS 根路径均提供主站。源码仓库为公开的 [tuzengji/ShouYuLove](https://github.com/tuzengji/ShouYuLove)。

## 当前部署

- 主机：`ubuntu@49.232.193.175`。
- 公开目录：`/var/www/shouyulove-home`，为当前发布目录的符号链接。
- 当前发布：`/var/www/shouyulove-home-releases/20260928T144827Z-collections13`。
- 上一版：`/var/www/shouyulove-home-releases/20260928T135914Z-naturecreators12`，保留可直接回退。
- 本次配置备份：`/etc/nginx/backups/shouyulove-home-20260928T144827Z-collections13`，包含站点配置、主页 snippet 和上一版路径。
- 站点配置：`/etc/nginx/sites-available/shouyulove`，由 `sites-enabled/shouyulove` 引用。
- 主页配置：`/etc/nginx/snippets/shouyulove-home.conf`，接管 `/`、`/home-assets/`、`/sign-projects/` 与 `/campus/`，后两者支持无尾斜杠跳转。
- 切换前配置：`/etc/nginx/backups/shouyulove-home-20260927T111544Z-plain5/shouyulove.conf`。

以手寻语 `/signtrace/`、词典 `/dict` 和游戏 `/chuanqinghuiyi/` 的既有代理保留，后端应用未重启。

## 更新流程

1. 执行 `npm run build` 和 `python3 scripts/check_catalog.py`，检查浏览器中的桌面、手机与减少动态效果模式。
2. 执行 `python3 scripts/package_site.py`，仅上传 ZIP 中的 `index.html`、`sign-projects/index.html`、`campus/index.html` 与 `home-assets/`。
3. 在远端创建新的发布目录，校验传输后的文件和权限，再原子切换 `/var/www/shouyulove-home` 符号链接；保留旧发布供回退。
4. 若改 nginx，先读取线上最新配置，将备份放在 `/etc/nginx/backups/`，通过 `nginx -t` 后 reload。
5. Reload 返回时新 worker 可能尚未接管请求；应进行有时限的内容就绪检查，再验证公网根页面、资源与三个子站。

不得把 `主站版本归档/`、`output/`、`docs/`、源项目数据或私密资料上传到公开目录。变更共享 CSS、JS 或字体时递增 `index.html`、CSS 和动态模块入口中的缓存版本，当前为 `collections-13`。

## 恢复切换前的根入口

将上述备份配置复制回 `/etc/nginx/sites-available/shouyulove`，执行 `sudo nginx -t`，通过后 `sudo systemctl reload nginx`。根入口会恢复为此前的 SignTrace 代理；无需停掉任何应用服务。新的静态发布文件可以保留供再次上线。

本版新增两个目录路由。若回退到不含分类页面的旧版，还需恢复本次备份中的 `shouyulove-home.conf` 到 `/etc/nginx/snippets/shouyulove-home.conf`，将符号链接指回上一版，通过 `nginx -t` 后 reload。三个子站配置不变。

## 验证记录

- `output/deployment/collections13-release.json`：当前发布、配置备份及上一版位置。
- `output/deployment/collections13-request.json`：部署前最新配置及旧发布哈希、公开文件白名单和新 snippet 哈希。
- `output/deployment/collections13-online-checks.json`：21 个公开文件的 SHA-256，以及 HTTP 主页、两个目录跳转、三个子站和拼好课入口状态。
- `output/playwright/collections-live-*.png`：线上桌面三页和手机目录截图；本地截图前缀为 `collections-*`。
- 21 个公开文件与本地部署包逐字节一致；上述页面 GET 均返回 200。真实浏览器从首页进入两个目录，并实际点击拼好课打开新标签页，原目录保留；无页面错误。
- 发布前后 `nginx -t` 通过；只更新主页 snippet 并 reload nginx，没有重启后端应用。主站配置文件及三个子站代理保持原样。

本次封面使用无人出镜的北大未名湖畔黄昏实拍，原图 4080×3060，桌面资源 3840×2880；首页和两个独立分类页面共用导航。手语作品收录三个原有项目；燕园服务收录拼好课。创作者只填写已有来源的姓名，不猜填。

一次性发布脚本 `output/deployment/publish_collections.py` 带旧发布、配置和新包哈希检查，保存可恢复备份；三页就绪检查失败时恢复上一版符号链接和旧 snippet。后续更新须重新读取线上状态，不直接重跑旧请求。
