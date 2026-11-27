# 当前运维状态与记录索引

## 2026-11-27 首页与作品集整体换成二维手绘风页面

按用户要求重新设计并替换主站首页 `/` 与作品集 `/portfolio/`，从 Astra/WebGL 三维运行时换成各一个 HTML 文件的轻量页面。

- **设计**：从主站标识「把爱递给你」生成全部插画。首屏一只手递出爱心，滚动时爱心沿手画虚线穿过全页，落进页尾另一只手并迸出小爱心；作品图标去掉原来的方形底色，改为透明图案垫一片形状不规则的浅色剪纸；鼠标悬停时蜡笔绕图标画一圈、角上冒出小爱心、标题被荧光笔划过。底色为暖白，标题用思源宋体中粗，正文用思源黑体，西文字标用 Cormorant Garamond 斜体（均为 SIL OFL 1.1）。页面不含任何三维或 WebGL 内容，系统开启「减少动态效果」时保持静止。
- **构建**：新增 `scripts/build_home.py`（页面）与 `scripts/sketch.py`（手绘线稿），样式 `styles/next.css`、`styles/home.css`、`styles/works.css`，脚本 `scripts/next.js`、`scripts/home.js`、`scripts/works.js`，测试 `tests/test_build_home.py`。`build_home.py --site` 写入 `index.html` 与 `portfolio/index.html`，并登记 `runtime-manifest.json` 与 `origin-asset-manifest.json`。首页约 146 KB、作品集约 137 KB，另有 3 个字体子集（约 234 KB）与 25 个 WebP 图标（约 291 KB），放在 `/assets/next-*`，文件名带内容哈希，沿用一年 `immutable` 缓存。
- **内容**：正文仍取自绑定原稿，25 个作品 28 个入口链接与原稿一致，「手语视听说」位于「核心创意」第 4 位。作品集保留点击统计挂钩与手机「添加到桌面」。
- **主站原子发布（`20261127T095304Z-astra-home`）**：运行白名单升级至 1,120 个运行文件、34 条页面路由、5 个相对链接、2 条外部跳转，共 `207,466,306` 字节（上一版本 `20261127T094624Z-astra-home`）。在上一版本目录的完整副本上替换 2 个页面并加入 28 个新资源，经 `publish_astra.py` 持锁完成 1,120 个文件 SHA-256 逐项校验、`nginx -t` 与平滑重载；Nginx 路由片段未变（`c557dff2…`），34 条页面路由、4 条站内 308 跳转、2 条外部 302 跳转与 `/signtrace/`、`/chuanqinghuiyi/`、`/dict/entries` 均通过。服务器记录位于 `/opt/shouyulove-maintenance/20261127-next-home/`，配置备份位于 `/etc/nginx/backups/shouyulove-home-20261127T095304Z-astra-home/`。
- **验收**：公网 `https://shouyulove.cn/` 与 `/portfolio/` 在 1440、390、320 宽度下用无头浏览器（`User-Agent: ShouYuLove-QA`）核对，无横向溢出、无脚本报错、无失败请求，三款字体加载成功；作品集点击后 `/__syl/portfolio-click/<id>` 请求照常发出，手机宽度下「添加到桌面」正常显示。
- **作品简介改成一句短话（`20261127T095945Z-astra-home`）**：按用户要求，把以手寻语、分社手语词典、手语视听说、手小语、行动代号、拼好课、北大知道、清华知道、手语分社统一通行证、心创云盘十条较长的简介各压成一句短话，奶家麻将保持原文；先改绑定原稿与公开副本 `content-source.md`，再运行 `build_home.py --site`。运行白名单升级至 1,122 个文件、`207,673,232` 字节（文案变化后新增 2 个字体子集，旧子集保留），同样经 `publish_astra.py` 原子发布并通过公网复核；服务器记录位于 `/opt/shouyulove-maintenance/20261127-next-home-copy/`。旧风格的 `/projects/<id>/` 详情页仍显示原简介。
- **作品图标换成同色描边（`20261127T102847Z-astra-home`）**：用户认为原图标的深墨绿粗描边发黑、没有高级感。先用核心创意五枚图标给出细线、同色描边、剪纸、线稿四种方案，用户选定同色描边后套用到全部 23 枚矢量图标和 4 种按钮小图标：图形与填色保持设计者原稿，每块颜色的描边改为它自己深一号的颜色，线宽收到原来的 0.62 倍。只有图片的两枚（小爱同学的物资小屋、2026 手语文化节）保持原图。新增 `scripts/icon_style.py`，重绘结果存入 `project-logos/20261127-同色描边/`，原稿目录未改。运行白名单升级至 1,145 个文件、`207,940,412` 字节（新增 23 个图标文件，旧文件保留），经 `publish_astra.py` 原子发布；公网 1440、390、320 宽度复核通过，25 个图标均为一年 `immutable` 缓存，点击统计照常。服务器记录位于 `/opt/shouyulove-maintenance/20261127-next-home-icons/`。
- **图标调亮、分类改名与旧页面统一（`20261127T104339Z-astra-home`）**：用户认为同色描边后的图标「上色还是比较偏暗」，希望「明亮一点，整个网页充满活力」；`icon_style.py` 新增 `brighten`（`BRIGHT = 1.3`），全部矢量图标与按钮小图标重新生成。按用户要求把分类「心创组内部使用」改名为「心创组」（原稿、公开副本、两个构建脚本与测试同步修改），首屏「以手予爱」、英文字标与身份说明三行的字号比例重新调整（桌面端约 132、49、18.5px），愿景段落改为两端对齐。用户要求标签页图标、分享图与旧页面「全都统一」：新增 `scripts/legacy_pages.py`，由 `build_home.py --site` 调用，重画主站标识得到新的标签页图标、桌面图标、安装图标与网页清单，重做 25 张作品方形图（暖白底、剪纸色块、新图标），重写页面数据脚本 `local-bridge.251d0b938b.js`，并改写 25 个作品页、7 个 the-studio 页与其 `_payload.json` 中的引用、分类名和简介。旧页面的字体与文字图集缺「即」「它」两字，故把以手寻语与心创云盘的简介改为「描述你看到的手语动作，查出对应词义。」「心创组内部共享网盘，登录后在线管理文件。」。运行白名单升级至 1,201 个文件、`209,767,166` 字节，经 `publish_astra.py` 原子发布；公网 1440、390、320 宽度复核通过，三个图标链接均返回 200，点击统计照常。服务器记录位于 `/opt/shouyulove-maintenance/20261127-next-home-bright/`。
- **布局、尺寸与手小语头像（`20261127T105733Z-astra-home`，随后 `20261127T110754Z-astra-home`）**：按用户要求，首页「心创组」不再与「其他作品」并排，单独放在第三位；两页所有作品图标统一为同一尺寸（首页宽屏 104px、作品集宽屏 84px、手机 72px，公网逐页核对 `offsetWidth` 一致）；作品集分类导航由圆角框按钮改为目录式（宋体分类名、斜体数量、当前分类下画豆沙色线），390px 下四项正好排满、320px 可横向滑动；以手寻语掌心改为浅肤色（`icon_style.RECOLOUR`）；手小语改用其网站头像。运行白名单 1,224 个文件、`211,032,979` 字节，公网 1440、390、320 宽度复核通过。旧版作品详情页在无头浏览器里有一条 `Cannot read properties of null (reading 'match')` 报错，改动前的页面同样存在，与本次修改无关。
- **「边界」底色（`20261127T114940Z-astra-home`）**：用户要求「边界也一样」，首页「边界」一节去掉浅黄底，两页所有分区统一暖白底，并删除不再使用的托盘样式。公网三种宽度复核通过。
- **手语游戏底色（`20261127T114244Z-astra-home`）**：按用户要求，首页与作品集的「手语游戏」不再垫浅桃色托盘，和其他分类一样用暖白底；各作品剪纸颜色保持不变。公网三种宽度复核通过。
- **作品集精简（`20261127T113431Z-astra-home`）**：按用户要求删去作品集四个分类大标题下的说明文字（用户特别说明只删这四句，各作品简介不动；首页的分类说明保留），删去作品之间的分隔横线，并把页头「心创组作品集」与身份说明的比例收拢到约 4 : 1（电脑端 74、18.5px；手机 390 宽度 28、14px）。只改动 `portfolio/index.html`，公网三种宽度复核通过。随后按用户要求加大分类标题与第一排作品的距离（`20261127T113721Z-astra-home`，电脑端约 75px、手机 40px）。
- **手机端动效（`20261127T112937Z-astra-home`）**：用户认为手机端「比较平常」。触屏上滚动经过屏幕中央的作品会自动点亮（与电脑悬停同一套动效，同一时间只有一个），两只手缓慢漂浮、首屏的手随滚动略有视差；电脑端与「减少动态效果」行为不变。公网 390、320 宽度滚动时首页与作品集均有作品依次点亮，1440 宽度不受影响，三种宽度均无溢出和报错。
- **首屏字号（`20261127T112403Z-astra-home`）**：用户认为「以手予爱」、英文字标和身份说明三行「大小悬殊太大」，改为约 5 : 2 : 1（电脑端 98、43、19px；手机 390 宽度 55、24、16px；320 宽度 46、20、15px），只改动 `index.html`，公网三种宽度复核通过。
- **奶家麻将标志（`20261127T111757Z-astra-home`）**：按用户要求，把用户提供的奶麻角色图（512px 透明底，原文件来自用户下载目录，副本 `project-logos/20261127-naimahjong-tile/naima-source.webp`）印在一张麻将牌上：牌面象牙色、牌背绿色，同样调亮并用同色描边；角色贴着牌面内框底边并占满宽度，原图截断处藏进圆角框。运行白名单 1,227 个文件、`211,154,649` 字节，公网 1440、390、320 宽度复核通过。奶家麻将站点自身部署在合作方主机，其标签页图标未改。
- **子站标签页图标统一（2026-11-27）**：以下 8 个子站的标签页图标、桌面图标与页内标识换成调亮加同色描边的版本，文件名不变（这些文件缓存不超过 7 天），各自按发布规则新建版本后切换，旧版本保留可回滚：以手寻语 `/opt/signtrace/releases/20261127T105848Z-pale-palm-2e0eead4a`（仓库提交 `e7786c6`，掌心改为浅肤色）、传情会意 `/opt/shouyu-game/releases/20261127T104927Z-bright-icons`（无 Git 仓库，本机文件已同步）、飞手传书 `/opt/flyinghands/releases/20261127-bright-icon`（`864c701`）、接锅 `/opt/jieguo/releases/20261127T105950Z`（`e4f9c49`）、年终总结 `/opt/sign-year-end-summary/releases/20261127T110040Z-bright-icons`（`ed21053`）、统一通行证 `/opt/shouyulove-auth/releases/20261127T110204Z`（本机提交 `77ba1dd`，该仓库没有远端）、指间趣游 `/var/www/shouyulove-signplay-releases/20261127T110553Z-signplay`（只替换线上 `index.html` 里内嵌的 4 个图标，未从带有未提交改动的源码重新构建；仓库提交 `270f56b`）、手语视听说（`xinchuangzu` 托管目录内原地替换 3 个图标并把页面里的 `?v=1` 改为 `?v=2`，原文件备份在 `/opt/shouyulove-maintenance/20261127-subsite-icons/shitingshuo-before/`）。手小语、文化节、小爱同学、骷髅牌、拼好课、北大知道与清华知道本来就用自己的品牌图或图片；完美一餐与五款伍家阳游戏没有设置标签页图标；奶家麻将与去哪自习部署在合作方主机。这些都没有改动。
- **未改动**：`/the-studio/` 与 `/projects/<id>/` 仍是旧版三维页面并保留在线，新版两页不再链接它们；其余子站的页面内容未变。需要回到旧版首页和作品集时，把 `/var/www/shouyulove-home` 指回 `20261127T094624Z-astra-home` 即可。

