// Original brand surface shaders. Textures and relief geometry are generated locally.
export const fullscreenVertex = `precision highp float;
attribute vec3 position;attribute vec2 uv;varying vec2 vUv;
void main(){vUv=uv;gl_Position=vec4(position,1.);}`;
export const extrusionFlowVertex = fullscreenVertex;
export const extrusionFlowFragment = `precision highp float;
varying vec2 vUv;uniform sampler2D tMap,tNoise;uniform float uFalloff,uAlpha,uDissipation,uDeltaMult,uOffset,uAspect,uTime;
uniform vec2 uMouse,uVelocity,uMouse2,uVelocity2;
vec4 mark(vec2 p,vec2 v){vec2 d=(vUv-p)*vec2(uAspect,1.);vec2 speed=v*50.;float m=1.-pow(1.-min(1.,length(speed)),2.);return vec4(speed,m,1.)*smoothstep(uFalloff,0.,length(d))*uAlpha;}
void main(){vec4 old=texture2D(tMap,vUv+vec2(0.,uOffset));old/=1.+uDeltaMult*(1./uDissipation-1.);vec2 p=vUv*vec2(uAspect,1.);
float a=smoothstep(.4,1.,texture2D(tNoise,p*.35+uTime*.01).g);float b=.15+.85*smoothstep(.4,1.,texture2D(tNoise,p*.8+uTime*.01).g);
vec4 self=mark(uMouse2,uVelocity2)*3.;self.a=self.b;self.rg=vec2(0.);vec4 value=old+(mark(uMouse,uVelocity)*b+self*a)*uDeltaMult;value=min(value,vec4(1.));value.rgb=max(value.rgb,vec3(-1.));gl_FragColor=value;}`;

const fastField = `
vec2 field(vec2 p){float t=uTime*2.;vec3 n=.5*(texture2D(tNoise,p/7.77+t*.007).rgb+texture2D(tNoise,p/7.77-t*.007).rgb);vec3 a=sin(vec3(t,t+1.047,t+2.094));a/=max(.001,dot(abs(a),vec3(1./3.)));vec3 b=sin(vec3(t+1.047,t+2.094,t));b/=max(.001,dot(abs(b),vec3(1./3.)));vec3 direction=normalize(n-.5+vec3(.0001));vec2 wave=smoothstep(vec2(-1.),vec2(1.),vec2(dot(direction,a),dot(direction,b)));return 1.-sqrt(max(vec2(0.),1.-wave*wave));}
`;
export const surfaceVertex = `uniform sampler2D tFlow,tNoise;uniform float uTime,uFast,uOpacity,uScreenScroll,uCompact;
varying vec2 vUv;varying vec3 vNormal;varying vec3 vWorld;
${fastField}
void main(){vUv=uv;vec3 rest=position;rest.x-=uCompact*2.6*clamp(position.x/3.25,-1.,1.);vec3 n=normal;if(abs(position.x)<3.25)n.x/=1.-uCompact*.8;vNormal=normalize(normalMatrix*n);vec4 projected=projectionMatrix*modelViewMatrix*vec4(rest,1.);vec2 screen=.5+.5*projected.xy/projected.w;vec4 flow=texture2D(tFlow,screen);float reveal=mix(.02+dot(flow.ba,vec2(.5)),field(screen-vec2(0.,uScreenScroll)).x*1.02,uFast)*uOpacity;vec3 pos=rest;pos.z*=mix(.05,1.,clamp(reveal,0.,1.));vec4 world=modelMatrix*vec4(pos,1.);vWorld=world.xyz;gl_Position=projectionMatrix*viewMatrix*world;}`;
const surfaceColor = `
vec3 rgbToHsv(vec3 c){vec4 k=vec4(0.,-1./3.,2./3.,-1.);vec4 p=mix(vec4(c.bg,k.wz),vec4(c.gb,k.xy),step(c.b,c.g));vec4 q=mix(vec4(p.xyw,c.r),vec4(c.r,p.yzx),step(p.x,c.r));float d=q.x-min(q.w,q.y);return vec3(abs(q.z+(q.w-q.y)/(6.*d+1.e-10)),d/(q.x+1.e-10),q.x);}
vec3 hsvToRgb(vec3 c){vec3 p=abs(fract(c.xxx+vec3(0.,2./3.,1./3.))*6.-3.);return c.z*mix(vec3(1.),clamp(p-1.,0.,1.),c.y);}
vec3 stone(float shade,vec2 world,vec2 screen){float grain=texture2D(tPlaster,world/10.).g;float gradient=mix(1.,.5,length(screen-vec2(0.,.8)));vec3 light=vec3((shade*grain+gradient*.7*.17)*uBrightness.x+uBrightness.y);vec3 dark=vec3(.075+(shade-.54504)*.15+(grain-.95)*.07);return mix(light,dark,uDark);}
`;
export const surfaceFragment = `precision highp float;
uniform sampler2D tFlow,tNoise,tPlaster,tBakeHigh,tBakeLow,tFluid;uniform vec2 uResolution,uBrightness,uBakeTexel;uniform float uTime,uFast,uOpacity,uDark,uScreenScroll,uSceneY;
varying vec2 vUv;varying vec3 vNormal,vWorld;
${fastField}${surfaceColor}
void main(){vec2 screen=gl_FragCoord.xy/uResolution;vec4 flow=texture2D(tFlow,screen)*2.;vec2 waves=field(screen-vec2(0.,uScreenScroll));float e=mix(.02+dot(flow.ba,vec2(.5)),waves.x*1.02,uFast)*uOpacity;vec2 bakeUv=vUv*(1.-uBakeTexel)+uBakeTexel*.5;vec3 high=texture2D(tBakeHigh,bakeUv).rgb;vec3 low=texture2D(tBakeLow,bakeUv).rgb;float shade=.54504;shade=mix(shade,low.g,smoothstep(0.,.2,e));shade=mix(shade,low.r,smoothstep(.2,.4,e));shade=mix(shade,high.b,smoothstep(.4,.6,e));shade=mix(shade,high.g,smoothstep(.6,.8,e));shade=mix(shade,high.r,smoothstep(.8,1.,e));vec3 color=stone(shade,vWorld.xy-vec2(0.,uSceneY),screen);
vec3 normal=normalize(vNormal);vec3 n=normal;n.z*=2.;n=normalize(n);vec3 hue=rgbToHsv((n+1.)*.5);hue.x=fract(hue.x-.52);vec3 fluid=texture2D(tFluid,screen).rgb+waves.y*uFast*2.;float inverseFresnel=1.-pow(1.-abs(normal.z),35.);float edge=max(smoothstep(1.,.1,mix(inverseFresnel,1.,.02)),smoothstep(.42,.2,high.r)*.25);float tint=clamp(edge*smoothstep(0.,1.,fluid.b*.15)*.57*uOpacity,0.,.5)*(1.-uDark);color=mix(color,hsvToRgb(hue),tint);color=mix(color,.76+.16*color,uFast*(1.-uDark));gl_FragColor=vec4(color,1.);}`;
export const backgroundFragment = `precision highp float;
uniform sampler2D tPlaster;uniform vec2 uResolution,uBrightness,uWorldSize;uniform float uDark,uSceneY,uFast;
varying vec2 vUv;${surfaceColor}
void main(){vec3 color=stone(.54504,(vUv-.5)*uWorldSize-vec2(0.,uSceneY),vUv);color=mix(color,.76+.16*color,uFast*(1.-uDark));gl_FragColor=vec4(color,1.);}`;

