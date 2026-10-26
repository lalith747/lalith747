#!/usr/bin/env python3
"""Build Lalith's self-contained animated profile SVGs from public GitHub data."""
from __future__ import annotations
import io, json, re, urllib.request
from collections import Counter
from datetime import date, timedelta
from html.parser import HTMLParser
from pathlib import Path
from xml.sax.saxutils import escape
from PIL import Image, ImageEnhance, ImageOps
ROOT=Path(__file__).resolve().parents[1]
USER='lalith747'
AVATAR='https://avatars.githubusercontent.com/u/208427940?v=4'
PALETTE=['#161b22','#0e4429','#006d32','#26a641','#39d353','#69f0a0']
class CalendarParser(HTMLParser):
 def __init__(self): super().__init__(); self.days=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='td' and a.get('data-date'):
   m=re.search(r'([\d,]+) contribution',a.get('aria-label',''),re.I)
   n=int(m.group(1).replace(',','')) if m else int(a.get('data-count','0'))
   self.days.append({'date':date.fromisoformat(a['data-date']),'count':n,'level':int(a.get('data-level','0'))})
def get(url):
 req=urllib.request.Request(url,headers={'User-Agent':'lalith747-profile-art'})
 with urllib.request.urlopen(req,timeout=30) as r: return r.read()
def fetch_days():
 p=CalendarParser(); p.feed(get(f'https://github.com/users/{USER}/contributions').decode('utf-8'))
 if not p.days: raise RuntimeError('Could not parse GitHub contribution calendar')
 return sorted(p.days,key=lambda x:x['date'])