## 2026-11-27 主站「核心创意」第 4 位接入「手语视听说」

按用户要求核验服务器上的「手语视听说」静态子站（由 `xinchuangzu` 经 `shouyulove-route` 托管于 `https://shouyulove.cn/shouyu-shitingshuo/`，目录 `/var/www/shouyulove-sign-games-custom/shouyu-shitingshuo`，含 109 路支持 HTTP 206 Range 播放的手语视频），设计以手予爱同系列柔和彩色图标并同步接入主站首页与作品集 `/portfolio/` 的「核心创意」第 4 位（排在「小爱同学的物资小屋」之后、「手小语」之前，设计者李昌昊，「核心创意」共 7 项、全站共 25 个作品）：

- **柔和彩色图标与子站标签页同步**：按 `shouyulove-icon-design` 规范绘制 `256×256` 主矢量图 `project-logos/20261127-shouyu-shitingshuo/shouyu-shitingshuo.svg`（奶油色圆角影屏 + 底部灰绿字幕定位带 + 豆沙粉播放三角 + 右上微倾雾蓝对话泡，统一 `13px` 灰绿圆润描边 `#4b5d54`）及小尺寸简化稿 `shouyu-shitingshuo-small.svg`，导出 `1024×1024` 透明主图（叠加雾蓝浅底 `#e1e8ec` 生成 `640×640` 卡片方图），同时为 `/shouyu-shitingshuo/` 补齐同源 `favicon-64.png`、`favicon.ico` 与 `apple-touch-icon.png`（保留 `xinchuangzu:sign-games-dev` `0664` 协作权限，原站 `verify-deployment.py` 134 文件与 109 路视频 Range 校验零报错通过）。
- **字体重建与主站原子发布（`20261127T094624Z-astra-home`）**：先更新绑定原稿与公开副本 `content-source.md`，使用 `msdfgen v1.13` 完整重建覆盖 625 个中文用字的浏览器 WOFF2 字体与双套 WebGL MSDF 图集（`syl-v1-1-shitingshuo`），保留全部旧版不可变资源与既有 CDN 资源；运行白名单升级至 1,092 个文件、34 条页面路由（新增 `/projects/shouyu-shitingshuo/`）、5 个相对链接、2 条外部跳转，共 `206,849,407` 字节（上一版本 `20261126T152545Z-astra-home`）。经 `publish_astra.py` 持锁校验切换，34 条主站路由、`https://shouyulove.cn/shouyu-shitingshuo/` 及公网 1440／390／320px 无头浏览器验收均通过。配置备份位于 `/etc/nginx/backups/shouyulove-home-20261127T094624Z-astra-home/`，维护记录位于 `/opt/shouyulove-maintenance/20261127-shouyu-shitingshuo/`。

## 2026-11-26 主站「核心创意」第 3 位接入「小爱同学的物资小屋」

按用户确认将「小爱同学的物资小屋」（`https://shouyulove.cn/XiaoAi-Warm-Cabin/`，简介「爱心社物资与社办储物间管理系统。」，设计者黄庭逸）收录至以手予爱主站首页与作品集 `/portfolio/` 的「核心创意」第 3 位（排在「分社手语词典」之后、「手小语」之前，「核心创意」共 6 项，桌面端正好 3 行两列对齐，全站共 24 个作品）：

- **图标制作与完整字体重建**：基于用户提供的小爱同学卡通原图精细去除外围与丝带环内白色底色、消除描边白边并保留眼中星光高光，居中导出 `1024×1024` 透明主图标（`project-logos/20261126-xiaoai-warm-cabin/xiaoai-warm-cabin.png`），按主站统一留白叠加暖粉米底色 `#f4e5e4` 生成 `640×640` 方形卡片图；使用 `msdfgen v1.13` 完整重建覆盖 612 个中文用字的浏览器 WOFF2 字体与双套 WebGL MSDF 图集（`syl-v1-1-xiaoai-cabin`），保留全部旧版不可变资源与既有 CDN 资源。
- **主站原子发布（`20261126T152545Z-astra-home`）**：运行白名单升级至 1,021 个文件、33 条页面路由（新增 `/projects/xiaoai-warm-cabin/`）、5 个相对链接、2 条外部跳转，共 `198,789,310` 字节（上一版本 `20261126T150007Z-astra-home`）。经 `publish_astra.py` 全量校验切换，33 条主站路由、`https://shouyulove.cn/XiaoAi-Warm-Cabin/` 与公网 1440／390／320px 无头浏览器验收均零报错、零横向溢出通过。配置备份位于 `/etc/nginx/backups/shouyulove-home-20261126T152545Z-astra-home/`，维护记录位于 `/opt/shouyulove-maintenance/20261126-xiaoai-cabin/`。

## 2026-11-26 全站去除 `/games/` 中缀、迁移 `/XiaoAi-Warm-Cabin/` 与开放 `xinchuangzu` 顶层路径权限

按用户要求取消所有 `https://shouyulove.cn/games/*` 中缀路径，将既有 `/games/` 项目迁至简洁贴合项目名称的顶层路径（既有其他域名与外部跳转保持不变），并升级 `xinchuangzu` 的全站顶层路径配置权限：

- **三项 `/games/` 路由迁移至顶层路径（备份于 `/var/backups/shouyulove-maintenance/remove-games-prefix-20261126/`）**：
  - **骷髅牌**：`/games/skull/` → **`https://shouyulove.cn/skull/`**（`proxy -> 127.0.0.1:19087`）。以 `xinchuangzu` 在 `/home/xinchuangzu/sign-games/skull-releases/20261126-root` 执行 `npm ci && ./node_modules/.bin/vite build --base=/skull/`（25/25 单元测试通过、`dist/` 零 `/games/` 残留、`npm prune --omit=dev`），保留 `20261125-2` 回滚目录，原子切换 `/home/xinchuangzu/sign-games/skull` 软链并重启 `skull-table.service`。
  - **完美一餐**：`/games/perfectmenu/` → **`https://shouyulove.cn/perfectmenu/`**（静态托管 `/var/www/shouyulove-sign-games-custom/perfectmenu/`，单文件零硬编码前缀）。
  - **小爱物资小屋（`shared-storage-room.service` `19016`）**：`/games/stored-room/` → **`https://shouyulove.cn/XiaoAi-Warm-Cabin/`**（前端 `appBase()` 动态解析前缀，`/XiaoAi-Warm-Cabin/api/state` 与 `/XiaoAi-Warm-Cabin/community-inventory/` 零改动直通，并附带大小写不敏感 308 归并）。
  - 为保障昨日已分享链接与打开标签页不中断，在受管配置中保留三条历史 `/games/{skull,perfectmenu,stored-room}/` → 对应新顶层路径的 `308` 兼容跳转（可随时通过 `shouyulove-route legacy-clear` 移除）。其余已有独立域名或站内跳转的项目（`/NaiMahjong/`、`/where-to-study/`、`pinhaoke.love`、`pkuknow.cn`、`pkuknow.cn/thu` 及 8 款内置手语游戏等）均原样保留。
