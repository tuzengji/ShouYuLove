"""Adapt the exported runtime without changing its artwork or scene animations."""

def optimize_chunk(name, text, version):
    if name != "entry.DyxL_KXi.js":
        return text
    def replace(old, new):
        nonlocal text
        assert text.count(old) == 1, old
        text = text.replace(old, new, 1)

    # Audio objects are retained; their downloads start after the critical scene.
    replace('e.push(...D3(t))', 'e.push(...D3({...t,preload:!1}))')
    replace('function d(){s.setAsLoaded(),p()}',
            'function d(){s.setAsLoaded(),p(),__sylAfterReady(h)}')

    # Feather the logo tile itself, leaving the central artwork fully opaque.
    # DOM previews use the same 14% falloff in the stylesheet.
    replace('uPreviewTextureAlpha:{value:0}}',
            'uPreviewTextureAlpha:{value:0},uSoftProjectEdges:{value:!!(this.isImage&&this.assetUrl?.includes("/shouyulove/")&&this.assetUrl.includes("-square."))}}')
    replace('uniform float uZoomProgress;float cremap',
            'uniform float uZoomProgress;uniform bool uSoftProjectEdges;float cremap')
    replace('gl_FragColor.rgb=color;gl_FragColor.a=alpha*uAlpha;if(uvImage.y>1.0||uvImage.y<0.0)',
            'if(uSoftProjectEdges){vec2 edgeAlpha=smoothstep(vec2(0.),vec2(.14),min(vUv,1.-vUv));alpha*=edgeAlpha.x*edgeAlpha.y;}gl_FragColor.rgb=color;gl_FragColor.a=alpha*uAlpha;if(uvImage.y>1.0||uvImage.y<0.0)')

    # Texture bytes are unchanged when a new module version is released.
    texture_version = 'syl-v1-1-fast'
    for number in ['05', '06']:
        resource_name = 'about/normalMap' + str(int(number))
        old = ('fallback:{mobile_or_lowTier:{type:kr==="ktx2"?"ktx2":"texture",path:`/webgl/about/model/textures/${kr}/ultralow/normal_' + number + '.${kr}`,name:"' + resource_name + '"}}')
        new = ('fallback:{mobile:{type:"ktx2",path:"/webgl/about/model/textures/ktx2/mobile/normal_' + number + '.' + texture_version + '.ktx2",name:"' + resource_name + '"},' + old.removeprefix('fallback:{'))
        replace(old, new)

    # These hooks run before the asynchronous Nuxt mount. Existing animation
    # methods remain responsible for drawing, hovering and changing scenes.
    text += r'''
const __sylAddViews=Wme.prototype._addViewsAssets;
Wme.prototype._addViewsAssets=function(views=[],loader=this._resourceLoader){
  const key=location.pathname.replace(/^\/+|\/+$/g,""),page=window.__IG_LOCAL_PAGES__?.[key];
  if(page){
    this._firstView=page.type==="about-detail"?"aboutDetail"+page.sceneIndex:page.type;
    for(const view of views){const needed=view.name===this._firstView||(page.type==="about-detail"&&view.name==="about");view.resources.preload={production:needed,development:needed};}
    views=[...views].sort((a,b)=>Number(b.resources.preload.production)-Number(a.resources.preload.production));
  }
  return __sylAddViews.call(this,views,loader);
};
const __sylLoadAssets=Oc.prototype._loadAssets;
Oc.prototype._loadAssets=function(){
  if(this._areResourcesLoaded())return Promise.resolve();
  return this.__sylAssetsPromise||(this.__sylAssetsPromise=__sylLoadAssets.call(this).finally(()=>{this.__sylAssetsPromise=null;}));
};
function __sylLoadScene(view){
  js.addViewAssets(view._viewConfig);view.resourceManager._setupResources();
  return view._loadAssets().then(()=>{view.prepare();view.$root._resize();return view;});
}
const __sylAboutHover=_ve.prototype.animOverOut;
_ve.prototype.animOverOut=function(over=true){
  this.__sylHoverWanted=over;
  if(!this._areResourcesLoaded()){
    if(over&&!this.__sylHoverPromise)this.__sylHoverPromise=__sylLoadScene(this).then(()=>{this.__sylHoverPromise=null;if(this.__sylHoverWanted)__sylAboutHover.call(this,true);}).catch(e=>{this.__sylHoverPromise=null;console.error(e);});
    return Ie.timeline();
  }
  return __sylAboutHover.call(this,over);
};
const __sylFooterShow=$ye.prototype.show,__sylFooterHide=$ye.prototype.hide;
$ye.prototype.show=function(){
  this.__sylFooterWanted=true;
  if(!this.sceneComponent){__sylLoadScene(this).then(()=>{if(this.__sylFooterWanted)__sylFooterShow.call(this);}).catch(console.error);return Ie.timeline();}
  return __sylFooterShow.call(this);
};
$ye.prototype.hide=function(){this.__sylFooterWanted=false;return this.sceneComponent?__sylFooterHide.call(this):Ie.timeline();};
const __sylPlayTheme=Fde.prototype.playTheme;
Fde.prototype.playTheme=function(theme){
  if(js._initialLoading!==false){this.__sylPendingTheme=theme;return;}
  return __sylPlayTheme.call(this,theme);
};
function __sylAfterReady(app){
  setTimeout(()=>{
    const footer=app.viewManager.get("footer")?.instance;
    const observer=footer&&new IntersectionObserver(entries=>{if(entries.some(e=>e.isIntersecting)){observer.disconnect();__sylLoadScene(footer).catch(console.error);}},{rootMargin:"200% 0px"});
    document.querySelectorAll("#__nuxt .footer").forEach(e=>observer?.observe(e));
    window.__sylFast?.ready(Dt,()=>dh().ready&&as().mainLoader.progressComplete);
    const theme=vo.__sylPendingTheme;
    if(theme!==undefined)vo.playTheme(theme);
  },0);
}
'''
    return text
