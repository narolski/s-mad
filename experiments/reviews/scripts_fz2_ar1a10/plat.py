import csv, collections
it=list(csv.DictReader(open('/mnt/t7/smad_next/FZ2/read_addon_items.csv')))
print(collections.Counter((r['platform'],r['db']) for r in it if r['key']=='DOSEX10_20'))
print(collections.Counter((r['platform'],r['flagged']) for r in it if r['key']=='X20'))
print(collections.Counter((r['platform'],r['cycle']) for r in it if r['key']=='X20').most_common(12))
cyc=collections.defaultdict(set)
for r in it:
    if r['key']=='X20': cyc[r['cycle']].add(r['platform'])
print('cycles spanning both platforms', sum(len(v)>1 for v in cyc.values()), 'of', len(cyc))