- **`xinchuangzu` 顶层路径配置工具升级（`shouyulove-route` / `sign-games-ctl`）**：
  - 升级 `/usr/local/sbin/sign-games-ctl` 并新增等价封装 `/usr/local/bin/shouyulove-route` 与软链 `/home/xinchuangzu/routes` → `/var/www/shouyulove-sign-games-custom`。
  - 不再强制 `/games/` 前缀，允许 `xinchuangzu` 在 `https://shouyulove.cn/<slug>/`（2–48 位大小写字母、数字、`-`、`_`）下自由执行 `add`（`static` / `proxy <19000-19999>` / `redirect <http(s)://...>` 外部服务器 302 跳转并透传子路径与参数）、`rename`、`delete [--purge-files]`、`routes`、`legacy-delete` / `legacy-clear`，所有自定义顶层路径均自动附带大小写不敏感 308 归并；写入前动态扫描 `/etc/nginx/sites-available/shouyulove` 与非受管片段，自动拦截对主站、`/auth/`、`/drive/`、`/dict/`、`/signtrace/`、`/catchpot/`、`/NaiMahjong/`、`/where-to-study/` 及内置 8 款游戏等既有路径的冲突覆盖，仍不开放通用 `sudo`/`docker`。同步更新 `/home/xinchuangzu/README-使用说明.txt` 并以 `xinchuangzu` 实测 `static`、改名、`redirect`、冲突拦截及删除清理全流程通过。
- **主站原子发布（`20261126T150007Z-astra-home`）**：先更新绑定原稿与 `content-source.md` 中「骷髅牌」「完美一餐」正式地址，升级 `BRIDGE_VERSION` / `PORTFOLIO_SCENE_VERSION` 至 `syl-v1-1-top-routes`（零新增中文字，保留 `syl-v1-1-naimahjong` 字体与旧版不可变桥文件），经 `publish_astra.py` 持锁校验切换：951 个文件、32 条页面路由、5 个相对链接、2 条外部跳转，总计 `190,830,502` 字节（上一版本 `20261125T061159Z-astra-home`，备份于 `/etc/nginx/backups/shouyulove-home-20261126T150007Z-astra-home/`，维护记录位于 `/opt/shouyulove-maintenance/20261126-top-routes/`）。全部 11 个同域系统服务及 `skull-table.service`、`shared-storage-room.service` 均正常运行。

## 2026-11-25 阿里云一号机 ECS 自动快照策略与快照前一致性热备上线

按用户确认启用阿里云 ECS 自动快照方案，并同步在服务器补齐快照前一致性热备，解决全站此前仅有本机局部备份、无云端兜底的隐患：

- **阿里云 ECS 自动快照策略（华东1 杭州）**：
  - 绑定实例：`i-bp1hi3u3w5p3vg4owfl0`（`以手予爱`，`101.37.209.227`），系统盘 `d-bp1hi3u3w5p3vg4r71kr`（`200 GiB ESSD 云盘 PL0`，`/dev/xvda`）；未改动账号下其他实例（如 `i-bp12k7010n8lbitm2phs`），未触发任何预付费购买流程。
  - 策略详情：`sp-bp13xzhg26jlbv1rvebq`（名称 `shouyulove-daily-7d`，状态正常），**每天 `04:00`（UTC+8，周一至周日）**自动创建标准增量快照，**保留 `7` 天**自动滚动清理，未开启跨地域复制。首次自动快照将于次日 `04:00` 自动触发。
- **服务器快照前一致性热备（`shouyulove-presnap-backup.timer`）**：
  - 部署 `/usr/local/sbin/shouyulove-presnap-backup.py` 及 `shouyulove-presnap-backup.{service,timer}`，每天 **`03:40` CST**（云盘快照前 20 分钟）运行：通过 Python SQLite Online Backup 只读 URI 对全站 9 份活跃可写数据库（`shouyulove-auth/accounts.sqlite`、`shouyulove-stats/visits.sqlite`、`pinhaoke/{账户,访问统计,留言板}.db`、`flyinghands/materials.sqlite`、`jieguo/jieguo.sqlite3`、`shouyu-game/访问统计.sqlite`、`signplay-bank/bank.sqlite`）热备并逐个校验 `PRAGMA integrity_check == ok`，连同云盘配置、路由表、Nginx 配置片段原子替换写入 `/var/backups/presnap/latest/`（单份滚动约 `33 MB`，权限严格 `0700 root:root`，`xinchuangzu` 不可读），末尾执行 `sync` 将系统盘与 `/srv/shouyulove-drive` 挂载镜像脏页刷盘。
  - 实测首次运行 1 秒完成（9 库全部校验 `ok`、`33,312,768` 字节），原库文件属主/权限与 11 个系统服务、`skull-table.service` 均零扰动。

## 2026-11-25 手语游戏六个项目界面重做上线

- **五款单文件游戏（`20261125T092841Z-sign-games`，保留 `20261125T091605Z-sign-games`、`20261125T062723Z-sign-games`、`20261124T090628Z-sign-games`）**：水果炸弹、炸飞机、行动代号、雪豹凶杀案、巴巴爸爸各自换成独立主题的新界面，文案重写，并修复一批逻辑问题（详见各游戏 `README.md`）。路由、存档键与 `巴巴爸爸素材/`、`巴巴爸爸视频/` 不变；`site/` 里的中文文件名改为与正式页面内容一致。发布用 `手语游戏/工具/deploy.sh --go`：以线上版本为底复制出新版本目录，同步各游戏 `site/`，校验 9 段视频与 10 张图后原子切换软链，未改 Nginx。
- **指间趣游（`20261125T091853Z-signplay`，保留 `20261017T031714Z-signplay`）**：保留配色、Logo 与信息架构的视觉打磨和界面文案润色，修复待补充游戏返回路径、难度说明与搜索框残留三处问题。静态版本经 `sign-games-ctl switch signplay` 切换，未使用旧发布器 `publish_release.py`，未改 Nginx 与题库服务。本机仓库改动尚未提交推送。
- **验收**：公网 13 个地址与本机文件 SHA-256 一致；10 个页面在 1440／390／320px 无头浏览器下零横向溢出、零报错；视频、素材、主站首页与作品集、其余手语游戏入口均返回 200。

## 2026-11-25 手语游戏手机端与桌面端专项优化上线

按用户要求巡检「手语游戏」栏目除涂增基与王宁静外的 8 款游戏在手机（390px、320px 触控）与桌面（1440px）视口下的显示与交互表现，并在保留原有视觉配色、文案与玩法机制前提下完成定向优化与上线：

- **无需改动（现状核验通过）**：「指间趣游 SignPlay」（`/signplay/`，首页、分类、详情、资料、反馈）与「骷髅牌」（`/games/skull/`，大厅、规则弹窗、3 人与 10 人测试牌桌）在 320／390／1440px 视口均零横向溢出、交互完整，保留现有发布与 `skull-table.service` 不动。
- **6 款游戏双端优化与原子发布**：
  - **完美一餐（`/games/perfectmenu/`）**：补齐第 1–4 步全套 `<= 960px`／`<= 360px` 响应式排版、新增手机触控表态栏 `#mobile-vote-bar` 与点击就座交互、将规则书按钮移至右上角胶囊避免遮挡卡片与底栏、修复规则书关闭状态与跨步切屏自动回顶；原子替换 `/var/www/shouyulove-sign-games-custom/perfectmenu/index.html`（`root:sign-games-dev` `0664`，旧版备份于 `/opt/shouyulove-maintenance/20261125-sign-games-mobile/perfectmenu-index.html.before`）。
  - **五款静态游戏（`20261125T062723Z-sign-games`，保留旧版 `20261124T090628Z-sign-games`）**：「炸飞机」玩家端改用流式 `--cell` 令 10×10 棋盘单屏完整显示、主持人端取消移动端吸顶工具栏遮挡并新增左右滑盘与「整盘缩览」一键切换；「水果炸弹」修复 `#triggerPanel` 层叠覆盖导致默认挡屏的 CSS 缺陷、放宽玩家姓名输入列、手机端将开局/操作卡置顶并将技能速查改为 66dvh 抽屉、玩家技能表在手机端切换为堆叠卡片；「巴巴爸爸」取消移动端吸顶栏遮挡、单列分组与角色卡并限制视频视口高度；「行动代号」优化 5×5 手机字号与角标留白，6×6／7×7 与自定义宽盘改由 `.board-scroll` 保留原行列坐标；「雪豹凶杀案」扩宽 SVG `viewBox` 至 `1130×680` 消除右侧标签裁切，手机端支持清晰滑图点选、一键「整图缩览」及全屏放大顶部可点击关闭。
- **权限与验收**：发布目录保持 `root:sign-games-dev`（`2775`/`0664` + 默认 POSIX ACL），9 段 `巴巴爸爸视频` 完好，11 个同域系统服务与 `skull-table.service` 均维持原 PID 稳定运行；公网 320／390／1440px 无头浏览器全流程验收零溢出、零 JS/HTTP 报错。

