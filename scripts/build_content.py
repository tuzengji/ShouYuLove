#!/usr/bin/env python3
"""Put the approved Markdown into Astra's existing pages and WebGL runtime."""

import copy
import hashlib
import html
import json
import re
import shutil
from pathlib import Path

from bs4 import BeautifulSoup
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from optimize_runtime import optimize_chunk, logo_svg_filter
from content_source import source_path, sync_snapshot


ROOT = Path(__file__).resolve().parents[1]
BASE_RECORDS = ROOT / "output/deployment/shouyulove-content-v1"
RECORDS = ROOT / "output/deployment/shouyulove-projects-blank-20261010"
MOBILE_TEXTURES = ROOT / "output/deployment/shouyulove-fast-20261009/mobile-textures"
# Keep historical manifests unchanged; locate their version inside this project.
V0_VERSION = Path(json.loads((BASE_RECORDS / "v0-backup.json").read_text())["local_backup"]).name
V0 = ROOT / "主站版本归档" / V0_VERSION / "site"
OUT = ROOT / "output/shouyulove-jieguo-site"
SHARED = Path("sites/immersive-g-com-955afd14/shared")
OLD_ASSETS = ROOT / "主站版本归档/20261001-120733-Astra替换前/source/home-assets"
FONT_SOURCE = ROOT / "output/deployment/shouyulove-md-binding-20261010/font-source"
RUNTIME_VERSION = "syl-v1-1-jieguo"
FONT_VERSION = "syl-v1-1-md-source"
MODULE_VERSION = "syl-v1-1-projects-ready"
BRIDGE_VERSION = "syl-v1-1-md-source"
SOURCE = source_path(ROOT)


def section(text, heading):
    match = re.search(rf"(?m)^### {re.escape(heading)}\s*$\n(.*?)(?=^### |^## |\Z)", text, re.S)
    assert match, heading
    return match.group(1).strip()


def parse_content(text=None):
    text = SOURCE.read_text(encoding='utf-8') if text is None else text
    projects = []
    identifiers = ["signtrace", "dictionary", "chuanqinghuiyi", "pinhaoke", "beida-zhidao", "qinghua-zhidao", "jieguo"]
    for identifier, match in zip(identifiers, re.finditer(r"(?m)^#### ([^\n]+)\n(.*?)(?=^#### |^### |\Z)", text, re.S)):
        title, body = match.groups()
        address = re.search(r"(?m)^地址：(.+)$", body).group(1).strip()
        link = re.search(r"https?://[^\s)]+", address)
        url = link.group() if link else "https://" + address
        assert re.fullmatch(r"https?://[^\s]+", url), "Invalid project address: " + address
        description = body.split("地址：", 1)[0].strip()
        designers = re.search(r"设计者：(.+)", body).group(1).strip()
        label = re.search(r"地址：\[([^]]+)\]", body)
        projects.append(dict(id=identifier, title=title, description=description, url=url, designers=designers,
                             label=label.group(1) if label else "打开" + title,
                             category=re.findall(r"(?m)^### ([^\n]+)$", text[:match.start()])[-1]))
    assert len(projects) == 7
    members = [line.strip() for line in section(text, "心创组第一届成员").splitlines() if line.strip()]
    assert members and len(members) == len(set(members)), "Empty or duplicate member names"
    introduction = re.search(r"(?m)^## 第二页\s*$\n(.*?)(?=^### )", text, re.S)
    assert introduction, "Second-screen introduction"
    identity, series = [line.strip() for line in introduction.group(1).splitlines() if line.strip()]
    vision = section(text, "愿景")
    # The source document includes an editing note outside the published blockquote.
    vision = "\n".join(line.removeprefix("> ").strip() for line in vision.splitlines() if line.startswith("> ")) or vision.split("\n\n", 1)[0]
    return dict(projects=projects, members=members, dream=section(text, "我们的梦想是").strip("* "),
                vision=vision,
                boundaries=[line[2:] for line in section(text, "边界").splitlines() if line.startswith("- ")],
                identity=identity, series=series,
                core=section(text, "核心创意").split("####", 1)[0].strip(),
                other=section(text, "其他作品").split("####", 1)[0].strip(),
                internal=section(text, "心创组内部使用").split("####", 1)[0].strip())


def text_block(title, body, size="medium"):
    return dict(type="text", id=title, align="center", text1=title, text2=body,
                text1Size="small", text1Layout="default", text2Size=size, text2Layout="default")


