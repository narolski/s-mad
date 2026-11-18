"""Authoritative-label admission [SPRINT5-5]; metadata only, no inferred labels."""
import argparse
import collections
import csv
import hashlib
import json
import pathlib

BASE=pathlib.Path('/mnt/t7/smad_next/MS1/celebahq')
LABELS=pathlib.Path('/mnt/t7/Datasety/datasets_processed/data-celeb-aligned/split.csv')


def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mapping',type=pathlib.Path)
    ap.add_argument('--identity',type=pathlib.Path)
    ap.add_argument('--out',type=pathlib.Path,required=True)
    a=ap.parse_args();assert not a.out.exists();a.out.mkdir(parents=True)
    labels=list(csv.DictReader(LABELS.open()))
    official={r['image_id']:r for r in labels}
    assert len(official)==len(labels)==202084
    report={'status':'LABEL_MAPPING_MISSING','label_path':str(LABELS),'label_sha256':sha(LABELS),
       'labelled128_images':len(labels),'labelled128_identities':len({r['person_id'] for r in labels}),
       'warning':'persons.csv embedding-components are not identity truth; never substituted',
       'mining':'NOT_RUN','fits':'NOT_RUN','mapping':None}
    truth={k:v['person_id'] for k,v in official.items()}
    if a.identity:
        truth={}
        for line in a.identity.read_text().splitlines():
            image,person=line.split();assert image not in truth;truth[image]=person
        assert len(truth)==202599
        assert all(truth[k]==r['person_id'] for k,r in official.items())
        report['official_identity']={'path':str(a.identity),'sha256':sha(a.identity),'images':len(truth),'historical_label_disagreements':0}
    if a.mapping is not None:
        # Official CelebAMask-HQ whitespace-delimited idx/orig_idx/orig_file mapping.
        lines=a.mapping.read_text().splitlines()
        header=next(i for i,l in enumerate(lines) if 'orig_file' in l and 'idx' in l)
        fields=lines[header].split();rows=[];seen=set()
        for line in lines[header+1:]:
            if not line.strip():continue
            values=line.split();assert len(values)==len(fields)
            m=dict(zip(fields,values));idx=int(m['idx']);assert idx not in seen;seen.add(idx)
            original=m['orig_file'];assert original in truth
            r=official.get(original)
            rows.append({'OFFICIAL_PGGAN_index':str(idx),'image_id':original,'person_id':truth[original],
                         'original_split':r['split'] if r else 'UNKNOWN_EXCLUDED',
                         'local_image_binding':'UNVERIFIED_DO_NOT_ATTACH_TO_EMBEDDINGS'})
        assert len(rows)==30000 and seen==set(range(30000))
        with (a.out/'OFFICIAL_IDENTITY_CATALOGUE_NOT_LOCAL.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
        report.update(status='OFFICIAL_CATALOGUE_JOINED_LOCAL_IMAGE_BINDING_HOLD',mapping={'path':str(a.mapping),'sha256':sha(a.mapping)},
          hq_images=len(rows),hq_identities=len({r['person_id'] for r in rows}),
          missing_historical_split=sum(r['original_split']=='UNKNOWN_EXCLUDED' for r in rows),
          local_binding_blocker='LocalZIP one-based00001..30000 vs officialzero-based0..29999; sampledPNG/RGBmd5s did not establish correspondence. No i-1 assumption permitted.')
    report['remaining_before_mining']=['verified official-index to ACTUAL local image/embedding correspondence',
       'authoritative sex/pose/IED/landmark metadata',
       'source person-component train/calibration/eval split and MS1-heldout exclusion',
       'labelled128 calibration and injected-noise filter thresholds',
       'independent eligibility review before any pairing search',
       'no new sealed-set embedding references without applicable authorization']
    (a.out/'inventory.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':main()