## 2026-11-25 主站「手语游戏」第 3 位接入「奶家麻将」（直连 `/NaiMahjong/`）

按用户确认将王宁静设计的「奶家麻将」收录至以手予爱主站首页与作品集 `/portfolio/` 的「手语游戏」第 3 位（列于「骷髅牌」「完美一餐」之后），直接复用既有站内独立跳转入口 `https://shouyulove.cn/NaiMahjong/`（`/etc/nginx/snippets/naimahjong.conf` `302` 跳转至 `http://39.96.206.228:8444/`，保留查询参数）：

- **原稿、图标与完整字体重建**：先更新绑定原稿与公开副本 `content-source.md`（简介采用用户指定文案、设计者王宁静）；设计柔和彩色红中麻将图标（`project-logos/20261125-naimahjong/`）；使用 `msdfgen v1.13` 完整重建覆盖 608 个中文用字的浏览器 WOFF2 字体与双套 WebGL MSDF 图集（`syl-v1-1-naimahjong`），保留全部旧版不可变资源与既有 CDN 资源。
- **主站原子发布（`20261125T061159Z-astra-home`）**：运行白名单升级至 949 个文件、32 条页面路由（新增 `/projects/naimahjong/`）、5 个相对链接、2 条外部跳转，共 `190,665,793` 字节（上一版本 `20261125T053315Z-astra-home`）；全站共 23 个作品（「手语游戏」11 款）。经 `publish_astra.py` 全量校验切换，32 条主站路由、`https://shouyulove.cn/NaiMahjong/` `302` 跳转与公网 1440／390／320px 无头浏览器验收均零报错通过。配置备份位于 `/etc/nginx/backups/shouyulove-home-20261125T061159Z-astra-home/`，维护记录位于 `/opt/shouyulove-maintenance/20261125-naimahjong/`。

## 2026-11-25 「完美一餐」主持人端上线并联动主站

按用户要求部署黄雨琦设计的 5–15 人手语点菜合作游戏「完美一餐 · 主持人控制台」（单文件纯静态 `perfectmenu-standalone(7).html`，零外部依赖）并同步接入主站首页与作品集「手语游戏」栏目：

- **静态站部署与协作权限**：本机归档至 `手语游戏/完美一餐/`（公网发布白名单 `site/index.html`，`146,950` 字节），同步上传至 `/var/www/shouyulove-sign-games-custom/perfectmenu/index.html`（`root:sign-games-dev`，`2775`/`0664`），并通过 `/usr/local/sbin/sign-games-ctl custom-add perfectmenu static` 纳入受管 Nginx 片段 `/etc/nginx/snippets/sign-games-managed.conf`，正式入口 `https://shouyulove.cn/games/perfectmenu/`（`/games/perfectmenu` 自动 `308` 归并），`xinchuangzu` 账号后续可直接更新或扩展双端。桌面无头浏览器实测开场页、规则书弹窗、5 人选座、词库与操控模式、词表分配及对局面板全流程零报错通过。
- **图标、字体、排序与简介精炼（`20261125T051617Z-astra-home` → `20261125T052701Z-astra-home` → `20261125T053315Z-astra-home`）**：先更新绑定原稿与副本 `content-source.md`（设计者黄雨琦），设计柔和彩色餐盖图标（`project-logos/20261125-perfectmenu/`），并用 `msdfgen v1.13` 完整重建覆盖 621 个中文用字的浏览器 WOFF2 字体与双套 WebGL MSDF 图集（`syl-v1-1-perfectmenu`）；随后按用户要求将「完美一餐」调至「手语游戏」第 2 位（`syl-v1-1-perfectmenu-v2`），再按 `humanizer` 原则将全部 10 款手语游戏简介润色为单句凝练介绍（`syl-v1-1-games-copy`），发布最新版本 `20261125T053315Z-astra-home`。当前运行白名单共 880 个文件、31 条页面路由（含 `/projects/perfectmenu/`）、5 个相对链接、2 条外部跳转，共 `182,903,784` 字节；「手语游戏」现共 10 款（作品集桌面端 5 行两列平衡排布，首行并列「骷髅牌」与「完美一餐」），全站共 22 个作品。经 `publish_astra.py` 持锁 `/run/lock/nginx-deploy.lock` 全量校验切换，31 条主站路由、公网 1440／390px 验收及全部既有后台服务均正常。配置备份位于 `/etc/nginx/backups/shouyulove-home-20261125T053315Z-astra-home/`，维护记录位于 `/opt/shouyulove-maintenance/20261125-games-copy/`。

## 2026-11-25 主站首页与作品集上架「骷髅牌」（手语游戏首位）

黄庭逸已在阿里云一号机 `shouyulove-aliyun`（`101.37.209.227`）通过 `sign-games-ctl custom-add skull proxy 19087` 与 `xinchuangzu` 用户级常驻服务 `skull-table.service`（`/home/xinchuangzu/sign-games/skull`）部署 3–10 人实时联机手语牌桌游戏「骷髅牌」（`https://shouyulove.cn/games/skull/`）。按用户要求将其同步上架至以手予爱主站首页与作品集 `/portfolio/` 的「手语游戏」栏目首位（未改动或重启游戏本体与受管 Nginx 路由）：

- **绑定原稿、图标与字体重建**：先更新绑定原稿 `/Users/wishingcat/ObsidianNotes/AI Study/爱心社/心创组主站-以手予爱.md` 及副本 `content-source.md`（设计者黄庭逸，列于「手语游戏」第 1 位）；在 `project-logos/20261125-skull/` 设计柔和彩色牌垫图标（奶白骷髅牌与灰粉玫瑰牌交叠）；使用 `msdfgen v1.13` 完整重建覆盖 615 个中文用字的 `swei-spring-serif.syl-v1-1-skull.woff2`、`fonts.syl-v1-1-skull.css` 及双套 WebGL MSDF 图集（`syl-v1-1-skull`），保留全部旧版不可变资源与 CDN `assets.shouyulove.cn/v/20261020-flyinghands/`。
- **主站原子发布（`20261125T035923Z-astra-home`）**：运行白名单升级至 808 个文件、30 条页面路由（新增 `/projects/skull/`）、5 个相对链接、2 条外部跳转，共 `174,829,536` 字节（上一版本 `20261124T091501Z-astra-home`）；「手语游戏」现收录 9 项（首页桌面端 3×3 排布、作品集桌面端 4 行两列加末项跨列），全站共 21 个作品。经 `publish_astra.py` 持锁 `/run/lock/nginx-deploy.lock` 全量校验切换，30 条主站路由、4 条 308 跳转、2 条 `/where-to-study` 外部 302 跳转、`https://shouyulove.cn/games/skull/`（HTTP 200）、本地与公网无头浏览器（1440／390px）及全部后台服务（含 `skull-table.service` PID `3738568`）均核验通过。配置备份位于 `/etc/nginx/backups/shouyulove-home-20261125T035923Z-astra-home/`，维护记录位于 `/opt/shouyulove-maintenance/20261125-skull/`。

## 2026-11-24 为 `xinchuangzu` 开放全部 8 款手语游戏完整控制与替换部署权限

按用户要求在阿里云一号机 `shouyulove-aliyun`（`101.37.209.227`）为 `xinchuangzu` 开放「手语游戏」栏目下全部 8 款项目的完整修改、版本替换、下线删除、路由模式切换及数据备份/重置权限，同时继续保持不开放通用 `sudo` 与 `docker`：

- **专用协作组 `sign-games-dev`**：将 `xinchuangzu`（及管理员 `wishingcat`、`zhuxingye`）加入 `sign-games-dev`，对 5 棵手语游戏发布目录树（`/var/www/shouyulove-sign-games-releases`、`/var/www/shouyulove-signplay-releases`、`/opt/signplay-bank/releases`、`/opt/flyinghands/releases`、`/opt/shouyu-game/releases`）与自定义新游戏根目录 `/var/www/shouyulove-sign-games-custom` 配置 SGID `2775` 与默认 POSIX ACL（`d:g:sign-games-dev:rwx,d:o:r-x`）；在 `/home/xinchuangzu/sign-games/` 下建立全部快捷软链并更新 `~/README-使用说明.txt`。
- **受管 Nginx 片段与完整控制工具 `sign-games-ctl`**：将全部 8 款游戏的线上路由统一迁入受管片段 `/etc/nginx/snippets/sign-games-managed.conf`（状态存储于 `/var/lib/shouyulove-sign-games-ctl/routes.json`，备份位于 `/var/backups/shouyulove-maintenance/sign-games-full-control-20261124/`）。部署 `root:root 0700` 隔离脚本 `/usr/local/sbin/sign-games-ctl`（封装 `/usr/local/bin/sign-games-ctl`），经 `/etc/sudoers.d/91-xinchuangzu-sign-games`（`0440`，`visudo -c` 通过）仅授权 `xinchuangzu` 调用，支持：`status`、`releases`、`switch`、`delete-release`、`start|stop|restart|enable|disable|logs`（仅限 `signplay-bank`、`flyinghands`、`shouyu-game`）、`route <game> default|static|proxy <19000-19999>|disable`、`remove <game> [--purge-files]`、`custom-add/custom-delete <slug>`（`/games/<slug>/`）及 `data backup|reset`。每次路由修改均持 `/run/lock/nginx-deploy.lock`、通过 `nginx -t` 并失败自动回滚。
- **边界核验**：以 `xinchuangzu` 实测目录读写、版本切换与删除、`/games/qa-probe/` 上线返回 `200` 与删除清理、数据库在线备份均通过；通用 `sudo`、未授权服务/非 `19000–19999` 端口反代、路径穿越、非手语游戏站点写入及 `/etc/signplay-bank.env`、`/var/lib/flyinghands/admin.json`、`/var/lib/*`、`/root`、`/home/wishingcat` 读取均全部拦截；全部 8 款线上游戏返回 `200` 且 12 个后台服务 PID 不变。服务器维护说明位于 `/opt/shouyulove-maintenance/20261124-xinchuangzu-sign-games-access/README.md`。

