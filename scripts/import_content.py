"""Import the approved Obsidian copy before rebuilding the three public pages."""
from pathlib import Path
import argparse,json,re
ROOT=Path(__file__).resolve().parent.parent
DEFAULT=Path('/Users/wishingcat/ObsidianNotes/AI Study/❄️进行中/心创组主站-以手予爱.md')

def parse(text):
    def block(title):
        match=re.search(r'^#{2,4} '+re.escape(title)+r'\s*\n(.*?)(?=^#{2,4} |\Z)',text,re.M|re.S)
        if not match: raise ValueError('Missing content section: '+title)
        return match[1].strip()
    def clean(value):
        return re.sub(r'^>\s?', '',value,flags=re.M).replace('**','').strip()
    intro=[clean(p) for p in block('首页').split('\n\n') if p.strip()]
    if len(intro)!=4: raise ValueError('Expected brand, identity, meaning and summary in 首页')
    data={'brand':'以手予爱 ShouYuLove','identity':intro[1],'meaning':intro[2],'summary':intro[3],
          'dream':clean(block('梦想')),'vision':clean(block('愿景')),
          'work':clean(block('我们做什么')),'collaboration':clean(block('我们怎样协作')),
          'principles':[s.removeprefix('- ').strip() for s in block('边界').splitlines() if s.startswith('- ')]}
    if len(data['principles'])!=3: raise ValueError('Expected three original principles')
    metadata=[('signtrace','以手寻语 SignTrace','sign','手语学习','magnifying-glass'),
              ('dictionary','分社手语词典','sign','手语学习','book-open-text'),
              ('chuanqinghuiyi','传情绘意-手语版','sign','互动游戏','game-controller'),
              ('pinhaoke','拼好课','campus','课程工具','book-open-text')]
    projects=[]
    for id,name,collection,category,icon in metadata:
        source=block(name)
        link=re.search(r'^地址：\[[^\]]+\]\((https://[^\s)]+)\)',source,re.M)
        creator=re.search(r'^设计者：(.+)$',source,re.M)
        description=source.split('\n\n',1)[0].strip()
        if not link or not creator or not description:raise ValueError('Incomplete project '+name)
        projects.append(dict(id=id,name=name,collection=collection,category=category,description=description,creator=creator[1].strip(),url=link[1],icon=icon))
    data['collections']={
       'sign':{'name':'手语作品','path':'sign-projects','description':clean(block('为分社、手语、无障碍事业服务：'))},
       'campus':{'name':'燕园服务','path':'campus','description':clean(block('为广大同学服务：'))}}
    return data,projects

def main():
    ap=argparse.ArgumentParser();ap.add_argument('source',nargs='?',type=Path,default=DEFAULT);args=ap.parse_args()
    source=args.source.read_text(); data,projects=parse(source)
    for name,obj in [('site-content.json',data),('projects.json',projects)]:
        (ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'content-source.md').write_text(source)
    print('Imported original copy and four project records; no source-note changes.')
if __name__=='__main__':main()
