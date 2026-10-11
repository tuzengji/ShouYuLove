# 以手予爱 ShouYuLove 主站

[以手予爱](https://shouyulove.cn/) 的心创组介绍与作品导航，采用现有 Astra/Nuxt、GSAP 和 WebGL 运行层。

本仓库保存当前已公开的精确静态版本：245 个运行文件、16 条页面路由、5 个相对资源链接，共 110,371,364 字节。本机已绑定用户指定 MD 为正文文本源，公开文案已按最新原稿同步，第一届成员为 13 人（包含李昌昊）；七个作品图标的底色透明度为 28%，边缘保持宽幅不规则渐隐，图案完全不透明，融入浮雕背景；图片和标题居中，介绍与署名左对齐；作品目录悬停改为标题深绿色与 3px 位移，署名保持原位；接锅入口为 `/catchpot/`。文件白名单、大小及 SHA-256 见 [runtime-manifest.json](runtime-manifest.json)。2026-10-11 当前发布版本为 `20261011T031026Z-astra-home`。

作品集独立使用轻量 HTML，正式入口为 `/portfolio/`，原 `/projects/` 自动跳转；名称、分类和设计者先显示，整行直接访问对应项目。完整原生三维程序在首次绘制至少两秒后后台加载；该页面不加载音乐。手机「添加到桌面」直接进入新入口。

首页继续只预载当前场景，心创组与页脚按需加载，保留现有音乐行为；版本化资源使用一年 immutable 缓存，HTML 和 payload 使用 no-cache。

## 验证、恢复与本地预览

只需 Python 3.9+ 和支持相对符号链接的文件系统，不需要 npm、pip 或重新构建：

```sh
python3 -B scripts/runtime_snapshot.py verify
python3 -B scripts/runtime_snapshot.py export output/runtime
python3 -B serve.py --directory output/runtime --port 8038
```

打开 `http://127.0.0.1:8038/`，结束时使用 Ctrl-C。导出工具按清单复制文件和链接，校验每个文件并拒绝覆盖已有目标；再次导出时请指定一个新的目录。导出的目录只包含运行白名单，源码、说明和版本历史不会混入。

验证已有独立副本：

```sh
python3 -B scripts/runtime_snapshot.py verify --directory output/runtime --exact
```

当前版本已退出旧 esbuild/garden 工程；不要恢复旧 `package.json`、`home-assets/` 或已退出展示的页面。

## 维护源码

`scripts/content_source.py` 解析本机正文源绑定，`content-source.md` 保存成功构建生成的公开文案副本；`styles/shouyulove-v1-1-jieguo.css` 保存当前样式，`styles/project-logo-mask.svg` 保存 HTML 与 WebGL 共用的不规则边缘遮罩。`scripts/build_content.py` 生成页面与运行资源，`scripts/optimize_runtime.py` 应用场景加载、手机纹理和图标边缘补丁，`scripts/fast_bootstrap.js` 衔接 HTML 与原生视图。中文子集与图集覆盖 358 字，字体缓存名由独立 `FONT_VERSION` 管理。四个回归检查覆盖文本源绑定、批次间字标刷新、每页共享字标和实际 HTTP 缓存响应。

维护脚本保留实际原始素材的读取约定，完整内容重新生成还需要本机保存的素材：

- `output/deployment/shouyulove-content-v1/v0-backup.json` 中对应的项目内 V0 原始页面与共享素材。
- `主站版本归档/20261001-120733-Astra替换前/source/home-assets/images/` 中使用的两个站点图标。
- `output/deployment/shouyulove-home-shortcut-20261011/font-source/` 中的当前字体源、子集与中文图集。
- 六个透明 Logo 原图、`music/` 中的既有音乐，以及字体候选清单指定的预览和许可文件。
- `output/deployment/shouyulove-fast-20261009/mobile-textures/` 中的两张手机纹理。重建脚本为 `scripts/prepare_mobile_textures.py`，使用固定版本 Khronos KTX-Software 4.4.2；已生成的纹理也在运行快照中。

克隆可独立恢复现有站点。完整内容重建还需上述原始素材；构建脚本会重建固定的 `output/shouyulove-jieguo-site/`，运行前保存已有输出。

源码回归检查使用 Python 3.13 和以下依赖：

```sh
python3 -m pip install -r requirements-build.txt
python3 -B -m unittest discover -s tests -v
```

回归测试自行创建临时页面与输入，不要求 V0 或完整字体。需要新增字形或重新生成音乐时，另外使用对应的 `prepare_chinese_font.py` / `prepare_music.py`；这些生成步骤依赖 fontTools/Brotli、NumPy、SciPy、FFmpeg，以及固定版本 msdfgen v1.13，不能用它们替代运行快照恢复。

## 发布和许可

按白名单使用既有主站发布流程，见 [部署说明](deploy/README.md)。按用户要求，后续修改需同步推送仓库并更新既有服务器部署；另有明确要求时从其要求。

保留 [第三方许可与归属说明](THIRD_PARTY_NOTICES.md)。公开仓库不包含凭据、服务器状态快照、内部交接、研究材料或历史大目录。

## 正文文本源绑定

本机 `.content-source-path` 保存正文 MD 的绝对路径（一行 UTF-8），该配置由 Git 忽略。修改主站文案时先同步修改该 MD；`scripts/build_content.py` 和 `scripts/prepare_chinese_font.py` 均直接读取绑定原稿，成功构建自动更新仓库的 `content-source.md` 副本。已绑定原稿不可读取时，构建会停止；没有本机绑定的克隆使用仓库副本。

文字更新流程：编辑绑定 MD，检查新增用字与对应字体版本，构建并检查电脑、手机页面，再提交推送和更新既有服务器部署。

## 导航回归

`tests/project_navigation.js` 覆盖原生首页进入独立作品集、返回及历史切换，可交给 Playwright CLI 的 `run-code`，在已打开的本地预览或部署标签执行；先创建 `output/playwright/project-navigation/` 保存截图。用例创建并关闭独立的桌面与手机上下文，覆盖原生按钮打开独立目录、返回首页与前进后退。

## 手机添加到桌面

作品集手机端右下角提供「添加到桌面」，位于页面右下角；支持浏览器原生安装提示，未提供提示时显示 iPhone、其他浏览器或内置浏览器的操作指引。已从桌面以独立窗口打开时隐藏按钮，快捷入口直接进入 `/portfolio/`。安装清单只覆盖作品集路径；没有新增 Service Worker 或更改页面缓存。

按钮和指引文案由绑定 MD 的「添加到桌面」章节生成。`scripts/home_shortcut.js` 处理安装提示与站内路由，初始 HTML 阶段即可使用。`tests/home_shortcut.js` 可通过 Playwright CLI 的 `run-code` 执行，先创建 `output/playwright/home-shortcut/`；覆盖手机、窄屏、横屏、原生提示分支、指引关闭、站内切换、独立窗口和桌面隐藏。原生提示结果通过事件替身检查，实际系统安装需由用户在设备上确认。

## 2026-10-11 轻量作品集与私有统计

作品集正式入口改为 `/portfolio/`，`/projects`、`/projects/`、`/projects/index.html` 使用 308 跳转，查询参数保留。七个作品详情原地址保留。作品目录由绑定 MD 直接生成 HTML，保留三个分类、名称和设计者，整行链接直接打开对应项目；字体或 JavaScript 未完成时也可以使用。

作品集不启动 Nuxt/WebGL、预加载场景或音频，背景仅在正文首次绘制至少两秒后低优先级加载既有石膏纹理；减少动态效果、节省流量或 2G 网络时跳过背景。安装按钮和清单同步进入新地址，安装身份仍保留原 id。首页的原生作品集按钮使用完整页面导航，离开时停止首页音频；初始 HTML 也提供作品集入口。

同一 5 Mbps/80 ms、禁用缓存的手机模拟中，首屏可见作品链接从约 17.58 秒变为 0.21 秒；该读数表示作品入口可用，字体和后置纹理可以继续下载。桌面、390px、320px、背景阻塞、无 JavaScript、旧地址跳转和手机安装入口通过实际浏览器检查。

访问统计使用本机 Unix 数据报和独立 SQLite 后台进程，不添加浏览器追踪代码或公开接口。按北京时间统计成功的主站 HTML GET 请求（含 304），重开/刷新增加次数；同一网络地址估算为同一访客，机器人与验证 UA 不计入。数据库只保存 HMAC 标识、日期、页面和计数，不保存原始地址、查询参数或浏览器标识。合计访客跨页面去重，分页面访客不能直接相加。统计从本次发布开始，SPA 内没有 HTML 请求的切换不会额外计数。

资料位于服务器 `/var/lib/shouyulove-stats/`，目录 0700、数据库与密钥 0600；后台进程 `shouyulove-stats.service` 随开机启动。通过 SSH 执行 `sudo shouyulove-stats --days 30`，或添加 `--json` 查看每日及分页面资料。统计资料不在运行清单和 Git 中。普通 Nginx 请求日志继续保留，主站统计仅追加独立的私有日志通道。

## 2026-10-11 作品集三维特效恢复

用户明确要求完整保留特效、只调整加载顺序。作品集继续使用独立可点击 HTML；首次内容绘制至少两秒后后台加载原生 Nuxt/WebGL 场景，复用原三维模型、着色器、鼠标跟随与流体交互，完成后渐入。静态作品列表一直保留，加载过程不覆盖正文或重置滚动；音乐不初始化、不下载。`/portfolio/`、旧地址跳转、手机桌面入口和私有后台统计继续保留。新的模块与数据桥版本为 `syl-v1-1-portfolio-3d`。

目录优先展示核心创意、心创组内部使用；两类使用字号大于作品名、加深加重的分区标题。其他作品置于末尾，作品名为 16px、署名 12px，行间距更紧凑。展示顺序由内容源 MD 的「作品集页面 / 展示顺序」读取。

## 2026-10-11 作品集标题与次要作品收紧

顶部只显示「心创组作品集」并保留首页入口，删除原品牌文字与重复的作品集标题。其他作品移至末尾的紧凑单行列表：名称 14px、署名 12px、点击高度 44px，桌面宽度最多 480px。核心创意与心创组内部使用保持主要分区标题。完整三维背景仍后置加载，音乐不下载。展示文字及规则已同步正文 MD。

## 2026-10-11 次要作品隐藏署名

作品目录中其他作品的三个入口只显示作品名称，暂不显示设计者；核心创意、心创组内部使用的署名保留。显示规则读取内容源「作品集页面 / 其他作品设计者：不显示」，原项目资料及其他页面的署名保留。完整三维背景、目录标题、分类层级和手机入口沿用已发布版本。

## 2026-10-11 移除加载临时页面

首页、心创组及七个作品详情等原生页面统一使用原加载界面；资源准备进度由 0 显示到 100，完成后进入原三维页面。已删除共享构建中的临时文字页面、巨型标题样式与阅读位置接续逻辑。初始 HTML 和原生加载组件连续衔接，进度值同时提供给辅助技术。作品集的独立正式列表继续立即可用，完整三维特效随后在后台加载，音乐不下载。模块版本为 `syl-v1-1-native-loader`；字体、图片与数据桥沿用现有版本。