## 2026-11-24 五款手语游戏静态站部署与主站联动上线

按用户确认将「炸飞机」「水果炸弹」「巴巴爸爸」「行动代号」「雪豹凶杀案」五个手语游戏（均由伍家阳设计）部署为阿里云一号机 `shouyulove-aliyun` 上的五条独立纯静态子路径，并同步接入主站首页与作品集「手语游戏」栏目：

- **五个游戏静态站与路由（`20261124T090628Z-sign-games`）**：本机分别整理于 `手语游戏/{炸飞机,水果炸弹,巴巴爸爸,行动代号,雪豹凶杀案}/`（仅同步白名单 `site/`，共 35 文件、`19,905,675` 字节，原压缩包留存本机未上公网），发布至 `/var/www/shouyulove-sign-games`，由 `/etc/nginx/snippets/sign-games.conf`（持锁 `/run/lock/nginx-deploy.lock` 接入 `/etc/nginx/sites-available/shouyulove`）提供 5 条入口：`https://shouyulove.cn/bombplane/`（双端分流页 + `/host/` 主持人端 + `/player/` 玩家端）、`https://shouyulove.cn/fruitbomb/`（双端分流页 + `/host/` + `/player/`）、`https://shouyulove.cn/barbapapa/`（含同级 `巴巴爸爸素材/` 10 张图与 `巴巴爸爸视频/` 9 段 MP4，支持 206 分段播放）、`https://shouyulove.cn/codenames/`、`https://shouyulove.cn/snowleopard/`。
- **专属柔和彩色图标与完整字体重建**：在 `project-logos/20261124-sign-games/` 新增 5 枚游戏主图标与 2 枚双端按钮小图标（`game-host.svg`、`game-player.svg`）。使用 `msdfgen v1.13` 完整重建覆盖 607 个中文用字的 `swei-spring-serif.syl-v1-1-five-games.woff2`、`fonts.syl-v1-1-five-games.css` 及双套 WebGL MSDF 图集（`PSTimesBody` 687 字、`Helvetica-neue` 679 字），彻底移除先前「配」字临时补充字形。
- **主站原子发布（`20261124T091501Z-astra-home`）**：运行白名单升级至 741 个文件、29 条页面路由（新增 `/projects/{bombplane,fruitbomb,barbapapa,codenames,snowleopard}/`）、5 个相对链接、2 条外部跳转，共 `167,147,840` 字节；作品集「手语游戏」现为 8 项（4 行两列），「炸飞机」「水果炸弹」在首页与作品集同步呈现「主持人端」「玩家端」双按钮。经 `publish_astra.py` 全量校验切换，全部 9 条游戏入口、29 条主站路由、公网 1440／390px 无头浏览器检查及 12 个既有后台服务 PID 均核验通过。配置与回滚备份位于 `/var/backups/shouyulove-maintenance/five-games-20261124/` 与 `/etc/nginx/backups/shouyulove-home-20261124T091501Z-astra-home/`，维护记录位于 `/opt/shouyulove-maintenance/20261124-five-games/`。

## 2026-11-24 主站首页与作品集新增「手语游戏」栏目

按用户要求在工作区新建 `手语游戏/` 目录并将「指间趣游」「飞手传书」「传情会意-手语版」三个项目从 `核心创意/` 整体移入（线上子站路由 `/signplay/`、`/flyinghands/`、`/chuanqinghuiyi/` 与服务保持不变），同步在绑定原稿、以手予爱主站首页与作品集 `/portfolio/` 的「核心创意」下方新增「手语游戏」栏目：

- **栏目排布与源码同步**：首页 `/` 顺序为「核心创意（5 项）→ 手语游戏（3 项：指间趣游 SignPlay、飞手传书、传情会意-手语版）→ 其他作品（4 项）→ 心创组内部使用（3 项）」；作品集 `/portfolio/` 顺序为「核心创意 → 手语游戏 → 心创组内部使用 → 其他作品」，「手语游戏」沿用与「核心创意」一致的两列醒目排版与独立标题锚点 `id="portfolio-games"`。新增栏目与简介用字 100% 落入现有 `syl-v1-1-shouxiaoyu-v2` 中文字体与 MSDF 图集内，未增加缺字补充。
- **主站版本与不可变资源**：线上切换至 `20261124T075334Z-astra-home`（上一版本 `20261116T055144Z-astra-home`，666 个运行文件、24 条页面路由、5 个相对链接、2 条外部跳转，共 `158,764,324` 字节）。新增三个不可变版本化静态资源 `shouyulove.syl-v1-1-sign-games.css`、`local-bridge.syl-v1-1-sign-games.js` 与 `portfolio-scene.syl-v1-1-sign-games.json`（均由 ECS 提供），既有旧版本资源与 CDN `assets.shouyulove.cn/v/20261020-flyinghands/` 保持不变。
- **发布与验收**：经 `publish_astra.py` 持锁 `/run/lock/nginx-deploy.lock` 完成 666 文件 SHA-256 逐项校验、`nginx -t` 及平滑重载；24 条页面路由、4 条站内 308 跳转、2 条 `/where-to-study` 外部 302 跳转与既有子站均通过，12 个服务器后台服务 PID 保持不变。本地 1440／390／320px 及公网 1440／390px 无头浏览器验收（零报错、零横向溢出、三款游戏入口均返回 200）通过。配置备份位于 `/etc/nginx/backups/shouyulove-home-20261124T075334Z-astra-home/`，服务器维护目录位于 `/opt/shouyulove-maintenance/20261124-sign-games/`。

## 2026-11-22 心创云盘白名单扩容与 `xinchuangzu` 非特权 SSH 账号

按用户要求在阿里云一号机 `shouyulove-aliyun`（`101.37.209.227`）完成两项配置：

- **心创云盘普通白名单成员**：通过 `shouyulove-drive-cli whitelist add` 新增手机号 `152****7606`（`role: user`，备注 `心创组成员`）。`/var/lib/shouyulove-drive/state.json` 保持 `0600 shouyulove-drive:shouyulove-drive`，`shouyulove-drive.service` 零重启热加载生效（白名单共 3 人：2 名超管 + 1 名普通成员）。核验 `/drive/api/state` 返回 `allowed: true, role: "user", isAdmin: false`，`/drive/api/agent/tree?path=/` 返回 `200`，管理接口 `/drive/api/whitelist/add` 返回 `403 ADMIN_ONLY`，未入白名单用户仍返回 `403 FORBIDDEN`。
- **非特权 SSH 协作账号 `xinchuangzu`**：创建 `uid=1003` 普通账号（仅附加组 `shouyulove-drive`，未加入 `sudo` 或 `docker` 组），登录命令 `ssh xinchuangzu@101.37.209.227`；家目录 `/home/xinchuangzu`（`0750`）下软链 `~/drive` → `/srv/shouyulove-drive/files`，预建 `~/projects`（`0750`）、`~/.ssh/authorized_keys`（`0600`）与 `~/README-使用说明.txt`，并开启 `loginctl enable-linger xinchuangzu` 以支持无需 `sudo` 的 `systemctl --user` 常驻部署。新增 `/etc/ssh/sshd_config.d/90-xinchuangzu-password.conf`（`Match User xinchuangzu`）仅对该账号开启密码登录，经 `sshd -t` 检查并平滑 reload `ssh.service`，原有账号（`root`/`wishingcat`/`zhuxingye`/`tunnel`）SSH 策略及全部 12 个业务服务 PID 均保持不变。实测密码登录、`sudo`/`docker` 拒绝、`~/drive` 与 `~/projects` 读写删、敏感目录隔离及 `systemctl --user` 均通过。
- **凭据与备份**：初始密码仅保存在本机仓库外 `0600` 凭据文件，不进入 Git 或公开目录；服务器变更前备份位于 `/var/backups/shouyulove-maintenance/xinchuangzu-20261122/`，非秘密说明归档于 `/opt/shouyulove-maintenance/20261122-xinchuangzu-account/`。

## 2026-11-18 奶家麻将独立跳转入口（`/NaiMahjong/`）

按用户要求在 `shouyulove-aliyun` 共享 Nginx 新增独立路由片段 `/etc/nginx/snippets/naimahjong.conf`（由 `/etc/nginx/sites-available/shouyulove` 引用，不加入以手予爱主站首页与作品集 `/portfolio/`，主站运行版本维持 `20261116T055144Z-astra-home` 不变）：

