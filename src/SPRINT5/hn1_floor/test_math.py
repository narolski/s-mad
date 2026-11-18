"""Only synthetic scores; AST loads the two pure statistic helpers, not runner."""
import ast,pathlib,numpy as np
source=pathlib.Path(__file__).with_name('fit.py');tree=ast.parse(source.read_text());nodes=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ('aucs','stat')]
y=np.tile([0,1],125);d=np.repeat(np.arange(5),50);keys=[str(x) for x in range(9)];g={'np':np,'y':y,'d':d,'keys':keys};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source),'exec'),g)
for mode,expected in [('perfect',1.),('tied',.5),('reverse',0.)]:
 s=y if mode=='perfect' else (1-y if mode=='reverse' else np.ones(len(y)))
 g['matrix']=np.tile(s,(9,1));assert np.allclose(g['stat'](np.arange(len(y))),expected)
g['matrix']=np.tile(y,(9,1));assert g['stat'](np.arange(50)) is None
print('PASS syntheticperfect/ties/reversed/missingstratum; nofeature/model/results read')