def raster_assets(content):
    destination = OUT / SHARED / "shouyulove"
    destination.mkdir(parents=True, exist_ok=True)
    palettes = [("#d4deda", "#879f92"), ("#e1e7e3", "#9aad9e"), ("#eddcd0", "#b39f8e"),
                ("#dde5d9", "#94a28d"), ("#dedde6", "#9b97ac"), ("#e3ded3", "#aca38b"), ("#dde8e1", "#63836f")]
    for project, palette in zip(content["projects"], palettes):
        icon = ROOT / "project-logos/20261004-轻盈版" / (project["id"] + ".png")
        if project["id"] == "jieguo":
            icon = ROOT / "project-logos/jieguo.png"
        mark = Image.open(icon).convert("RGBA")
        assert mark.width == mark.height and mark.getchannel("A").getextrema() == (0, 255), icon
        size = 640
        picture = Image.new("RGB", (size, size), palette[0])
        # Fit the visible artwork consistently; the untouched transparent masters stay local.
        bounds = mark.getchannel("A").point(lambda value: 255 if value >= 128 else 0).getbbox()
        assert bounds, icon
        mark = mark.crop(bounds)
        scale = size * .66 / max(mark.size)
        mark = mark.resize((round(mark.width * scale), round(mark.height * scale)), Image.Resampling.LANCZOS)
        picture.paste(mark, ((size-mark.width)//2, (size-mark.height)//2), mark)
        picture.save(destination / f"{project['id']}-square.{RUNTIME_VERSION}.png", optimize=True)
    shutil.copy2(FONT_SOURCE / "swei-spring-serif.woff2", destination / ("swei-spring-serif." + FONT_VERSION + ".woff2"))
    shutil.copy2(FONT_SOURCE / "OFL-SweiSpring.txt", destination / "OFL-SweiSpring.txt")
    for name in ["favicon.png", "apple-touch-icon.png"]:
        shutil.copy2(OLD_ASSETS / "images" / name, destination / name)


def chinese_atlases():
    chinese = json.loads((FONT_SOURCE / "chinese-font.json").read_text())
    texture = Image.open(FONT_SOURCE / "chinese-atlas-0.png").convert("RGB")
    for folder, name, font_name in [("PSTimesBody", "PSTimes-Regular", "PSTimes-Regular"),
                                     ("Helvetica-neue", "Helvetica-neue", "Helvetica-neue-msdf")]:
        source = V0 / SHARED / "webgl/msdf" / folder
        destination = OUT / SHARED / "webgl/msdf" / folder
        data = json.loads((source / (font_name + ".json")).read_text())
        # Preserve all original Latin glyph pixels, metrics and kerning; append the Chinese glyphs.
        atlas = Image.new("RGB", (2048, 2048))
        atlas.paste(Image.open(source / (name + ".png")).convert("RGB"), (0, 0))
        atlas.paste(texture, (256, 0))
        existing = {x["id"] for x in data["chars"]}
        for char in chinese["chars"]:
            if char["id"] in existing:
                continue
            item = dict(char)
            item["x"] += 256
            item["yoffset"] += data["common"]["base"] - chinese["common"]["base"]
            data["chars"].append(item)
        data["common"].update(scaleW=2048, scaleH=2048)
        data["info"]["charset"] = [x["char"] for x in data["chars"]]
        data["pages"] = [name + "." + FONT_VERSION + ".png"]
        atlas.save(destination / (name + "." + FONT_VERSION + ".png"), optimize=True)
        (destination / (font_name + "." + FONT_VERSION + ".json")).write_text(json.dumps(data, ensure_ascii=False))


def media(project, width, position, legend=None):
    w = h = 640
    return dict(type="ComponentCommonMedia", media=dict(type="image", mime="image/png", width=w, height=h,
                url="/" + str(SHARED / "shouyulove" / f"{project['id']}-square.{RUNTIME_VERSION}.png"), formats=None),
                videoPreview=None, legend=legend, width=width, position=position, margin="grid_1",
                offsetY=None, mediaWidth=w, mediaHeight=h)


def make_pages(content):
    pages = {}
    home = dict(id="1", type="home", title="首页", slug="home", uri="", url="/",
                loaded=True, loading=False, metas=None, blocks=[])
    # Keep all second-screen copy in the original MSDF title component and its reveal timeline.
    introduction = "\n".join([content["identity"], content["series"], "我们的梦想是\n" + content["dream"]])
    home["blocks"] = [dict(type="hero", id="home-intro", text1=html.escape(introduction), textAlign="left", cta=None, url=None),
                      text_block("愿景", content["vision"])]
    listing = []
    descriptions = {"核心创意": content["core"], "其他作品": content["other"], "心创组内部使用": content["internal"]}
    category = None
    for project in content["projects"]:
        if project["category"] != category:
            category = project["category"]
            home["blocks"].append(text_block(category, descriptions[category], "large"))
        description = html.escape(project["description"])
        legend = (project["description"] + "\n" if description else "") + "设计者：" + project["designers"]
        uri = "projects/" + project["id"]
        home["blocks"].append(dict(type="project", title=project["title"], slug=project["id"], uri=uri,
                                   projectType=project["category"], projectSpecs=project["designers"],
                                   projectUrl=project["url"], blocks=[],
                                   medias=[media(project, 12, "left", project["description"] or " ")]))
        listing.append(dict(type="projectItem", title=project["title"], media=media(project, 6, "left")["media"],
                            slug=project["id"], projectType=project["category"], projectSpecs=project["designers"],
                            projectUrl=project["url"], uri=uri, external=True, url=project["url"], blocks=[]))
        pages[uri] = dict(type="project", title=project["title"], slug=project["id"], uri=uri, url="/"+uri+"/",
                          loaded=True, loading=False, metas=None, projectUrl=project["url"], projectSpecs=project["designers"],
                          projectType=project["category"], blocks=[dict(type="hero", text1=project["title"],
                              textAlign="left", cta=project["label"], url=project["url"]),
                              text_block("", legend), dict(type="footer")])
    home["blocks"].extend([text_block("边界", "<br/><br/>".join(map(html.escape, content["boundaries"]))),
                           text_block("心创组第一届成员", '<div class="memberGrid">'+"".join('<span class="memberName">'+html.escape(name)+"</span>" for name in content["members"])+"</div>"),
                           dict(type="footer")])
    pages[""] = home
    pages["projects"] = dict(uri="projects", slug="projects", type="projects", title="作品集", url="/projects/",
                              loaded=True, loading=False, metas=None, blocks=[dict(type="hero", text1="作品集", textAlign="center"),
                               dict(type="listingProjects"), dict(type="footer")])
    sections = [("the-studio", "心创组", content["identity"], [text_block("", content["series"]), text_block("愿景",content["vision"])]),
                ("our-approach", "梦想", content["dream"], []),
                ("services", "核心创意", content["core"], [text_block(p["title"], html.escape(p["description"])+
                    '<br/><a href="'+html.escape(p["url"])+ '" target="_blank" rel="noopener noreferrer">'+p["label"]+'</a><br/>设计者：'+p["designers"]) for p in content["projects"] if p["category"] == "核心创意"]),
                ("awards", "其他作品", content["other"], [text_block(p["title"], html.escape(p["description"])+
                    '<br/><a href="'+html.escape(p["url"])+ '" target="_blank" rel="noopener noreferrer">'+p["label"]+'</a><br/>设计者：'+p["designers"]) for p in content["projects"] if p["category"] == "其他作品"]),
                ("clients", "边界", content["boundaries"][0], [text_block("",x) for x in content["boundaries"][1:]]),
                ("contact-us", "心创组第一届成员", "　".join(content["members"]), [])]
    about_sections = []
    for i, (slug, title, description, blocks) in enumerate(sections):
        uri = "the-studio/" + slug
        about_sections.append(dict(type="about-section", number=["I","II","III","IV","V","VI"][i], title=title,
                             desc=description, cta="了解", uri=uri, link=dict(type="about-detail",title=title,slug=slug,uri=uri)))
        detail_blocks = []
        for index, block in enumerate([text_block("",html.escape(description)), *blocks]):
            detail_blocks.append(dict(type="text",text1=(html.escape(block["text1"])+"<br/><br/>" if block["text1"] else "")+
                 block["text2"],text2=None,align="center-left" if index%2==0 else "center-right",
                 text1Size="medium",text1Layout="default",titleSection=None))
        pages[uri] = dict(type="about-detail", title=title, slug=slug, uri=uri, url="/"+uri+"/", loaded=True,
                         loading=False, metas=None, sceneIndex=i+1, blocks=detail_blocks)
    pages["the-studio"] = dict(type="about",title="心创组",slug="the-studio",uri="the-studio",url="/the-studio/",
                               loaded=True,loading=False,metas=None,sections=about_sections,blocks=[])
    return pages, listing


def revive(data, index=0, cache=None):
    cache = {} if cache is None else cache
    if index < 0:
        return None
    if index in cache:
        return cache[index]
    value = data[index]
    if isinstance(value, dict):
        result = {}; cache[index] = result
        result.update((key, revive(data, child, cache)) for key, child in value.items())
        return result
    if isinstance(value, list):
        if value and isinstance(value[0], str):
            if value[0] in ["Map", "Set"]:
                return Tagged(value[0], [revive(data, child, cache) for child in value[1:]])
            return revive(data, value[1], cache) if len(value) > 1 else []
        result = []; cache[index] = result
        result.extend(revive(data, child, cache) for child in value)
        return result
    return value


class Tagged:
    def __init__(self, tag, value=None):
        self.tag, self.value = tag, value


def flatten(value):
    result = []
    identities = {}
    def encode(item):
        if isinstance(item, (dict, list)) and id(item) in identities:
            return identities[id(item)]
        index = len(result); result.append(None)
        if isinstance(item, (dict, list)):
            identities[id(item)] = index
        if isinstance(item, Tagged):
            result[index] = [item.tag]+[encode(child) for child in (item.value or [])] if item.tag in ["Map","Set"] else [item.tag, encode(item.value)]
        elif isinstance(item, dict):
            result[index] = {key: encode(child) for key, child in item.items()}
        elif isinstance(item, list):
            result[index] = [encode(child) for child in item]
        else:
            result[index] = item
        return index
    encode(value)
    assert revive(result)["data"], "Nuxt payload round trip"
    return result


def loader_wordmark():
    with TTFont(FONT_SOURCE / "SweiSpringSugarCJKsc-Regular.ttf") as font:
        glyphs, cmap = font.getGlyphSet(), font.getBestCmap()
        outline = []
        for i, char in enumerate("心创组"):
            pen = SVGPathPen(glyphs)
            glyphs[cmap[ord(char)]].draw(pen)
            outline.append('<path d="' + pen.getCommands() + '" transform="translate(' + str(i * 20) + ' 20) scale(.02 -.02)" fill="#030303"/>')
    return "".join(outline)


def initial_loader(wordmark=None):
    wordmark = loader_wordmark() if wordmark is None else wordmark
    # Reuse the native loader's grid and wordmark until Vue has mounted that same screen.
    markup = '<div id="boot-loader" class="introLoader" role="status" aria-label="网站加载中">' + \
        '<div class="gridWrapper padding rowGap introLoader__wrapper" data-v-ad74c4db>' + \
        '<div class="introLoader__logo"><svg width="170" height="22" viewBox="0 0 170 22" aria-label="心创组">' + wordmark + '</svg></div>' + \
        '<div class="introLoader__progressWrapper"><div class="introLoader__progressBar"></div>' + \
        '<div class="introLoader__baseline"><div>以手予爱\u00a0 </div><div>ShouYuLove\u00a0 </div></div></div>' + \
        '<div class="introLoader__scrollDown"><div><div>0</div></div></div></div></div>'
    loader = BeautifulSoup(markup, "html.parser").div
    for node in [loader, *loader.find_all("div")]:
        node["data-v-0b3c665a"] = ""
    return loader


def runtime_chunks(wordmark=None):
    wordmark = loader_wordmark() if wordmark is None else wordmark
    assets = OUT / SHARED / "assets"
    modules = sorted(assets.glob("*.js"))
    renames = {p.name: p.stem + "." + MODULE_VERSION + ".js" for p in modules}
    for path in modules:
        text = path.read_text()
        if path.name == "entry.DyxL_KXi.js":
            # Native hover labels repeat the section heading beside the project name.
            # Keep category data for the works index; omit only its extra canvas mesh.
            start = 'if(this.isProject){const{title:a,projectType:l}=this._blockData'
            end = '}else if(this.isVideoLink){const{legend:a}=this._blockData'
            assert text.count(start) == 1 and text.count(end) == 1
            begin = text.index(start)
            finish = text.index(end, begin)
            text = text[:begin] + 'if(this.isProject){const{title:a}=this._blockData,c=new Hu({font:n,text:a,align:"left"});c.rotateX(Math.PI),c.scale(s,s,s),c.computeBoundingBox();const u=new Ot({vertexShader:M1,fragmentShader:D1,uniforms:{uColorAlpha:{value:1},uAtlas:{value:Qe.get("helvetica-neue/atlas")},uAlpha:{value:0},uColor:{value:o}},transparent:!0,depthTest:!1,depthWrite:!1}),p=new dt(c,u);r.add(p)' + text[finish:]
            logo = re.search(r"dwe=(\w+)\('(.*?)',16\),fwe=",text,re.S)
            assert logo, "Original animated wordmark"
            text = text[:logo.start()]+"dwe="+logo.group(1)+"('"+wordmark+"',3),fwe="+text[logo.end():]
            # The loading screen is already visible in HTML; continue it without replaying its entrance.
            for old, new in {
                'this.isDefaultMuted=!0,this.isMuted=!1,this.isUserMuted=!0':
                    'this.isDefaultMuted=!1,this.isMuted=!1,this.isUserMuted=!1',
                'audio:{isMuted:!0}': 'audio:{isMuted:!1}',
                '_l.addEventListener("change",this.onVisibilityChange),this.uiStore=as(),this.mute(this.uiStore.isMuted)':
                    '_l.addEventListener("change",this.onVisibilityChange),this.uiStore=as(),this.mute(this.uiStore.isMuted),this._resumeTheme=()=>{const n=this.currentThemeHTML5;!this.isUserMuted&&n&&n.state()==="loaded"&&!n.playing()&&n.play()},["click","touchend","keydown"].forEach(n=>document.addEventListener(n,e=>{e.isTrusted&&this._resumeTheme()},!0)),this.playTheme("ShouYuLove_Warm_Airy_v1_1")',
                'n.play(),n.volume(0),n.fade(0,t,P3),this.currentThemeHTML5=n':
                    'n.once("load",()=>ac.Howler._audioUnlocked&&this._resumeTheme()),n.once("playerror",()=>{ac.Howler._audioUnlocked?this._resumeTheme():n.once("unlock",this._resumeTheme)}),n.play(),n.volume(0),n.fade(0,t,P3),this.currentThemeHTML5=n',
                'this.isUserMuted=e,(t=this.uiStore)':
                    'this.isUserMuted=e,!e&&this._resumeTheme(),(t=this.uiStore)',
                'p=tn(null),m=tn(!0),_=tn(!1)': 'p=tn(null),m=tn(!e.main),_=tn(!1)',
                'x.value=!0,Ee(1,!0),js.addEventListener':
                    'x.value=!0,Ee(0,!1),Ie.set([...u.value,d.value],{opacity:1}),document.getElementById("boot-loader")?.remove(),js.addEventListener',
            }.items():
                assert text.count(old) == 1, old
                text = text.replace(old, new, 1)
            # Distance-field glyphs must retain their channels when scaled down; mipmaps erase hairlines.
            old = '_createMesh(){const t=this._getCSSInformations(),n=new Hu({font:Qe.get("PSTimes-body/font")})'
            assert text.count(old) == 2, old
            text = text.replace(old, '_createMesh(){const a=Qe.get("PSTimes-body/atlas");a.generateMipmaps=!1,a.minFilter=1006,a.needsUpdate=!0;const t=this._getCSSInformations(),n=new Hu({font:Qe.get("PSTimes-body/font")})', 1)
            old = 'float edge=clamp(sigDist/fwidth(sigDist)+0.5,0.0,1.0);edge*=fadeProgress*maskProgress*uOpacity;'
            assert text.count(old) == 1, old
            text = text.replace(old, 'vec2 screenTexSize=1./fwidth(vUv);float screenPxRange=max(.5*dot(vec2(4./2048.),screenTexSize),1.);float edge=clamp(sigDist*screenPxRange+0.5,0.0,1.0);edge*=fadeProgress*maskProgress*uOpacity;', 1)
            # UI targets contain premultiplied colors. A white transparent clear faded hairlines twice.
            for old, new in {
                'this.$renderer.instance.setClearColor(16777215,0),this.$renderer.instance.setRenderTarget(t)':
                    'this.$renderer.instance.setClearColor(t===this._renderTargetUi?0:16777215,0),this.$renderer.instance.setRenderTarget(t)',
                'nextColor=texture2D(tPrevViewUi,uvUI);color.rgb=mix(color.rgb,nextColor.rgb,nextColor.a*opacity);':
                    'nextColor=texture2D(tPrevViewUi,uvUI);color.rgb=color.rgb*(1.-nextColor.a*opacity)+nextColor.rgb*opacity;',
                'opacity=uView1Alpha;color.rgb=mix(color.rgb,nextColor.rgb,nextColor.a*opacity);':
                    'opacity=uView1Alpha;color.rgb=color.rgb*(1.-nextColor.a*opacity)+nextColor.rgb*opacity;',
                'nextColor=texture2D(tView2Ui,uvUI);color.rgb=mix(color.rgb,nextColor.rgb,nextColor.a*opacity);':
                    'nextColor=texture2D(tView2Ui,uvUI);color.rgb=color.rgb*(1.-nextColor.a*opacity)+nextColor.rgb*opacity;',
                'this._minDprUi=t.minDprUi||Uo.device.views.minDprUi':
                    'this._minDprUi=Math.min(2,window.devicePixelRatio||1)',
                'this._maxDprUi=t.maxDprUi||Uo.device.views.maxDprUi':
                    'this._maxDprUi=Math.min(2,window.devicePixelRatio||1)',
            }.items():
                assert text.count(old) == 1, old
                text = text.replace(old, new, 1)
            # Compact project images and captions share their DOM rows; independent vertical drift overlaps them.
            old = 'this._parallaxPositionOffset=-h*this._parallaxPositionFactor.value*this._parallaxScrollFactor.value'
            assert text.count(old) == 1, old
            text = text.replace(old, 'this._parallaxPositionOffset=this.isProject?0:-h*this._parallaxPositionFactor.value*this._parallaxScrollFactor.value', 1)
            # Finish the existing noisy reveal with complete strokes, including thin serif details.
            for old, new in {
                'float sdf=msdf(uAtlas,vUv);float sigDist=sdf+MIN_THICKNESS':
                    'thicknessProgress=mix(thicknessProgress,1.,smoothstep(.85,1.,uThicknessProgress));fadeProgress=mix(fadeProgress,1.,smoothstep(.85,1.,uFadeProgress));maskProgress=mix(maskProgress,1.,smoothstep(.85,1.,uMaskProgress));float sdf=msdf(uAtlas,vUv);float sigDist=sdf+MIN_THICKNESS',
                'IG_HomePage_v5_v4:1,IG_FocusPage_v5_v8:1,IG_AboutPage_v5_v5:1': 'ShouYuLove_Warm_Airy_v1_1:.72',
                '{src:["/sounds/general/IG_HomePage_v5_v4.mp3"],loop:!0,preload:!1},{src:["/sounds/general/IG_FocusPage_v5_v8.mp3"],loop:!0,preload:!1},{src:["/sounds/general/IG_AboutPage_v5_v5.mp3"],loop:!0,preload:!1}':
                    '{src:["/sounds/general/ShouYuLove_Warm_Airy_v1_1.mp3"],loop:!0,preload:!1}',
            }.items():
                assert text.count(old) == 1, old
                text = text.replace(old, new, 1)
            for old in ['vo.playTheme("IG_HomePage_v5_v4")', 'vo.playTheme("IG_FocusPage_v5_v8")', 'vo.playTheme("IG_AboutPage_v5_v5")']:
                assert old in text, old
                text = text.replace(old, 'vo.playTheme("ShouYuLove_Warm_Airy_v1_1")')
            for old, new in {"Innovative digital experiences studio":"以手予爱 ShouYuLove", "Scroll down":"向下探索",
                             'title:"Close"':'title:"首页"', 'title:"Menu"':'title:"心创组"',
                             'title:"Immersive Garden"':'title:"以手予爱 ShouYuLove"',
                             "Since 2013 we have produced more than 67 projects.":"作品集",
                             "/webgl/msdf/PSTimesBody/PSTimes-Regular.png":"/webgl/msdf/PSTimesBody/PSTimes-Regular."+FONT_VERSION+".png",
                             "/webgl/msdf/PSTimesBody/PSTimes-Regular.json":"/webgl/msdf/PSTimesBody/PSTimes-Regular."+FONT_VERSION+".json",
                             "/webgl/msdf/Helvetica-neue/Helvetica-neue.png":"/webgl/msdf/Helvetica-neue/Helvetica-neue."+FONT_VERSION+".png",
                             "/webgl/msdf/Helvetica-neue/Helvetica-neue-msdf.json":"/webgl/msdf/Helvetica-neue/Helvetica-neue-msdf."+FONT_VERSION+".json"}.items():
                assert old in text, old
                text = text.replace(old, new)
        if path.name == "HomePage.ClaPmn7U.js":
            old = 'projectType:{type:String,default:null},uri:'
            assert old in text
            text = text.replace(old, 'projectType:{type:String,default:null},projectSpecs:{type:String,default:null},projectUrl:{type:String,default:null},uri:', 1)
            old = ']))),128))],10,Pe)'
            assert old in text
            text = text.replace(old, ']))),128)),n.projectSpecs?A("p",{class:"projectCard__designers"},"设计者："+n.projectSpecs,1):w("",!0),n.projectUrl?A("a",{class:"projectEntry",href:n.projectUrl,target:"_blank",rel:"noopener noreferrer","aria-label":"打开"+n.title,onClick:e=>e.stopPropagation()},[A("span",{class:"sr-only"},n.title)]):w("",!0)],10,Pe)', 1)
            old = '"data-uri":n.uri},[(s(!0),y(D,null,H(p(r)'
            assert text.count(old) == 1, old
            text = text.replace(old, '"data-uri":n.uri},[A("h2",{class:"projectCard__title"},n.title,1),(s(!0),y(D,null,H(p(r)', 1)
        if path.name == "HeroBlock.DoznkBHg.js":
            # Animate member grid cells directly instead of splitting the grid into text lines.
            old = 'l=new J(n.value,{type:"lines"}),P()'
            assert text.count(old) == 1, old
            text = text.replace(old, 'l=n.value.querySelector(".memberGrid")?{lines:Array.from(n.value.querySelectorAll(".memberName")),split:()=>{}}:new J(n.value,{type:"lines"}),P()', 1)
        if path.name == "index.CeH_ahVV.js":
            old = 'projectType:{type:String,default:""},url:'
            assert text.count(old) == 1, old
            text = text.replace(old, 'projectType:{type:String,default:""},projectSpecs:{type:String,default:""},url:', 1)
            old = 'null,10,Te),D(he,{class:"name"'
            assert text.count(old) == 1, old
            text = text.replace(old, 'null,10,Te),C("p",{class:"projectListItem__designers"},"设计者："+a.projectSpecs,1),D(he,{class:"name"', 1)
        if path.name == "AllProjectsButton.BJXpRcDM.js":
            text = text.replace("See all projects", "作品集")
            for old, new in {"https://x.com/Immersive_g":"/projects/", "https://www.instagram.com/immersive_g/":"/the-studio/",
                             "https://fr.linkedin.com/company/immersive-garden":"/", 'te(" X ")':'te(" 作品集 ")',
                             'te(" Instagram ")':'te(" 心创组 ")', 'te(" Linkedin ")':'te(" 首页 ")'}.items():
                text = text.replace(old, new)
        if path.name == "AboutPage.DgUWXiAT.js":
            text = text.replace(" Click to explore ", " 点击了解 ")
            # Native mobile uses DOM text; desktop uses the original WebGL title meshes.
            assert "aboutPage:!0" in text
            text = text.replace("aboutPage:!0", "aboutPage:!0,\"aboutPage--domText\":J.device.mobile", 1)
        if path.name == "default.CxpTjDRZ.js":
            old = 'Fe.isDevelopment&&new Ct,f.setCursor("Click to enable sound",f.darkBg,!0),window.addEventListener("click",n)'
            assert text.count(old) == 1, old
            text = text.replace(old, 'Fe.isDevelopment&&new Ct', 1)
            old = 'function n(){window.removeEventListener("click",n),f.setCursor(null),W.muteByUser(!1)}'
            assert text.count(old) == 1, old
            text = text.replace(old, '', 1)
        for old, new in renames.items():
            text = text.replace(old, new)
        (assets / renames[path.name]).write_text(optimize_chunk(path.name, text, MODULE_VERSION))
        path.unlink()
    return renames


def early_page(content, page):
    """Accessible approved content, replaced once the native view is ready."""
    pieces = ['<main id="syl-early" class="homePage"><nav class="syl-early-nav"><a href="/">首页</a><a href="/the-studio/">心创组</a></nav><div class="page__wrapper">']
    title = '以手予爱<br/>ShouYuLove' if page['type'] == 'home' else html.escape(page['title'])
    pieces.append('<section class="syl-early-brand" data-syl-key="brand"><h1>' + title + '</h1></section>')
    for block in page.get('blocks', []):
        kind = block['type']
        key = html.escape(block.get('id', ''), quote=True)
        if kind == 'hero':
            pieces.append('<section class="syl-early-section" data-syl-key="' + key + '"><p class="syl-early-intro">' + block.get('text1', '') + '</p></section>')
            if block.get('url'):
                pieces.append('<p class="syl-early-section"><a href="' + html.escape(block['url'], quote=True) + '" target="_blank" rel="noopener noreferrer">' + html.escape(block.get('cta') or page['title']) + '</a></p>')
        elif kind == 'text':
            pieces.append('<section class="syl-early-section textBlock" data-syl-key="' + key + '"><h2>' + block.get('text1', '') + '</h2><div class="syl-early-copy">' + (block.get('text2') or '') + '</div></section>')
        elif kind == 'project':
            media = block['medias'][0]; uri = html.escape(block['uri'], quote=True)
            pieces.append('<section class="projectBlock" data-uri="' + uri + '" data-syl-key="' + uri + '"><h2 class="projectCard__title">' + html.escape(block['title']) + '</h2><div class="mediaBlock__grid"><img class="mediaBlock__image image" width="180" height="180" loading="lazy" alt="" src="' + html.escape(media['media']['url'], quote=True) + '"/><div class="mediaBlock__image text"><p>' + html.escape(media.get('legend', '')) + '</p></div></div><p class="projectCard__designers">设计者：' + html.escape(block['projectSpecs']) + '</p><a class="projectEntry" href="' + html.escape(block['projectUrl'], quote=True) + '" target="_blank" rel="noopener noreferrer" aria-label="打开' + html.escape(block['title'], quote=True) + '"></a></section>')
        elif kind == 'footer':
            pieces.append('<section class="syl-early-brand"><p>以手予爱<br/>ShouYuLove</p></section>')
        elif kind == 'listingProjects':
            pieces.append('<section class="syl-early-section">' + ''.join('<p><a href="' + html.escape(project['url'], quote=True) + '" target="_blank" rel="noopener noreferrer">' + html.escape(project['title']) + '</a></p>' for project in content['projects']) + '</section>')
    if page['type'] == 'about':
        for section in page.get('sections', []):
            pieces.append('<section class="syl-early-section"><h2><a href="/' + html.escape(section['uri'], quote=True) + '/">' + html.escape(section['title']) + '</a></h2><p>' + html.escape(section['desc']) + '</p></section>')
    pieces.append('</div></main>')
    return BeautifulSoup(''.join(pieces), 'html.parser').main


def html_pages(content, pages, listing, renames, wordmark=None):
    # A full CJK font is expensive to decode; build the identical loader once per batch.
    # Clone its DOM per page because BeautifulSoup moves inserted nodes between parents.
    loader = initial_loader(wordmark)
    nav = [dict(id="", label="首页", url="/", urlPrefix="/", uri="", type="home"),
           dict(id="the-studio", label="心创组", url="/the-studio/", urlPrefix="/", uri="the-studio/", type="about")]
    general = dict(metas=dict(baseUrl="https://shouyulove.cn",seo=dict(title="以手予爱 ShouYuLove",description=content["identity"])),
                   nav=[dict(uri=x["id"],slug=x["id"],title=x["label"],type=x["type"]) for x in nav])
    footer = dict(contactTitle="以手予爱<br/>ShouYuLove", contactEmail="", contactAddress="以手予爱<br/>ShouYuLove")
    for route, page in pages.items():
        template_route = route if (V0 / route / "index.html").exists() else "projects/louis-vuitton-1"
        soup = BeautifulSoup((V0 / template_route / "index.html").read_text(), "html.parser")
        data = revive(json.loads(soup.select_one("#__NUXT_DATA__").string))
        data["pinia"]["ui"]["audio"]["isMuted"] = False
        ds = data["pinia"]["datas"]
        ds.update(general=general, footer=footer, nav=nav, pages=list(pages.values()), projectsList=listing,
                  base={"en":dict(loaded=True,loading=False,data=dict(general=general,
                     global_=None, pages=list(pages.values())))})
        ds["base"]["en"]["data"]["global"] = dict(type="GlobalEntity",footer=footer,projectsPopinTitle="作品集",projectsList=listing)
        ds["base"]["en"]["data"].pop("global_")
        key = "en_home" if not route else ("en_about" if route == "the-studio" else "en_projects" if route == "projects" else "en_page_"+route.replace("/","_"))
        data.update(state=Tagged("Reactive",{}), once=Tagged("Set"), _errors=Tagged("Reactive",{key:None}),
                    serverRendered=False, path=page["url"], data=Tagged("ShallowReactive",{key:page}))
        soup.select_one("#__NUXT_DATA__").string = json.dumps(flatten(data),ensure_ascii=False,separators=(",",":")).replace("<","\\u003c")
        soup.html["lang"] = "zh-CN"
        soup.html['class'] = ['syl-fast-early']
        soup.title.string = "以手予爱 ShouYuLove" if not route else page["title"]+" · 以手予爱 ShouYuLove"
        for meta in soup.find_all("meta"):
            if meta.get("name") == "description" or meta.get("property") in ["og:description","twitter:description"]:
                meta["content"] = content["identity"]
            if meta.get("property") in ["og:title","twitter:title"]:
                meta["content"] = soup.title.string
            if meta.get("property") in ["og:url","twitter:url"]:
                meta["content"] = "https://shouyulove.cn"+page["url"]
            if meta.get("property") in ["og:image","twitter:image"]:
                meta["content"] = "/"+str(SHARED/("shouyulove/signtrace-square." + RUNTIME_VERSION + ".png"))
        for node in soup.find_all("link"):
            if "modulepreload" in node.get("rel",[]):
                node.decompose(); continue
            href = node.get("href", "")
            if "canonical" in node.get("rel",[]):
                node["href"] = "https://shouyulove.cn"+page["url"]
            if "icon" in node.get("rel",[]):
                node["href"] = "/"+str(SHARED/"shouyulove/favicon.png")
            if "apple-touch-icon" in node.get("rel",[]):
                node["href"] = "/"+str(SHARED/"shouyulove/apple-touch-icon.png")
        stylesheet = soup.new_tag("link",rel="stylesheet",href="/assets/shouyulove." + MODULE_VERSION + ".css")
        soup.head.append(stylesheet)
        boot_style = soup.new_tag("style", id="boot-loader-style")
        boot_style.string = '#boot-loader{position:fixed;inset:0;height:100vh;width:100%;background:#e8e8e8;z-index:1010}#boot-loader .introLoader__logo svg,#boot-loader .introLoader__baseline>div,#boot-loader .introLoader__scrollDown{opacity:1}'
        soup.head.append(boot_style)
        for font in ["assets/PSTimes-Regular.hY69LrJ0.woff2", "shouyulove/swei-spring-serif." + FONT_VERSION + ".woff2"]:
            soup.head.append(soup.new_tag("link", rel="preload", href="/" + str(SHARED / font), **{"as": "font", "type": "font/woff2", "crossorigin": "anonymous"}))
        # Keep the first paint outside Vue's root so asynchronous route setup cannot clear it early.
        preview = soup.select_one("#__nuxt");preview.clear()
        preview['aria-hidden'] = 'true'
        preview.insert_before(early_page(content, page))
        preview.insert_before(copy.deepcopy(loader))
        soup.body.append(BeautifulSoup(logo_svg_filter(), 'html.parser').svg)
        soup.body.append(soup.new_tag('script', src='/assets/fast-bootstrap.' + MODULE_VERSION + '.js'))
        fallback = BeautifulSoup('<noscript><style>#boot-loader{display:none}</style><main class="static-preview"><h1>以手予爱<br/>ShouYuLove</h1><p>'+html.escape(content["identity"])+
            '</p><p>'+html.escape(content["series"])+ '</p><h2>梦想</h2><p>'+html.escape(content["dream"])+
            '</p><h2>愿景</h2><p>'+html.escape(content["vision"])+ '</p>'+''.join('<h2>'+html.escape(p["title"])+
            '</h2><p>'+html.escape(p["description"])+ '</p><a target="_blank" rel="noopener noreferrer" href="'+html.escape(p["url"])+
            '">'+html.escape(p["label"])+ '</a><p>设计者：'+html.escape(p["designers"])+ '</p>' for p in content["projects"])+
            '<h2>边界</h2>'+''.join('<p>'+html.escape(b)+ '</p>' for b in content["boundaries"])+
            '<h2>心创组第一届成员</h2><p>'+ '　'.join(content["members"])+ '</p></main></noscript>','html.parser')
        preview.append(fallback.noscript)
        text = str(soup)
        text = text.replace("/shared/local-bridge.js", "/shared/local-bridge." + BRIDGE_VERSION + ".js")
        for old,new in renames.items():
            text = text.replace(old,new)
        destination = OUT / route / "index.html";destination.parent.mkdir(parents=True,exist_ok=True);destination.write_text(text)
        (destination.parent/"_payload.json").write_text(json.dumps(flatten(dict(data=Tagged("ShallowReactive",{key:page}))),
            ensure_ascii=False,separators=(",",":")).replace("<","\\u003c"))
    (OUT / SHARED / ("local-bridge." + BRIDGE_VERSION + ".js")).write_text("window.__IG_LOCAL_PAGES__="+json.dumps(pages,ensure_ascii=False,separators=(",",":"))+";\n")


def font_preview():
    source = ROOT / "字体候选"
    target = OUT / SHARED / "assets/font-preview-v1-1-2"
    manifest = json.loads((source / "manifest.json").read_text())
    files = {"index.html", "favicon.png", "README.md", "manifest.json", manifest["english"]["file"]}
    for item in manifest["fonts"]:
        files.update([item["preview_file"], item["folder"] + "/" + item["license_name"]])
        if item['license_type'].startswith('IPA'):
            files.add(item['folder'] + '/恢复原始IPA字体.md')
    for relative in sorted(files):
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, destination)


def main():
    source_text = SOURCE.read_text(encoding='utf-8')
    content = parse_content(source_text)
    cmap = TTFont(FONT_SOURCE / 'swei-spring-serif.woff2').getBestCmap()
    missing = sorted({c for c in json.dumps(content, ensure_ascii=False) if ord(c) > 127 and ord(c) not in cmap})
    assert not missing, 'Regenerate and version the Chinese font for: ' + ''.join(missing)
    assert OUT.parent == ROOT / "output" and OUT.name == "shouyulove-jieguo-site"
    RECORDS.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True,exist_ok=True)
    for name in ["assets","webgl","sounds","images","lotties"]:
        target = OUT / SHARED / name
        shutil.copytree(V0 / SHARED / name,target,dirs_exist_ok=True)
        link = OUT / name
        if not link.is_symlink():
            link.symlink_to(SHARED/name,target_is_directory=True)
    shutil.copytree(V0/SHARED/"benchmarks",OUT/SHARED/"benchmarks",dirs_exist_ok=True)
    raster_assets(content)
    chinese_atlases()
    pages,listing = make_pages(content)
    wordmark = loader_wordmark()
    renames = runtime_chunks(wordmark)
    html_pages(content,pages,listing,renames,wordmark)
    shutil.copy2(ROOT/"styles/shouyulove-v1-1-jieguo.css", OUT/SHARED/("assets/shouyulove." + MODULE_VERSION + ".css"))
    shutil.copy2(ROOT/'scripts/fast_bootstrap.js', OUT/SHARED/('assets/fast-bootstrap.' + MODULE_VERSION + '.js'))
    shutil.copytree(MOBILE_TEXTURES, OUT/SHARED/'webgl/about/model/textures/ktx2/mobile')
    sounds = OUT / SHARED / "sounds/general"
    for name in ["IG_HomePage_v5_v4.mp3", "IG_FocusPage_v5_v8.mp3", "IG_AboutPage_v5_v5.mp3"]:
        (sounds / name).unlink()
    for name in ["ShouYuLove_Warm_Airy_v1_1.mp3", "ShouYuLove_Warm_Airy_v1_1.txt"]:
        shutil.copy2(ROOT / "music" / name, sounds / name)
    font_preview()
    assert SOURCE.read_text(encoding='utf-8') == source_text, 'Content source changed during build; run again.'
    sync_snapshot(ROOT, source_text)
    (RECORDS/"content.json").write_text(json.dumps(content,ensure_ascii=False,indent=2)+"\n")
    manifest = dict(routes={page["url"]: (route+"/" if route else "")+"index.html" for route,page in pages.items()},files={},symlinks={},bytes=0)
    for path in sorted(OUT.rglob("*")):
        name = str(path.relative_to(OUT))
        if path.is_symlink():
            manifest["symlinks"][name] = str(path.readlink())
        elif path.is_file():
            contents = path.read_bytes();manifest["files"][name] = dict(bytes=len(contents),sha256=hashlib.sha256(contents).hexdigest());manifest["bytes"] += len(contents)
    assert len(manifest["routes"]) == 16 and len(manifest["symlinks"]) == 5
    (RECORDS/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(dict(pages=len(pages),files=len(manifest["files"]),bytes=manifest["bytes"]),indent=2))


if __name__ == "__main__":
    main()