- `https://shouyulove.cn/NaiMahjong` 与 `https://shouyulove.cn/NaiMahjong/` 均以 `302`（`Cache-Control: no-store`）直接跳转至合作主机 `http://39.96.206.228:8444/`，完整保留查询参数（如 `?room=123456`）；
- 其他大小写形式（如 `/naimahjong`、`/naimahjong/?room=123456`）先 `302` 规范化至 `/NaiMahjong/` 并保留参数，子路径 `/naimahjong/<rest>` 同步跳转至对应上游路径；
- 持锁 `/run/lock/nginx-deploy.lock` 完成 `nginx -t` 与平滑 reload，12 个既有后台服务（`system-shouyulove.slice` 11 个单元及 `pinhaoke.service`）PID 与运行状态保持不变，主站及 10 个子站巡检全部返回 `200`。配置备份与验收回执位于 `/var/backups/shouyulove-maintenance/naimahjong-20261118/20261118T125814Z/`，非秘密说明归档于 `/opt/shouyulove-maintenance/20261118-naimahjong/`。撤销时持锁恢复 `shouyulove.before`、移除 `/etc/nginx/snippets/naimahjong.conf` 并验证重载即可。

## 2026-11-18 云盘文件操作与以手寻语 HTTP 修复

- 心创云盘运行版本为 `20261118T013142Z`，仓库提交为 `573c384`。覆盖移动失败时保留原文件，ZIP 超过 4 GiB 时使用 ZIP64，单次超过 10,000 项会在传输前报错。39 个发布文件的 SHA-256 与仓库一致，代码属主为 `root:shouyulove-drive`。独立解压校验通过，正式主机使用临时存储通过 7 项测试。
- 以手寻语运行版本为 `20261118T013309Z-http-encoding-2e0eead4a`，仓库提交为 `2e0eead`。首页、词汇页和公共静态资源支持 HEAD 巡检，请求指定 gzip 权重为零时返回原始内容。离线载荷预览可在没有模型密钥的环境运行。已核对 37 个运行文件。

## 2026-11-17 心创云盘界面整体重构（`shouyulove-drive`）

`https://shouyulove.cn/drive/` 发布 `20261117T003512Z`（上一版本 `20261115T103534Z`，云盘仓库提交 `7546a0e`）。页面由深色方案改为只有浅色一种外观的暖纸面工作台：左侧目录树与刻度尺存储条，右侧文件区，管理设置改为独立对话框，统一通行证悬浮窗以浅色主题打开。静态资源改为带内容版本号的地址（`?v=`），接口、Nginx 片段、存储卷与权限均未变化；发布过程重启了 `shouyulove-drive.service` 与 `shouyulove-drive-fb.service` 并持锁重载 Nginx。发布后核验：两项服务与 Nginx 均为 `active`，`/drive/` 返回 200 且占位符全部替换，访客接口不返回成员名单与令牌，`/drive/files/` 仍归并回 `/drive/`，无头浏览器在 1440、390、320 三种宽度下无横向溢出、无控制台报错，主站首页与作品集的云盘入口均可打开。主站本身未重新发布。

## 2026-11-16 首页与作品集通行证卡片同步为双入口按钮

首页与作品集「心创组内部使用」分区的「手语分社统一通行证」卡片同步改为两个独立按钮：「通行证主页」（`https://shouyulove.cn/auth/`）与「接入与配置中心」（`https://shouyulove.cn/auth/dev`，仅超级管理员可进入），各带一枚同系列小图标（源文件 `project-logos/20261113-shouyu-pass/pass-home.svg` 与 `pass-console.svg`）。卡片本身不再整体可点，也不在卡片内显示简介，两个按钮直接放在标题下方、设计者上方，沿用 `data-project="shouyu-pass"` 计入作品集跳转统计；「心创组内部使用」分区三张卡片（接锅、手语分社统一通行证、心创云盘）的左侧图标统一与右侧文字垂直居中对齐。原稿简介保留，作品详情页 `/projects/shouyu-pass/` 照常显示。

- **主站版本**：`20261116T055144Z-astra-home`（663 个运行文件、24 条页面路由、5 个相对链接、2 条外部跳转，共 `158,647,863` 字节；同日先前两次作品集单页发布为 `20261116T053402Z-astra-home` 与 `20261116T053836Z-astra-home`，再上一版为 `20261114T123404Z-astra-home`）。
- **实现与发布方式**：本机缺少完整重建所需的历史字体与构建记录目录，因此在当前线上运行包副本上增量更新并经 `publish_astra.py` 逐文件校验切换。作品集由 `scripts/build_content.py`（绑定原稿「入口：」行、`ENTRY_ICONS`、`entry_icon`）与 `styles/portfolio.css` 生成；首页卡片由打包运行时渲染，新增独立脚本 `scripts/project_entries.js`（线上 `/assets/project-entries.syl-v1-1-20261116.js`，由 ECS 提供，23 个 Nuxt 页面引入，样式来自 `styles/project-entries.css`，版本常量 `PROJECT_ENTRIES_VERSION`）在页面加载后把简介替换为双按钮。
- **字体**：按钮文字中的「配」（`U+914D`）不在 `syl-v1-1-shouxiaoyu-v2` 中文子集内，已在作品集页面与 `sites/immersive-g-com-955afd14/shared/assets/project-entries.syl-v1-1-20261116.js` 临时内嵌仅含该字的补充字形（844 字节）。下次完整重建前须先重新生成并升级中文字体版本，届时一并移除两处补充字形。
- **记录**：服务器维护目录 `/opt/shouyulove-maintenance/20261116-pass-entries/`（含 `stage-3/`），配置备份 `/etc/nginx/backups/shouyulove-home-20261116T055144Z-astra-home/`。本地与公网 1440／390／320px 无头浏览器验收通过。

## 2026-11-16 手语分社统一通行证全站更名与暖色视觉重构（`shouyulove-auth`）

位于 `心创组内部使用/手语分社账号/` 的认证服务对外名称全面统一为「手语分社统一通行证」（覆盖登录页、SDK 悬浮窗、控制台与门禁页、后端提示、CLI、接入指南与 `package.json`，仅本机目录名保持不变），并分两步完成页面视觉与交互重构上线：

- **通行证主页 `https://shouyulove.cn/auth/`（线上版本 `20261116T042852Z`，提交 `5741457`）**：撤下短暂试用的石膏浮雕版（`236a8e6`），改为独立的暖色天光风格。背景由 `src/web/glow.js` 渲染奶油黄、杏色与珊瑚粉流动天光（无 WebGL 自动降级为静态暖色渐变，系统开启「减少动态效果」时关闭动画）；左侧为摊开手掌托起跳动发光爱心（点击散出小爱心）与「手语分社统一通行证」大字；右侧为半透明暖白卡片与珊瑚红渐变高光按钮，已登录状态以深暖色倾斜反光票卡展示脱敏手机号；页脚统一为「北京大学爱心社手语分社　设计者：涂增基」，并精简全页提示文案。
- **接入与配置中心 `https://shouyulove.cn/auth/dev`（线上版本 `20261116T050830Z`，提交 `4da17af`，文档同步 `7e27979`）**：与主页共用 `glow.js` 暖色天光体系，将原单长页拆分为顶部滑块切换的三个视图——「项目」（左侧项目卡片、右侧固定新建/编辑表单）、「成员与权限」（全站超级管理员名单与三级身份说明）与「接入文档」（三种接入方式卡片、代码示例、字段对照、端点与可折叠常见问题），兼容旧锚点 `#super-gov`、`#methods`、`#recipes`、`#endpoints` 自动切到对应视图；门禁页（`dev-gate.html`）简化为单卡片并统一跳转 `/auth/?return_to=/auth/dev`。同步修复管理员授撤提示读取层级错误、底部浮层通知自动消失、增删管理员清空其他卡片输入、SDK `<script type="module">` 顶层 `await` 示例语法、切换账号直达登录表单及项目表单前端校验。外部子站嵌入悬浮窗 `modal.css` 暂维持原样式；`npm test` 10 项测试与 1440／390／320px 无头浏览器验收全部通过。

## 2026-11-14 全站网页访问统计核查与补齐

已完成阿里云一号机（`shouyulove-aliyun`）与北大知道主机（`yanyuan-calendar`）上全部站点的统计核查：拼好课（`/var/lib/pinhaoke/访问统计.db`）、北大／清华知道（`/var/lib/yanyuan-calendar/访问统计.sqlite` + `广告点击.sqlite`）及海王求职（`/var/lib/zhaopin-zhidao/auth.sqlite`）均持续正常统计；位于 `yanyuan-calendar` 的 `wisact.pkuknow.cn` 维持 `access_log off;` 边界未作改动。

在 `shouyulove-aliyun` 侧完成四项统计补齐：补全近期上线项目名称映射并合并分裂的项目健康观测键；为 `https://shouyulove.cn/where-to-study/` 接入外部网关 `GET 302` 采集并从日志一次性补回 2026-11-11 起 233 次跳转访问；将心创云盘 `/drive/files/` 改为仅上报私有 Unix 数据报并在采集端脱敏为 `/drive/files/`；为 `https://tuzengji.com/`（未改任何静态字节，17/17 文件发布校验一致）接入隔离表 `site_visits` 与 `tuzengji-stats` 命令，并补入 2026-10-31 至 11-14 的 1,553 次访问。12 项 Python 与隔离 Nginx 回归、全站 `ShouYuLove-QA` 无污染探针与 `PRAGMA integrity_check` 全部通过；备份与一次性回补回执位于 `/var/backups/shouyulove-stats/20261114-all-sites/`，维护说明归档于 `/opt/shouyulove-maintenance/20261114-stats-audit/`。详见 [后台统计说明](private-statistics.md)。

