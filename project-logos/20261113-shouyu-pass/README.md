# 手语分社统一通行证图标

通行证卡片中央印有爱心签章，右下角斜置一把暖金色通行钥匙，表示统一身份与单点登录接入。沿用以手予爱系列的 256px 画布与 13px 圆润灰绿描边（`#4b5d54`），填色采用暖米（`#ece2cf`）、灰绿（`#aec2b1`）、豆沙红（`#c9a2a4`）与暖金（`#d4be88`）。

`shouyu-pass.svg` 为可编辑矢量源，`shouyu-pass.png` 为 1024×1024 透明 PNG，供主站首页、作品集与作品详情生成配图。

项目名：手语分社统一通行证。设计者：涂增基。正式入口：通行证主页 `https://shouyulove.cn/auth/`、接入与配置中心 `https://shouyulove.cn/auth/dev`。

## 入口小图标（2026-11-16）

主站首页与作品集卡片的两个入口按钮各用一枚小图标，由主图标拆解而来，描边与配色不变：

- `pass-home.svg`：通行证主页（`/auth/`）。保留印有爱心签章的通行证卡片。
- `pass-console.svg`：接入与配置中心（`/auth/dev`）。暖金色齿轮，中心是暖米色锁孔，表示接入凭证与配置。

两枚图标登记在 `scripts/build_content.py` 的 `ENTRY_ICONS` 中，直接内嵌进作品集页面与首页动态替换脚本 `scripts/project_entries.js`，不单独生成位图。
