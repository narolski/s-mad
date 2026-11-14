"""Adopted ordered calibration/evaluation metadata, never candidate arrays."""
import json
import pathlib
import policy as P
import shared


def load(binding,dev_spec):
    populations={key:json.loads(pathlib.Path(binding[key+'_path']).read_text()) for key in ('calibration','positive_evaluation','genuine_evaluation')}
    C=populations['calibration'];E=populations['positive_evaluation'];G=populations['genuine_evaluation']
    assert len(C)==70 and len(E)==180 and len(G)==288
    assert len({r['component'] for r in C})==26 and len({r['component'] for r in E})==27
    assert len({r['id'] for r in C+E+G})==538,'duplicate/overlapping population IDs'
    assert sum(r['source']=='feret' for r in C)==42 and sum(r['source']=='frgc' for r in C)==28
    for key,rows in populations.items():
        label=0 if key=='genuine_evaluation' else 1
        for r in rows:
            assert r['id'] in dev_spec['ids'] and int(r['label'])==label and r['role']=='dev'
            assert r['source'] in ('feret','frgc') and r['component'].startswith(r['source']+':')
            assert r['training_person_overlap']==r['training_photo_overlap']==[] and r['training_component_overlap'] is False
            assert r['persons'] and r['photos']
    evaluation=E+G
    for field in ('persons','photos'):
        cal={x for r in C for x in r[field]};ev={x for r in evaluation for x in r[field]}
        assert not cal&ev,'calibration/evaluation source overlap '+field
    assert not {r['component'] for r in C}&{r['component'] for r in evaluation}
    cells=[]
    for source,processing in P.CELLS:
        ii=[i for i,r in enumerate(evaluation) if int(r['label'])==0 and (r['source'],r['processing'])==(source,processing)]
        expected=(70,20) if source=='feret' else (26,14)
        assert (len(ii),len({evaluation[i]['component'] for i in ii}))==expected
        cells.append({'source':source,'processing':processing,'indices':ii,'rows':len(ii),'components':expected[1]})
    guards=[]
    for family,count,components in zip(P.FAMILIES,(146,0,17,17),(10,0,17,17)):
        ii=[i for i,r in enumerate(evaluation) if int(r['label'])==1 and r['positive_family']==family]
        assert len(ii)==count and len({evaluation[i]['component'] for i in ii})==components
        guards.append({'family':family,'indices':ii,'rows':count,'components':components})
    return {'calibration':C,'evaluation':evaluation,'positive_evaluation':E,'genuine_evaluation':G,
            'genuine_cells':cells,'positive_guards':guards,'calibration_components':26}