## 2026-11-14 手小语展示页上线并接入作品集（`/shouxiaoyu/`）

手语分社微信群陪伴伙伴「手小语」展示页已上线 `shouyulove-aliyun`（`101.37.209.227`）：正式入口 `https://shouyulove.cn/shouxiaoyu/`，聚焦微信群日常陪伴、聊天水群、接梗斗图与看图猜手语（不含天气播报）。

- **主站与作品集联动**：主站发布 `20261114T123404Z-astra-home`（662 个运行文件、24 条页面路由、5 个相对链接、2 条外部跳转，共 158,632,740 字节；上一版本 `20261114T075210Z-astra-home`）。作品集共 15 个作品，桌面端「核心创意」4 行两列中第 3 行并列展示「手小语」（设计者涂增基，柔和彩色图标位于 `project-logos/20261114-shouxiaoyu/`）与「传情会意-手语版」；数据桥与作品集场景版本为 `syl-v1-1-shouxiaoyu-v3`，图像、字体（中文覆盖 565 字）与运行模块保持 `syl-v1-1-shouxiaoyu-v2`，由 ECS 提供，既有 CDN 资源 `/v/20261020-flyinghands/` 保留。
- **静态子站与隐私边界**：本机源码位于 `核心创意/手小语/`（origin `git@github.com:tuzengji/shouxiaoyu.git`），线上仅同步纯静态 `site/` 目录至 `/var/www/shouyulove-shouxiaoyu-releases/20261114T123437Z-shouxiaoyu/shouxiaoyu/`（符号链 `/var/www/shouyulove-showcase`），由 `/etc/nginx/snippets/shouxiaoyu.conf` 直接托管（同步移除此前的 `/projects/shouxiaoyu*` 404 临时拦截）。展示页直接使用手小语微信头像作为 Logo，通过五个主题集合展示 34 张纯深色手机端脱敏群聊截图（已剔除私聊图与白色桌面截图、移除张数角标及「福瑞庭审」顶部多余按钮并遮盖二维码及群友实名备注），原始设计文档、`qa/` 与本地脱敏脚本不进入线上发布目录或公开仓库。

## 2026-11-14 心创云盘上线、扩至 100 GB 并升级为一体化工作台（`shouyulove-drive`）

心创组内部共享网盘与智能协作空间已上线 `shouyulove-aliyun`（`101.37.209.227`）：一体化完整网页云盘 `https://shouyulove.cn/drive/`（页面直出多级目录、拖拽上传文件与文件夹、在线新建/预览/编辑文档、重命名/移动与流式 `.zip` 打包下载，已取消二级跳转；旧 `/drive/files/` 访问自动归并回 `/drive/` 对应目录，底层兼容二进制为 `/opt/shouyulove-drive/bin/filebrowser` `v2.63.23`）。

- **主站与作品集联动**：主站发布 `20261114T051119Z-astra-home`（538 个运行文件、23 条页面路由、5 个相对链接、2 条外部跳转，共 144,466,376 字节；上一版本 `20261113T044411Z-astra-home`）。在首页与作品集「心创组内部使用」分区新增「心创云盘」（设计者涂增基，柔和彩色图标位于 `project-logos/20261114-xinchuang-drive/`），共 14 个作品；新增资源版本为 `syl-v1-1-xinchuang-drive`（中文覆盖 556 字），由 ECS 提供，既有 CDN 资源 `/v/20261020-flyinghands/` 保留。
- **共享存储池与在线扩容边界**：独立稀疏可扩容 ext4 磁盘镜像 `/var/lib/shouyulove-drive/volume.img` 初始划分 `60 GB` 并已在线零停机扩容至 `100 GB`（实际宿主机仅占写入体积，挂载 `/srv/shouyulove-drive`，共享读写目录 `/srv/shouyulove-drive/files`，软链 `/srv/drive` 及各用户 `~/drive`、`~/projects/drive`）。采用 `2777` 目录、`0666` 文件、`UMask=0000` 及默认 POSIX ACL（`other::rwx`），服务器上的任意进程与拥有服务器权限的伙伴无需额外用户组即可直接自由读写；支持控制台或 `shouyulove-drive-cli resize <GB>` 经 `/usr/local/sbin/shouyulove-drive-resize` 在线持续扩容。
- **服务架构与认证边界**：本机源码位于 `心创组内部使用/心创云盘/`（origin `git@github.com:tuzengji/ShouYuLove-Drive.git`），服务器当前发布位于 `/opt/shouyulove-drive/releases/20261117T003512Z` → `/opt/shouyulove-drive/current`。`shouyulove-drive.service` 监听 `127.0.0.1:8768`，`shouyulove-drive-fb.service` 监听 `127.0.0.1:8769`，均归属 `system-shouyulove.slice`。Web 端通过统一通行证当前页悬浮窗免跳转登录，经 `/etc/nginx/snippets/shouyulove-drive.conf` 调用 `shouyulove-auth` `auth_request /_syl_auth_optional/drive`，由 `X-Shouyu-User-Phone-Hash` 判定白名单并结合 `X-Shouyu-User-Role` 判定分级权限（`191****0323` 与 `152****6060` 为全站超级管理员，连同受权的 `drive` 项目管理员可调用「管理与接入设置」；其余普通白名单成员隐藏管理面板并享有完整网盘存取权限；`/var/lib/shouyulove-drive/state.json` 仅存哈希与脱敏号，不存明文手机号）；本机回环 `/drive/api/agent/*` 免密直连，远程协作支持签发 Bearer Token。

## 2026-11-13 手语分社统一通行证上线并接入作品集（`shouyulove-auth`）

手语分社独立账号与单点登录基础设施已上线 `shouyulove-aliyun`（`101.37.209.227`）：用户通行证登录页 `https://shouyulove.cn/auth/`，**仅全站超级管理员可访问**的接入与配置中心 `https://shouyulove.cn/auth/dev`（原 `/auth/手语分社统一通行证接入指南.md` 与 `/auth/guide.md` 同步整合至 `/auth/dev#recipes` 并受超级管理员权限保护）。

- **主站与作品集联动**：主站发布 `20261113T044411Z-astra-home`（477 个运行文件、22 条页面路由、5 个相对链接、2 条外部跳转，共 137,472,614 字节；上一版本 `20261111T013217Z-astra-home`）。在首页与作品集「心创组内部使用」分区新增「手语分社统一通行证」（设计者涂增基，柔和彩色图标位于 `project-logos/20261113-shouyu-pass/`），桌面与「接锅」两列并排展示、窄屏单列排列；新增资源版本为 `syl-v1-1-shouyu-pass`（中文覆盖 551 字），由 ECS 提供，既有 CDN 资源 `/v/20261020-flyinghands/` 保留。
- **应用与账号数据边界**：本机源码位于 `心创组内部使用/手语分社账号/`，服务器发布位于 `/opt/shouyulove-auth/releases/20261113T041013Z` → `/opt/shouyulove-auth/current`，`shouyulove-auth.service` 监听 `127.0.0.1:8767`（纳入 `system-shouyulove.slice`）；独立加密账号库 `accounts.sqlite`（手机号 AES-256-GCM 加密 + HMAC 索引、密码 scrypt 哈希）、主密钥与 JWT 密钥位于 `/var/lib/shouyulove-auth/`（`0700`/`0600`），`shouyulove-auth-backup.timer` 每日两次热备至 `/var/backups/shouyulove-auth/`。
- **短信认证、三级角色与超管专属接入中心**：短信验证复用阿里云 `dypnsapi` 与 ECS 实例 RAM 角色 `ShouYuLoveSmsVerifyRole` 免密钥方案（配置于 `/etc/shouyulove-auth/sms.json`），支持未注册手机号验证码登录时自动完成注册。全站采用三级角色体系：`191****0323` 与 `152****6060` 为全站超级管理员，拥有全站与所有已接入项目的管理权限并可任命其他超级管理员及各项目定制管理员；各接入项目可隔离授撤本项目管理员身份，未指定的项目内权限与普通用户一致。`/auth/dev`、`dev.js` 及 `/auth/api/dev/*` 由服务端校验仅限全站超级管理员访问（未登录展示超管登录引导门户，非超管已登录返回 `403` 提示切换超级管理员），并直接在网页内集中展示全部同域/SPA/OIDC/JWKS/Roles API/`shouyulove-auth-cli` 接入与配置方法。

## 2026-11-11 拼好课迁入 `shouyulove-aliyun`（`101.37.209.227`）

按用户授权，将「拼好课 Pinhaoke」（`https://www.pinhaoke.love/`、`https://pinhaoke.love/`）从 `8.140.215.49`（`i-2zeci8v2bkvj5dyy4yr9`）零停机迁入 `shouyulove-aliyun`（`101.37.209.227`）。代码与只读课表库位于 `/opt/pinhaoke`，`pinhaoke.service` 监听 `127.0.0.1:8000`；三份可写 SQLite 库位于 `/var/lib/pinhaoke/`，`pinhaoke-backup.timer` 每日两次快照至 `/var/backups/pinhaoke/`。独立虚拟主机 `/etc/nginx/sites-available/pinhaoke` 接入本机 Certbot 自动续期，DNS 的 `@` 与 `www` 已切至 `101.37.209.227`；源机 `8.140.215.49` 已停止本地业务与定时任务，仅保留过渡反代与磁盘冻结备份。