def contribution_svg(days):
 first,last=days[0]['date'],days[-1]['date']; sunday=first-timedelta(days=(first.weekday()+1)%7)
 weeks=max(53,(last-sunday).days//7+1); lookup={d['date']:d for d in days}
 total=sum(d['count'] for d in days); best=max(days,key=lambda d:d['count']); longest=streak=0; prev=None
 for d in days:
  if d['count']:
   streak=streak+1 if prev==d['date']-timedelta(days=1) else 1; longest=max(longest,streak)
  else: streak=0
  prev=d['date']
 counts={d['date']:d['count'] for d in days}; cursor=date.today() if counts.get(date.today(),0) else date.today()-timedelta(days=1); current=0
 while counts.get(cursor,0): current+=1; cursor-=timedelta(days=1)
 left,top=46,28; out=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 172" role="img" aria-labelledby="t d"><title id="t">lalith747 contributions</title><desc id="d">Animated 53-week contribution calendar</desc><rect width="100%" height="100%" rx="12" fill="#0d1117"/><style>text{font-family:ui-monospace,monospace;fill:#8b949e}</style>']; seen=set()
 for col in range(weeks):
  week=sunday+timedelta(days=7*col); month=week.strftime('%b')
  if month not in seen: out.append(f'<text x="{left+col*14}" y="16" font-size="9">{month}</text>'); seen.add(month)
  for row in range(7):
   day=week+timedelta(days=row); item=lookup.get(day)
   if item:
    delay=col*.018+row*.03; color=PALETTE[min(5,item['level'])]
    out.append(f'<rect x="{left+col*14}" y="{top+row*14}" width="10" height="10" rx="2" fill="{color}" data-date="{day}" data-count="{item["count"]}"><animate attributeName="opacity" values="0;1" dur=".35s" begin="{delay:.2f}s" fill="freeze"/></rect>')
 out.append(f'<text x="10" y="151" font-size="10">{total:,} contributions · current streak {current} days · longest {longest} days</text>')
 out.append(f'<text x="10" y="166" font-size="9">Best day: {best["date"]} ({best["count"]}) · monthly totals in data/contributions.json</text>')
 for i,c in enumerate(PALETTE): out.append(f'<rect x="736" y="116" width="9" height="9" rx="2" fill="{c}"/>')
 return ''.join(out)+'</svg>'
def portrait_svg():
 im=Image.open(io.BytesIO(get(AVATAR))).convert('RGB'); im=ImageOps.fit(im,(48,32),method=Image.Resampling.LANCZOS,centering=(.5,.42)); im=ImageEnhance.Contrast(ImageOps.grayscale(im)).enhance(1.7)
 ramp=' .`:-=+*cs#%@'; lines=[''.join(ramp[min(len(ramp)-1,im.getpixel((x,y))*len(ramp)//256)] for x in range(48)).rstrip() for y in range(32)]
 out=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 410 410 455" role="img" aria-labelledby="t d"><title id="t">Animated ASCII portrait of T Lalith Krishna</title><desc id="d">Monochrome avatar rendered in animated terminal text</desc><rect x="0" y="410" width="410" height="455" rx="12" fill="#0d1117"/><text x="10" y="432" fill="#8b949e" font-family="monospace" font-size="10">lalith747@github:~$ whoami</text>']
 for i,line in enumerate(lines):
  y=449+i*13; out.append(f'<clipPath id="r{i}"><rect x="0" y="{y-10}" width="0" height="13"><animate attributeName="width" from="0" to="400" dur=".42s" begin="{.25+i*.10:.2f}s" fill="freeze"/></rect></clipPath><text x="10" y="{y}" clip-path="url(#r{i})" xml:space="preserve" fill="#c9d1d9" font-family="ui-monospace,monospace" font-size="10">{escape(line)}</text>')
 return ''.join(out)+'</svg>'
def info_svg():
 rows=[('Name','T Lalith Krishna'),('Now','Entrepreneur · AI · Healthcare · Tech'),('Builds','At the intersection of AI and healthcare'),('Featured','protein-viz_new · HireFlow-AI_Hack-w-Hyd'),('Also','epc-intelligence-hackathon · portfolio'),('Web','lalith747.github.io/portfolio/')]
 out=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 490 270" role="img" aria-labelledby="t d"><title id="t">T Lalith Krishna profile card</title><desc id="d">Terminal-style profile and featured work</desc><rect width="490" height="270" rx="12" fill="#0d1117" stroke="#30363d"/><path d="M0 42h490" stroke="#30363d"/><circle cx="20" cy="21" r="5" fill="#ff7b72"/><circle cx="38" cy="21" r="5" fill="#d29922"/><circle cx="56" cy="21" r="5" fill="#3fb950"/><text x="78" y="25" fill="#8b949e" font-family="monospace" font-size="12">lalith747 — profile</text>']
 for i,(key,val) in enumerate(rows):
  y=72+i*31; delay=.25+i*.16
  for x,text,color in [(22,key,'#79c0ff'),(108,val,'#c9d1d9')]: out.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="monospace" font-size="12" opacity="0">{escape(text)}<animate attributeName="opacity" from="0" to="1" dur=".45s" begin="{delay:.2f}s" fill="freeze"/><animate attributeName="x" from="{x+8}" to="{x}" dur=".45s" begin="{delay:.2f}s" fill="freeze"/></text>')
 return ''.join(out)+'</svg>'
def main():
 days=fetch_days(); (ROOT/'data').mkdir(exist_ok=True); monthly=Counter()
 for d in days: monthly[d['date'].strftime('%Y-%m')]+=d['count']
 payload={'username':USER,'days':[{'date':d['date'].isoformat(),'count':d['count'],'level':d['level']} for d in days],'monthly_totals':dict(sorted(monthly.items()))}
 (ROOT/'data/contributions.json').write_text(json.dumps(payload,indent=2)+'\n')
 (ROOT/'contrib-heatmap.svg').write_text(contribution_svg(days)+'\n'); (ROOT/'ascii-portrait.svg').write_text(portrait_svg()+'\n'); (ROOT/'info-card.svg').write_text(info_svg()+'\n')
if __name__=='__main__': main()
