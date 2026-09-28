# 首页摄影素材记录

首页仅保留一张没有人物的真实照片：北京大学未名湖畔的灯笼、树影与黄昏天空。没有生成、扩图或人物合成。

摄影：星外之神，2024-03-11。[Wikimedia Commons 原始页面](https://commons.wikimedia.org/wiki/File:Weiming_Lake_Spring_Dusk.jpg)，[4080×3060 原图](https://upload.wikimedia.org/wikipedia/commons/7/7e/Weiming_Lake_Spring_Dusk.jpg)。适用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)，页面脚注保留署名、许可与修改说明，公开许可文件为 `home-assets/licenses/WEIMING-PHOTO.txt`。摄影派生资源沿用相同许可。

## 文件

- 桌面：`home-assets/images/hero-weiming-3840.webp`，3840×2880，完整原图等比缩小、WebP quality 90。
- 手机：`home-assets/images/hero-weiming-1280.webp`，1280×2277；原图裁切区域 `(1400,0,3120,3060)` 后等比缩小、WebP quality 90。
- 完整原图在本地 `output/weiming-photo/spring-dusk-original.jpg`，未上传至公开站点。
- Canvas 使用同一照片，按滚动进度叠加暖光与蓝调，保留既有晨光、夕照、夜色节奏；减少动态效果时显示原始静态照片。
- 上一版树下牵手照片资源保留在 `主站版本归档/20260928-人物封面停用/`，不进入当前部署包。
- 更早的人物近景、生成湖景与草地素材仍保留在原本的项目归档目录，不恢复到当前页面。

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

GSAP 3.15.0、Lenis 1.3.26 与 esbuild 0.28.2 的版本固定在锁文件；依赖许可和打包版权声明保留。首屏 170 帧按滚动位置计算，没有后台视频循环。减少动态效果时显示静态主图。