## 2026-11-11 去哪自习固定入口

正式入口为 https://shouyulove.cn/where-to-study/ 。带斜杠和不带斜杠两种写法均通过 302 直接跳转至 https://39.96.206.228/ ，查询参数保留，响应不缓存。首页、作品集、项目详情和绑定原稿使用新入口；项目仍在原服务器运行。

主站版本 `20261111T013217Z-astra-home`，运行白名单 415 个文件、21 条页面路由及两条外部跳转。图标、字体与运行模块沿用上一版；页面数据更新为 `syl-v1-1-where-to-study`，两份新数据文件由现有 ECS 提供，既有 CDN 与旧资源保留。

跳转目标记录在 `deploy/project-redirects.json`，本地预览和发布核验读取该文件；线上 Nginx 规则位于 `deploy/nginx-home.locations.conf`，修改目标时须同步两处。发布器在切换后检查普通请求与含参数请求，失败时恢复上一版。Nginx 重载期间可能由旧进程短暂处理请求，发布检查会等待新跳转规则就绪，再严格核对目标地址。

上一版本为 `20261110T155641Z-astra-home`。证据位于 `output/deployment/where-to-study-20261111/`，服务器维护目录为 `/opt/shouyulove-maintenance/20261111-where-to-study/`。

## 2026-11-10 去哪自习入口

新增「去哪自习」，设计者为王宁静，归入其他作品。首页、作品集和详情页直接链接至 https://39.96.206.228/ ，共用书页与定位标记图标。作品集通过条目中的「作品集署名：显示」字段显示本项目署名，其他作品的原有署名设置保留。

主站版本 `20261110T155641Z-astra-home`，运行白名单 413 个文件、21 条页面路由、12 个项目。新资源版本为 `syl-v1-1-quna-study`，中文覆盖 545 字；SVG、透明 PNG 和小尺寸图标位于 `project-logos/20261110-quna-study/`。

本次 57 个新增资源由现有 ECS 提供，共 6,671,534 字节；既有 CDN 对象继续使用 `/v/20261020-flyinghands/`，原 `cdn-manifest.json` 保留。新增资源清单为 `origin-asset-manifest.json`。系统上传选择器无法确认选择，本次未上传新 CDN 版本；后续可按常规 CDN 流程发布新前缀，不能把本机候选 CDN 包当作已上线。

发布与浏览器验收记录在 `output/deployment/quna-study-20261110/`，服务器维护目录为 `/opt/shouyulove-maintenance/20261110-quna-study/`。上一版本为 `20261020T123649Z-astra-home`。

## 2026-10-28 腾讯旧机退役与系统重装

按用户确认，将北京七区腾讯轻量服务器 `lhins-rarfnokk`（系统元数据实例号 `ins-fkge8gwd`）重装为纯净 Ubuntu 22.04.5 LTS。公网 IP `49.232.193.175`、4 核 / 4 GB / 40 GB 套餐和实例保留；使用维护者原有 SSH 公钥登录 `ubuntu`。重装后的系统盘占用约 4.6 GB，公网 TCP 只监听 22，旧项目目录与业务进程已不存在。

重装前保留系统盘快照 `lhsnap-0ts9hm86`（`Snapshot-20261028105033`，2026-10-28 10:50:37 创建）。控制台已确认快照状态为“正常”，回滚入口可用。旧燕园图寻、时间秘书、SignTrace、年终总结、词典备用工程和历史站点均退出这台服务器。

阿里云只局部移除旧 SignTrace 任务的 `28018` 回源、年终总结的 `28042` 会话分流，以及对腾讯旧 IP 的真实地址信任。旧迁移隧道停止并禁用后，七个 `280xx` 端口均已消失；主站、作品集、词典、SignTrace、传情会意及年终总结返回 200，不存在的 SignTrace 任务返回 403。词典沿用阿里云本机 `18080/18081` 的 CLab 直连。

共享 Nginx 修改持有 `/run/lock/nginx-deploy.lock`，配置检查和平滑重载通过；九个已核对业务服务的 PID 与状态保持。主站仍为 `20261020T123649Z-astra-home`。配置备份与验收回执位于阿里云 `/var/backups/shouyulove-maintenance/tencent-retirement-20261028/20261028T024922Z/`，本机证据位于 `output/deployment/tencent-reset-20261028/`。

本节替代下方迁移记录中“腾讯旧机仍需保留”的当前状态；旧记录保留用于追溯，不能据此恢复已退役的兼容路由。

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

## 服务器当前职责

| 服务器 | 当前职责 | 维护入口 |
| --- | --- | --- |
| 阿里云 `101.37.209.227` | 以手予爱主站、全部同域子项目、词典 CLab 直连与会话保护、全站私有统计（含 `tuzengji.com`）及拼好课 Pinhaoke | `ssh shouyulove-aliyun` |
| 阿里云 `121.43.143.226` | 北大知道、清华知道与公众号后台服务，由其项目独立维护 | `ssh yanyuan-calendar` |
| 腾讯云 `49.232.193.175` | 2026-10-28 已重装为纯净 Ubuntu 22.04.5，旧项目与迁移隧道均已退役 | `ssh ubuntu@49.232.193.175`（现有密钥） |

以手予爱所在 ECS 为杭州 `i-bp1hi3u3w5p3vg4owfl0`，公网带宽 5 Mbps；拼好课已于 2026-11-11 从原 `8.140.215.49` 零停机迁入本机。主站保留北大知道、清华知道、拼好课及去哪自习（`/where-to-study/` → `https://39.96.206.228/`）的导航与跳转入口。

## 部署协作账号

2026-10-15 按用户最终确认，在阿里云 `101.37.209.227` 创建 `zhuxingye`，授予完整、免密码的 sudo 权限。登录命令为 `ssh zhuxingye@101.37.209.227`，项目目录为 `/home/zhuxingye/projects`，登录后可用 `sudo -i` 进入管理员 shell。

登录沿用旧腾讯同名账号最近使用的 SSH 公钥；未复制其 CLab 和其他设备公钥。账号密码锁定，服务器继续关闭密码登录。sudo 规则位于 `/etc/sudoers.d/90-zhuxingye`，仅 root 可写。新增账号未改动原 SSH/Nginx 配置、现有发布链接或服务进程。

已检查目录与公钥文件权限、`visudo -c`、`sshd -t`，并以该用户执行 `sudo -n id -u` 得到 `0`；SSH 公钥探测确认服务器接受已配置的公钥。实际签名登录需账号持有人使用自己的私钥完成，维护过程未索取私钥。

后续修改共用 Nginx 时继续使用 `/run/lock/nginx-deploy.lock`，先验证配置再 reload。账号配置与验收记录在本机 `output/deployment/zhuxingye-account-20261015/`，服务器回执为 `/var/backups/shouyulove-migration/20261015/zhuxingye-account-result.json`；本次维护说明同步至 `/opt/shouyulove-maintenance/20261015-zhuxingye-account/`。

## 迁移交接时的发布与服务（2026-10-15 历史基线）

主站 `/var/www/shouyulove-home` 当时指向 `20261014T162210Z-astra-home`，SignPlay `/var/www/shouyulove-signplay` 指向 `20261015T020134Z-signplay`。当时主站清单为 **255 个文件、19 条页面路由、5 个相对链接、111,756,084 字节**，作品集共 **10 个项目**。后续新增项目与现行服务清单以本文顶部最新章节及 [迁移与维护](../迁移与维护.md) 为准。

当时六个服务（`signtrace`、`shouyu-game`、`jieguo`、`sign-language-festival`、`sign-year-end-summary`、`shouyulove-stats`）率先纳入 `system-shouyulove.slice`（CPUQuota 200%、CPUWeight 20、MemoryHigh 2G、MemoryMax 3G；SignTrace 保留两检索 worker 和四核亲和性），后续新增的 `signplay-bank`、`flyinghands`、`shouyulove-auth`、`shouyulove-drive`、`shouyulove-drive-fb` 同样归属该 slice。

## 迁移、统计和证书（2026-10-15）

- 2026-10-15 15:51:40–41，根域与 www 解析切到新 ECS；两台权威 DNS 均核对通过。最终数据同步约 24 秒，临时 gate 排队和错误均为 0。gate 已退出，当前 unit 为 `inactive`，Nginx 直连新机服务；当时保留的腾讯 `280xx` 中转端口与旧机业务已在 2026-10-28 重装退役中全部移除。
- 旧统计的 1,528 次页面访问一次导入，固定去重密钥保留；新机持续接收新访问。源端采集器已停止并禁用，不能重新开启造成重复统计。统计范围、查看命令见 [后台统计说明](private-statistics.md)。
- 迁移验收共 190 项最终通过；其中一项首次 TLS 连接失败，独立复验两次均通过，原始结果保留。1440px 桌面和 390px 手机的首页、作品集已验证，完整 WebGL、延后场景和导航保持。
- 新证书覆盖根域和 www，有效至 2027-01-13。Certbot webroot、专属 hook、timer 及仅本域的续期 dry-run 均通过；后续运维命令见 [阿里云配置说明](../deploy/aliyun/README.md)。

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
