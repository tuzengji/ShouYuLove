# 以手予爱 ShouYuLove 主站

[以手予爱](https://shouyulove.cn/) 的心创组介绍与作品导航，采用现有 Astra/Nuxt、GSAP 和 WebGL 运行层。

本仓库保存当前已公开的精确静态版本：238 个运行文件、16 条页面路由、5 个相对资源链接，共 110,100,862 字节。公开文案已按指定原稿同步，第一届成员为 13 人（包含李昌昊）；七个作品图标的底色透明度为 28%，边缘保持宽幅不规则渐隐，图案完全不透明，融入浮雕背景；图片和标题居中，介绍与署名左对齐；接锅入口为 `/catchpot/`。文件白名单、大小及 SHA-256 见 [runtime-manifest.json](runtime-manifest.json)。2026-10-10 发布版本为 `20261010T101759Z-astra-home`。

首页只预载当前场景；心创组在悬停或进入时加载，页脚在接近可视区域时加载。正文和导航由初始 HTML 提供，原生视图完成后保留阅读位置；音乐稍后加载。手机两张法线纹理为 1024×1024，合计 1.75 MB，较原版减少约 61%。版本化公共资源缓存一年且 `immutable`，HTML 和页面 payload 使用 `no-cache`。

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

`content-source.md` 保存当前已公开文案；`styles/shouyulove-v1-1-jieguo.css` 保存当前样式，`styles/project-logo-mask.svg` 保存 HTML 与 WebGL 共用的不规则边缘遮罩。`scripts/build_content.py` 生成页面与运行资源，`scripts/optimize_runtime.py` 应用场景加载、手机纹理和图标边缘补丁，`scripts/fast_bootstrap.js` 衔接 HTML 与原生视图。中文子集与图集覆盖 324 字，字体缓存名由独立 `FONT_VERSION` 管理。三个回归检查覆盖批次间字标刷新、每页共享字标和实际 HTTP 缓存响应。

维护脚本保留实际原始素材的读取约定，完整内容重新生成还需要本机保存的素材：

- `output/deployment/shouyulove-content-v1/v0-backup.json` 中对应的项目内 V0 原始页面与共享素材。
- `主站版本归档/20261001-120733-Astra替换前/source/home-assets/images/` 中使用的两个站点图标。
- `output/deployment/shouyulove-content-sync-20261010/font-source/` 中的当前字体源、子集与中文图集。
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
