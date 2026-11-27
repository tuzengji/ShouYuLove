# 奶家麻将：印着奶麻的麻将牌

2026-11-27 按用户要求，用用户提供的奶麻角色图（`naima-source.webp`，512px 透明底）印在一张麻将牌上作为奶家麻将的标志。

- `tile.svg`：麻将牌底座，象牙色牌面加绿色牌背，构建时与其他图标一样调亮并改为同色描边。
- `make_icon.py`：把角色贴着牌面内框底边放置、占满牌面宽度，截断处藏进圆角框，输出 `naimahjong.png`（1024px 透明底）。换角色图后运行 `python3 -B project-logos/20261127-naimahjong-tile/make_icon.py <图片>`。
- 主站通过 `scripts/build_home.py` 的 `ICON_SETS` 使用 `naimahjong.png`；它没有同名 SVG，构建时按图片处理，不再调色。
