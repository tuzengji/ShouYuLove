# 首页摄影素材记录

首页仅保留首屏的一张真实摄影素材：两名孩子牵手走过大树下的草地，人物占比较小，画面主要为树影与天空。这是陪伴与自然主题照片，不是手语示范。人物不表示北京大学真实成员，也不代表项目参与者。

封面来源：Anastasia Leyko 在 Pexels 发布的 [Children Walking on a Grass Field](https://www.pexels.com/photo/children-walking-on-a-grass-field-9173951/)，原图 3024×4032；[Pexels 许可](https://www.pexels.com/license/)允许免费用于网站并可修改，无需署名。未进行生成、扩图或人物合成。

首屏不再生成或合成多张封面图。Canvas 使用同一张真实照片，按滚动进度叠加轻微的暖光和蓝调色场，保留晨光—夕照—夜色的交互节奏。

## 文件

- 桌面封面：`home-assets/images/hero-tree-field-2048.webp`，2048×1444；从原图裁取 `(0,1900,3024,4032)` 后等比缩放。
- 手机封面：`home-assets/images/hero-tree-field-960.webp`，960×1711；从同一原图裁取 `(1400,2250,2400,4032)` 后等比缩放，页面横向裁切定位为 68%。
- 高清原图保留于本地 `output/photo-selection-20260928/9173951-original.jpg`。
- 上一版人物近景来自 Leah Newhouse 的 [Two Women Making Love Hand Signs](https://www.pexels.com/photo/two-women-making-love-hand-signs-1449671/)，派生图已移至本地 `主站版本归档/20260928-近景封面停用/`，不再用于页面或当前部署。
- 已停用的六张湖景 WebP 位于本地 `主站版本归档/20260928-湖景素材停用/`，不进入仓库或部署包。
- 湖景历史原始图片位于本地 `output/daylight-study/nature-lake/{morning,sunset,night}-original.png`，不进入仓库或部署包。
- 仅进行裁切、等比缩放与 WebP 编码。网页不依赖生成工具目录。
- 旧草地配图与素材记录封存在 `主站版本归档/20260927-184148-Daylight草地版/`，不再打包进部署文件。

## 历史生成提示词（已停用）

以下提示词属于此前湖光版本的研究记录；当前封面不再使用生成图，也不再依赖这些提示词。

### morning

```text
Use case: photorealistic-natural.
Asset type: full-bleed photographic hero for an elegant Chinese sign-language community website.
Create a beautiful natural lakeside scene, intimate and quiet, with still jade-green water, fine rippling reflections, and delicate willow branches descending from the upper right. Across the upper third, a softly wooded bank dissolves into a little pale morning mist. A few leaves catch the sun; most of the lower half is calm, uncluttered water. This is a small peaceful East Asian lake, not a grand mountain tourism vista.
Composition: landscape 1536x1024, natural 50mm editorial photography, restrained fine film texture, realistic vegetation and optics. The left 48 percent of the image is darker restful deep-green tree reflections and water, usable as negative space behind large white title text; the visual focus is a slender sunlit willow branch at the right and its reflection. Keep generous calm water in the middle. A subtle warm sun glow enters from high on the right.
Lighting: fresh early-morning natural light, luminous yet gentle. Muted jade, olive, silver-green leaves, pale warm highlights. Beautiful photographic tonal depth, no oversaturation, no dramatic HDR.
No people, figurines, hands, grass lawn, meadow, buildings, furniture, text, logos, heart shapes, graphics or watermarks. One coherent photograph only. This is the morning keyframe for a scrolling morning-to-sunset-to-evening transition; the exact composition will later remain fixed for lighting variants.
```

### sunset

```text
Use case: lighting-weather. Edit ONLY the lighting of this exact lake photograph for a website day-to-night scroll animation. Preserve the camera position, 1536x1024 crop, horizon, ALL tree silhouettes, ALL hanging willow branches and individual leaves, shoreline, every water ripple and reflection geometry in exactly the same pixel locations. Do not move or add any objects. One single edited photograph, no comparison panel, no text. Natural and photographic with muted, refined color. Change the scene to golden hour just before sunset. The sun is now low and just outside the frame on the right, illuminating the mist and hanging leaves in rich honey-gold light. The water reflects a beautiful subtle peach and amber sky on the right, with deeper olive-green shadow reflections on the left. Beautiful warm low light and elongated soft light over the water, a clear perceptible change from morning. Keep the left side darker for white web text. No oversaturated orange wash, no new visible sun disk, no changed scenery, no people, buildings, grass or artificial lights.
```

### night

```text
Use case: lighting-weather. Edit ONLY the lighting of this exact lake photograph for a website day-to-night scroll animation. Preserve the camera position, 1536x1024 crop, horizon, ALL tree silhouettes, ALL hanging willow branches and individual leaves, shoreline, every water ripple and reflection geometry in exactly the same pixel locations. Do not move or add any objects. One single edited photograph, no comparison panel, no text. Natural and photographic with muted, refined color. Change the scene to quiet blue hour just after sunset. All direct golden sunlight is gone. Cool muted deep teal and soft indigo ambient light, silvery-blue water reflections, blue dusk haze on the distant shoreline. The hanging willow leaves remain visible with a faint cool edge; forest reflected on the left is dark. Keep fine realistic texture and luminous water visible, not a black silhouette. The residual sky near upper right is pale steel-blue, not warm orange. No moon, stars, lights, people or new objects. Preserve every silhouette and ripple exactly.
```

## 字体与依赖

字体为自托管、按页面文字子集化的 Noto Serif SC Medium，许可见 `home-assets/licenses/OFL-NotoSerifSC.txt`。正文使用系统字体。图标为 Phosphor，许可随项目保留。品牌图标和 favicon 沿用现有版本。

GSAP 3.15.0、Lenis 1.3.26 与 esbuild 0.28.2 的版本固定在锁文件；依赖许可和打包版权声明保留。首屏 170 帧按滚动位置计算，没有后台视频循环。减少动态效果时显示清晨静态主图。