// Standard incompressible-fluid steps, implemented explicitly to keep the field independent.
export const fluidVertex = `precision highp float;attribute vec3 position;attribute vec2 uv;uniform vec2 texelSize;varying vec2 vUv,vL,vR,vT,vB;
void main(){vUv=uv;vL=uv-vec2(texelSize.x,0.);vR=uv+vec2(texelSize.x,0.);vT=uv+vec2(0.,texelSize.y);vB=uv-vec2(0.,texelSize.y);gl_Position=vec4(position,1.);}`;
const fluidHeader = `precision highp float;varying vec2 vUv,vL,vR,vT,vB;`;
export const fluidClear = `${fluidHeader}uniform sampler2D uTexture;uniform float value;void main(){gl_FragColor=texture2D(uTexture,vUv)*value;}`;
export const fluidSplat = `${fluidHeader}uniform sampler2D uTarget;uniform vec3 color;uniform vec2 point;uniform float aspectRatio,radius;
void main(){vec2 d=(vUv-point)*vec2(aspectRatio,1.);gl_FragColor=vec4(texture2D(uTarget,vUv).rgb+exp(-dot(d,d)/max(radius,.000001))*color,1.);}`;
export const fluidAdvect = `${fluidHeader}uniform sampler2D uVelocity,uSource;uniform vec2 texelSize;uniform float dt,dissipation;
void main(){vec2 previous=vUv-dt*texture2D(uVelocity,vUv).xy*texelSize;gl_FragColor=vec4(texture2D(uSource,previous).rgb*dissipation,1.);}`;
export const fluidDivergence = `${fluidHeader}uniform sampler2D uVelocity;
void main(){float l=texture2D(uVelocity,vL).x;float r=texture2D(uVelocity,vR).x;float t=texture2D(uVelocity,vT).y;float b=texture2D(uVelocity,vB).y;vec2 c=texture2D(uVelocity,vUv).xy;if(vL.x<0.)l=-c.x;if(vR.x>1.)r=-c.x;if(vT.y>1.)t=-c.y;if(vB.y<0.)b=-c.y;gl_FragColor=vec4(.5*(r-l+t-b),0.,0.,1.);}`;
export const fluidCurl = `${fluidHeader}uniform sampler2D uVelocity;
void main(){float l=texture2D(uVelocity,vL).y;float r=texture2D(uVelocity,vR).y;float t=texture2D(uVelocity,vT).x;float b=texture2D(uVelocity,vB).x;gl_FragColor=vec4(.5*(r-l-t+b),0.,0.,1.);}`;
export const fluidVorticity = `${fluidHeader}uniform sampler2D uVelocity,uCurl;uniform float curl,dt;
void main(){float l=texture2D(uCurl,vL).x;float r=texture2D(uCurl,vR).x;float t=texture2D(uCurl,vT).x;float b=texture2D(uCurl,vB).x;vec2 f=.5*vec2(abs(t)-abs(b),abs(r)-abs(l));f/=length(f)+.0001;f*=curl*texture2D(uCurl,vUv).x;f.y=-f.y;gl_FragColor=vec4(texture2D(uVelocity,vUv).xy+f*dt,0.,1.);}`;
export const fluidPressure = `${fluidHeader}uniform sampler2D uPressure,uDivergence;
void main(){float sum=texture2D(uPressure,vL).x+texture2D(uPressure,vR).x+texture2D(uPressure,vB).x+texture2D(uPressure,vT).x;gl_FragColor=vec4((sum-texture2D(uDivergence,vUv).x)*.25,0.,0.,1.);}`;
export const fluidGradientSubtract = `${fluidHeader}uniform sampler2D uPressure,uVelocity;
void main(){vec2 g=vec2(texture2D(uPressure,vR).x-texture2D(uPressure,vL).x,texture2D(uPressure,vT).x-texture2D(uPressure,vB).x);gl_FragColor=vec4(texture2D(uVelocity,vUv).xy-g,0.,1.);}`;
