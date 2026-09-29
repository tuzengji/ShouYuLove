"""Import the approved Obsidian copy before rebuilding the three public pages."""
from pathlib import Path
import argparse,json,re
ROOT=Path(__file__).resolve().parent.parent
DEFAULT=Path('/Users/wishingcat/ObsidianNotes/AI Study/❄️进行中/心创组主站-以手予爱.md')

def parse(text):
    def block(title, required=True):
        match=re.search(r'^#{2,4} '+re.escape(title)+r'\s*\n(.*?)(?=^#{2,4} |\Z)',text,re.M|re.S)
        if not match:
            if required: raise ValueError('Missing content section: '+title)
            return ''
        return match[1].strip()
    def clean(value):
        return re.sub(r'^>\s?', '',value,flags=re.M).replace('**','').strip()
    intro=[clean(p) for p in block('首页').split('\n\n') if p.strip()]
    if len(intro) not in (3,4): raise ValueError('Expected brand, identity, meaning and optional summary in 首页')
    data={'brand':'以手予爱 ShouYuLove','identity':intro[1],'meaning':intro[2],'summary':intro[3] if len(intro)==4 else '',
          'dream':clean(block('梦想')),'vision':clean(block('愿景')),
          'work':clean(block('我们做什么',False)),'collaboration':clean(block('我们怎样协作',False)),
          'principles':[s.removeprefix('- ').strip() for s in block('边界').splitlines() if s.startswith('- ')]}
    if len(data['principles'])!=3: raise ValueError('Expected three original principles')
    data['collections']={
       'sign':{'name':'核心创意','path':'sign-projects','description':clean(block('核心创意'))},
       'campus':{'name':'其他作品','path':'campus','description':clean(block('其他作品'))}}
    metadata=[('signtrace','以手寻语 SignTrace','sign','手语学习','magnifying-glass'),
              ('dictionary','分社手语词典','sign','手语学习','book-open-text'),
              ('chuanqinghuiyi','传情绘意-手语版','sign','互动游戏','game-controller'),
              ('pinhaoke','拼好课','campus','课程工具','book-open-text'),
              ('beida-zhidao','北大知道','campus','校园服务','book-open-text'),
              ('qinghua-zhidao','清华知道','campus','校园服务','book-open-text')]
    projects=[]
    for id,name,collection,category,icon in metadata:
        source=block(name)
        link=re.search(r'^地址：(?:\[[^\]]+\]\()?((?:https?://)[^\s)]+)\)?',source,re.M)
        creator=re.search(r'^设计者：(.+)$',source,re.M)
        description='\n\n'.join(part.strip() for part in source.split('\n\n') if not re.match(r'^(地址|设计者)：',part.strip())).strip()
        if not description and collection == 'campus': description='心创组成员开发的校园服务工具。'
        if not link or not creator or not description:raise ValueError('Incomplete project '+name)
        projects.append(dict(id=id,name=name,collection=collection,category=category,description=description,creator=creator[1].strip(),url=link[1],icon=icon,logo=f'home-assets/logos/{id}.svg'))
    members=[line.strip() for line in block('心创组第一届成员',False).splitlines() if line.strip() and not line.lstrip().startswith(('-', '*'))]
    if not members: raise ValueError('Missing first-generation members')
    data['members']=members
    return data,projects

def main():
    ap=argparse.ArgumentParser();ap.add_argument('source',nargs='?',type=Path,default=DEFAULT);args=ap.parse_args()
    source=args.source.read_text(); data,projects=parse(source)
    for name,obj in [('site-content.json',data),('projects.json',projects)]:
        (ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'content-source.md').write_text(source)
    print(f'Imported original copy and {len(projects)} project records with {len(data["members"])} members; no source-note changes.')
if __name__=='__main__':main()
