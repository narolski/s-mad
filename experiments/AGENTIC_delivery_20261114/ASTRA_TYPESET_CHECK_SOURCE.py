from pathlib import Path
import hashlib,json,re,subprocess,functools
D=Path(__file__).parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((D/'TYPESET_PACKAGE_MANIFEST.json').read_text());assert len(m['files'])==21
for x in m['files']:assert H(D/x['path'])==x['sha256'] and (D/x['path']).stat().st_size==x['bytes']
tables=[]
for si,name in enumerate(['pools_summary.md','result.md','tt1_read_tables.md','tt1_read_fs_tables.md'],1):
 lines=(D/name).read_text().splitlines();i=0;ti=0
 def split(s):
  # State-aware split: an escaped pipe is content, never a column boundary.
  s=s.strip()[1:-1];out=[];part='';escaped=False
  for c in s:
   if c=='|' and not escaped:out.append(part.strip());part=''
   else:part+=c
   escaped=(c=='\\' and not escaped)
  out.append(part.strip());return out
 while i<len(lines)-1:
  if lines[i].lstrip().startswith('|') and re.fullmatch(r'[\s|:\-]+',lines[i+1]):
   h=split(lines[i]);i+=2;rr=[]
   while i<len(lines) and lines[i].lstrip().startswith('|'):rr.append(split(lines[i]));i+=1
   ti+=1;tables.append((f'{si}.{ti}',name,h,rr))
  else:i+=1
j=json.loads((D/'supplement_table_cells.json').read_text());assert len(j)==len(tables)==33
for x,(id,name,h,rr) in zip(j,tables):assert (x['id'],x['source'],x['headers'],x['rows'])==(id,name,h,rr)
tex=(D/'supplement_cvpr.tex').read_text();panels=re.findall(r'\\begin\{table\*\}.*?\\end\{table\*\}',tex,re.S);assert len(panels)==84
mapping={'F̄':r'\(\bar F\)','Ā':r'\(\bar A\)','−':'-','–':'--','…':r'\ldots{}','ρ':r'\(\rho\)','±':r'\(\pm\)','≤':r'\(\le\)','Δ':r'\(\Delta\)','≥':r'\(\ge\)','τ':r'\(\tau\)','≈':r'\(\approx\)','×':r'\(\times\)'}
@functools.lru_cache(None)
def cell(s):
 if not s:return r'\emph{[blank]}'
 for a,b in mapping.items():s=s.replace(a,b)
 s=re.sub(r'`([^`]+)`',lambda m:r'\path{'+m[1]+'}',s)
 return subprocess.check_output(['pandoc','-f','markdown+raw_tex+tex_math_single_backslash','-t','latex','--wrap=none'],input=s,text=True).strip().replace(r'\path{',r'\protect\path{')
k=0;displayed=0;blanks=0
for id,name,h,rr in tables:
 for start in range(1,len(h),3):
  cols=[0]+list(range(start,min(start+3,len(h))))
  for rstart in range(0,len(rr),16):
   p=panels[k];k+=1;assert r'\label{tab:transfer-'+f'{id}.{start}.{rstart}'+'}' in p
   expected=[[h[c] for c in cols]]+[[r[c] for c in cols] for r in rr[rstart:rstart+16]]
   body=p.split('\\toprule\n')[1].split('\\bottomrule')[0].replace('\\midrule\n','')
   wanted=''.join(' & '.join(cell(v) for v in row)+r' \\'+'\n' for row in expected)
   assert body==wanted,(id,start,rstart)
   displayed+=sum(map(len,expected));blanks+=sum(v=='' for row in expected for v in row)
report={'verdict':'PASS_SOURCE_TABLE_FIDELITY','manifest_members_verified':21,'source_tables':len(tables),'panels':k,'source_cells':sum(len(h)*(len(rr)+1) for _,_,h,rr in tables),'displayed_cells':displayed,'displayed_blanks':blanks,'package_manifest_sha256':H(D/'TYPESET_PACKAGE_MANIFEST.json'),'pdf_sha256':H(D/'supplement_cvpr.pdf'),'tex_sha256':H(D/'supplement_cvpr.tex'),'method':'Independent state-aware Markdown table extraction compared with all recorded source cells, then every panel header and row re-converted via Pandoc with reviewed typography mappings and compared exactly with actual TeX. No model/data/score reads.'}
(D/'ASTRA_TYPESET_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
