"""Reads source/conditional templates only; never executes scientific producer."""
import hashlib,json,pathlib,subprocess,unittest
B=pathlib.Path(__file__).resolve().parents[1]
class PolicySource(unittest.TestCase):
    def test_exact_cohorts_and_common_roles(self):
        p=json.loads((B/'POLICY.json').read_text());self.assertEqual({k:len(v) for k,v in p['cohorts'].items()},{'SbFM':20,'GX':15,'SbMR':25,'SbM':25,'Sb512':30,'SbMR512':30,'Sbc':25,'DINOv3':20})
        self.assertEqual(sum(len(v) for k,v in p['ab1_tasks'].items() if k!='GX'),70)
        for branch,rows in p['ab1_tasks'].items():
            for row in rows:
                self.assertEqual(row['branch'],branch);self.assertIn(row['seed'],range(413,418));self.assertIn(row['producer_arm'],['AB1_A','AB1_B','AB1_Sb'])
        self.assertEqual(p['ab1_tasks']['GX'],[])
    def test_original_math_text_and_last_checkpoint_retention(self):
        p=json.loads((B/'POLICY.json').read_text());original=pathlib.Path(p['original_parent_path']);s=original.read_text();f=(B/'source/run_ab1_fresh.sh').read_text()
        self.assertEqual(hashlib.sha256(original.read_bytes()).hexdigest(),p['fixed']['original_parent_sha256'])
        self.assertIn(s[s.index('py "$W/pn1/code/smadcvpr/train.py"'):s.index('[ -f "$RUN/last.pt" ]')],f)
        self.assertIn(s[s.index('py "$W/pn1/src/pn1_score.py"'):s.index('cp "$RUN/meta.json"')],f)
        self.assertIn('413|414|415|416|417',f);self.assertNotIn('case "$SEED" in 408',f)
        self.assertLess(f.index('worker_gate.py'),f.index('source "$TASK_DIR/task.env"'))
        self.assertIn('NEXT_CONFIRM_TASK_DURABLE',f);self.assertIn('last.pt.part',f)
        subprocess.run(['bash','-n',str(B/'source/run_ab1_fresh.sh')],check=True)
    def test_self_sourcepins_match(self):
        p=json.loads((B/'POLICY.json').read_text())
        for path,h in p['source_pins'].items():
            name=pathlib.Path(path).name;self.assertEqual(hashlib.sha256((B/'source'/name).read_bytes()).hexdigest(),h)
if __name__=='__main__':unittest.main(verbosity=2)
