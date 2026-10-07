# 以手予爱 ShouYuLove 主站

[以手予爱](https://shouyulove.cn/) 的心创组介绍与作品导航，采用现有 Astra/Nuxt、GSAP 和 WebGL 运行层。

本仓库保存当前已公开的精确静态版本：232 个运行文件、15 条页面路由、5 个相对资源链接，共 108,085,445 字节。包含已确认的中文字体、六个作品标识、背景音乐和光标提示清理。文件白名单、大小及 SHA-256 见 [runtime-manifest.json](runtime-manifest.json)。原始记录对应 `20261005T023111Z-astra-home`，2026-10-07 再次与线上文件逐项核对一致。

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

`content-source.md` 保存当前已公开文案；`styles/shouyulove-v1-1-cursor-clean.css` 保存当前样式。`scripts/build_content.py` 保留既有内容生成逻辑和每批次复用加载字标的优化，`tests/test_build_content.py` 覆盖两批构建间字体刷新及各页面共享字标的行为。

维护脚本保留实际原始素材的读取约定，完整内容重新生成还需要本机保存的素材：

- `output/deployment/shouyulove-content-v1/v0-backup.json` 中对应的项目内 V0 原始页面与共享素材。
- `主站版本归档/20261001-120733-Astra替换前/source/home-assets/images/` 中使用的两个站点图标。
- `output/deployment/shouyulove-hover-boundaries-20261004/font-source/` 中的当前字体源、子集与中文图集。
- 六个透明 Logo 原图、`music/` 中的既有音乐，以及字体候选清单指定的预览和许可文件。

这些历史原始素材和内部发布证据未作为公开运行版本重新发布。克隆可独立恢复现有站点；它不等同于包含全部设计原稿和原始 V0 的完整内容重建环境。保留原始资料的维护者应在独立副本中配置素材，再运行构建。构建脚本会重建固定的 `output/shouyulove-cursor-clean-site/`，因此不要把该目录作为唯一备份。

源码回归检查使用 Python 3.13 和以下依赖：

```sh
python3 -m pip install -r requirements-build.txt
python3 -B -m unittest discover -s tests -v
```

回归测试自行创建临时页面与输入，不要求 V0 或完整字体。需要新增字形或重新生成音乐时，另外使用对应的 `prepare_chinese_font.py` / `prepare_music.py`；这些生成步骤依赖 fontTools/Brotli、NumPy、SciPy、FFmpeg，以及固定版本 msdfgen v1.13，不能用它们替代运行快照恢复。

## 发布和许可

仅导出白名单供既有主站发布流程使用，见 [部署说明](deploy/README.md)。Git 同步与站点发布是独立动作；文件已经与线上一致时，无需再次上传或重启服务。

保留 [第三方许可与归属说明](THIRD_PARTY_NOTICES.md)。公开仓库不包含凭据、服务器状态快照、内部交接、研究材料或历史大目录。
