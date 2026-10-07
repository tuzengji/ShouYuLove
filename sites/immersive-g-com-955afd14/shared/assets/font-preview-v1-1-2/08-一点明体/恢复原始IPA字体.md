# 恢复为 IPA 原始字库

本目录附有 IPA Font License 1.0 全文；完整原始 TTF 保持作者发布内容。字体对比页在此字体的 `@font-face` 中优先使用本机 `IPAmjMincho` / `IPAexMincho`，再使用 `I.Ming-8.10.ttf`；采用作者嵌入说明中的 `local()` 方案。

如希望将此字体恢复为 IPA 原始字库：

1. 从 [IPAmj 明朝官方页面](https://moji.or.jp/mojikiban/font/) 或 [IPA 官方下载页](https://moji.or.jp/ipafont/ipafontdownload) 获取原始字体。
2. 在 macOS 中双击原始 TTF，通过系统“字体册”安装。
3. 重新打开浏览器并刷新对比页。此选项将优先使用安装的原始 IPA 字库。

原始字体为日文字体，部分中文字形可能变化。作者说明保存在 `README_UPSTREAM.md`；Web Font 嵌入方案参考下方说明链接；上游说明来源：https://github.com/lxgw/lxgw/blob/main/documents/xizhi_embedding_instructions.md 。
