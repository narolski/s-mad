import sys, html.parser, re
class P(html.parser.HTMLParser):
    def __init__(s):
        super().__init__(); s.tables=[]; s.depth=0; s.row=None; s.cell=None; s.cap=None; s.incap=False
    def handle_starttag(s,t,a):
        if t=='table': s.depth+=1; s.tables.append({'rows':[], 'cap':s.cap}); 
        if t=='tr' and s.depth: s.row=[]
        if t in('td','th') and s.row is not None: s.cell=''
        if t=='figcaption': s.incap=True; s.cap=''
    def handle_endtag(s,t):
        if t=='table': s.depth-=1
        if t in('td','th') and s.cell is not None: s.row.append(re.sub(r'\s+',' ',s.cell).strip()); s.cell=None
        if t=='tr' and s.row is not None: s.tables[-1]['rows'].append(s.row); s.row=None
        if t=='figcaption': s.incap=False
    def handle_data(s,d):
        if s.cell is not None: s.cell+=d
        if s.incap: s.cap+=d
p=P(); p.feed(open(sys.argv[1],encoding='utf8').read())
for i,t in enumerate(p.tables):
    print('=== TABLE',i, (t['cap'] or '')[:200].replace('\n',' '))
    for r in t['rows']: print(' | '.join(r))
