# 项目标识

当前六个应用采用内置 `image_gen` 生成的轻盈版 Logo，保存在 [20261004-轻盈版](20261004-轻盈版/README.md)。每个应用分别生成 1:1 透明 PNG；拼好课与北大知道经过定向调整。原图、总览与提示词均在该文件夹。

构建器将新图片统一留白并导出 640×640 方形，用于首页与作品目录。生成记录保存在 `output/deployment/shouyulove-image-logos-20261004/generation.json`。

此前的六个 Claude SVG 作为历史源文件保留，不再进入本次运行清单；对应记录位于 `output/deployment/shouyulove-strokes-20261003/`。

年终总结使用原项目登录页的爱心标识，源文件 `2026-year-end-summary.svg` 与透明 PNG 位于本目录；构建为与其他作品一致的方形、羽化图标。
