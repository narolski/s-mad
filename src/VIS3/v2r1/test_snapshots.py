"""Generated control replacement/mutation fixtures. No real scientific payload/effect."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import authority_snapshot as A
import contracts as K
import construct_driver as D
import numeric_worker as N


def digest(raw):return hashlib.sha256(raw).hexdigest()


class Controls(unittest.TestCase):
    def test_replacements_samecapturedbytes_all_control_kinds(self):
        # Replaces the PATH after fd read but BEFORE hashing; old expected accepts ONLY old bytes.
        names=['root_grant','inventory','constructed_receipt','admission','roster','smoke_review','source_manifest']
        for name in names:
            with self.subTest(control=name),tempfile.TemporaryDirectory() as tmp:
                p=Path(tmp)/name
                before=b'a'*64+b'  old.py\n' if name=='source_manifest' else b'{"scope":"PINNED_OLD"}'
                after=b'b'*64+b'  other.py\n' if name=='source_manifest' else b'{"scope":"UNTRUSTED_REPLACEMENT"}'
                p.write_bytes(before);original_read=os.read;changed=[False]
                def swap(fd,n):
                    raw=original_read(fd,n)
                    if raw and not changed[0]:
                        q=p.with_suffix('.new');q.write_bytes(after);q.replace(p);changed[0]=True
                    return raw
                with patch.object(A.os,'read',side_effect=swap):
                    with self.assertRaises(ValueError):A.capture_bytes(p,digest(before))
                self.assertEqual(p.read_bytes(),after)
                # Expecting the later path digest cannot authenticate the captured old bytes.
                p.write_bytes(before);changed[0]=False
                with patch.object(A.os,'read',side_effect=swap):
                    with self.assertRaises(ValueError):A.capture_bytes(p,digest(after))
                # Replacement completed before capture also fails old expected SHA.
                with self.assertRaises(ValueError):A.capture_bytes(p,digest(before))

    def test_aftercapture_replacement_cannot_change_parsed_object(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'grant';raw=b'{"scope":"PINNED"}';p.write_bytes(raw)
            original=json.loads
            def replace_before_parse(captured,**kw):
                p.write_bytes(b'{"scope":"UNTRUSTED"}')
                return original(captured,**kw)
            with patch.object(A.json,'loads',side_effect=replace_before_parse):snap=A.capture_json(p,digest(raw))
            self.assertEqual(snap.value['scope'],'PINNED');self.assertEqual(snap.sha256,digest(raw))
            self.assertEqual(p.read_bytes(),b'{"scope":"UNTRUSTED"}')

    def test_admission_roster_smoke_fail_before_any_payload_or_effect(self):
        for failed in ['admission','roster','smoke']:
            with self.subTest(control=failed),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);rp=root/'CONSTRUCTION_RECEIPT.json';rosterp=root/'DERIVED_INPUT_ROSTER.json';ap=root/'admission.json'
                roster=[]
                for ident in K.IDS:
                    host='00042' if ident.startswith('42') else '00056'
                    donor=host if ident.endswith('samephoto') else ('00056' if host=='00042' else '00042')
                    roster.append({'id':ident,'host_photo':host,'donor_photo':donor,'host_history':'native512 only','path':str(root/(ident+'.png'))})
                roster_raw=json.dumps(roster).encode();rosterp.write_bytes(roster_raw);rh=digest(roster_raw)
                receipt={'author':'author','status':'COMPLETE_PRIVATE_CONSTRUCTION_ONLY','inventory_sha256':'1'*64,'derivative_roster_sha256':rh,
                         'actual_alpha':{'path':str(root/'mask.npy'),'sha256':'2'*64}}
                receipt_raw=json.dumps(receipt).encode();rp.write_bytes(receipt_raw)
                admission={'decision':'GO_VIS3_PRIVATE_DERIVED_INPUTS','reviewer':'other','author':'author','construction_receipt_sha256':digest(receipt_raw),
                           'inventory_sha256':'1'*64,'derivative_roster_sha256':rh,'render_allowed':False,'publication_allowed':False,'actual_alpha_npy_sha256':'2'*64}
                ar=json.dumps(admission).encode();ap.write_bytes(ar)
                inv={'construction_output':str(root),'repository':str(root),'numeric_output':str(root/'numeric')}
                grant={'construction_receipt_path':str(rp),'construction_receipt_sha256':digest(receipt_raw),'constructed_input_admission_path':str(ap),
                       'constructed_input_admission_sha256':digest(ar),'derivative_roster_sha256':rh}
                if failed=='admission':ap.write_bytes(b'{"decision":"UNTRUSTED"}')
                if failed=='roster':rosterp.write_bytes(b'[]')
                if failed=='smoke':
                    sp=root/'smoke_review.json';sp.write_bytes(b'{"decision":"UNTRUSTED"}')
                    grant.update({'smoke_postreview_path':str(sp),'smoke_postreview_sha256':'0'*64})
                with patch.object(K,'sha') as scientific_hash,patch.object(D,'exact_rgb') as decode,patch.object(Path,'mkdir') as effect:
                    with self.assertRaises(ValueError):
                        if failed=='smoke':N.smoke_admission(inv,grant,{'inventory_sha256':'1'*64,'derivative_roster_sha256':rh},'A')
                        else:N.construction_admission(inv,grant,'1'*64)
                    scientific_hash.assert_not_called();decode.assert_not_called();effect.assert_not_called()

    def test_mutation_same_descriptor_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'control';raw=b'{"scope":"old"}';p.write_bytes(raw);original=os.read;changed=[False]
            def mutate(fd,n):
                chunk=original(fd,n)
                if chunk and not changed[0]:p.write_bytes(b'{"scope":"changed-longer"}');changed[0]=True
                return chunk
            with patch.object(A.os,'read',side_effect=mutate):
                with self.assertRaises(ValueError):A.capture_bytes(p,digest(raw))

    def test_regular_bounded_strict_json_and_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'control';p.write_bytes(b'x'*33)
            with self.assertRaises(ValueError):A.capture_bytes(p,digest(p.read_bytes()),cap=32)
            link=Path(tmp)/'link';link.symlink_to(p)
            with self.assertRaises(OSError):A.capture_bytes(link,digest(p.read_bytes()))
            fifo=Path(tmp)/'fifo';os.mkfifo(fifo)
            with self.assertRaises(ValueError):A.capture_bytes(fifo,'0'*64)
            for raw in [b'{"x":1,"x":2}',b'{"x":NaN}',b'{"x":1e999}',b'[]',b'not-json']:
                p.write_bytes(raw)
                with self.assertRaises(ValueError):A.capture_json(p,digest(raw))
            for raw in [b'a'*64+b'  ../bad.py\n',b'a'*64+b'  /bad.py\n',(b'a'*64+b'  same.py\n')*2,b'a'*64+b'  dir/file.py\n']:
                p.write_bytes(raw);snap=A.capture_bytes(p,digest(raw))
                with self.assertRaises(ValueError):A.manifest_entries(snap)

    def test_root_external_hash_rejects_before_png_hash_decode_or_effect(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root=Path(tmp);grant=root/'grant.json';inventory=root/'inventory.json'
            grant.write_bytes(b'{"issued_by":"root"}');inventory.write_bytes(b'{}')
            with patch.object(K,'sha') as scientific_hash,patch.object(D,'exact_rgb') as decode,patch.object(Path,'mkdir') as effect:
                with self.assertRaises(ValueError):K.authority(inventory,grant,'construct',expected_release_sha256='0'*64)
                scientific_hash.assert_not_called();decode.assert_not_called();effect.assert_not_called()

    def test_replaced_inventory_rejects_before_payload_or_output(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root=Path(tmp);grant=root/'grant.json';inventory=root/'inventory.json'
            old=b'{"scope":"original_inventory"}';inventory.write_bytes(b'{"scope":"replaced_inventory"}')
            raw=json.dumps({'issued_by':'root','phase':'construct','decision':'GO_VIS3_PRIVATE_CPU_CONSTRUCTION',
                            'author':'author','reviewer':'other','inventory_sha256':digest(old)}).encode();grant.write_bytes(raw)
            with patch.object(K,'sha') as scientific_hash,patch.object(D,'exact_rgb') as decode,patch.object(Path,'mkdir') as effect:
                with self.assertRaises(ValueError):K.authority(inventory,grant,'construct',expected_release_sha256=digest(raw))
                scientific_hash.assert_not_called();decode.assert_not_called();effect.assert_not_called()

    def test_replaced_or_unsafe_manifest_before_payload_effects(self):
        # Metadata-only temporary controls inside repository; no real grant/source package altered.
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root=Path(tmp);ip=root/'inventory.json';rp=root/'release.json';review=root/'review.txt';pre=root/'prereg.txt';manifest=root/'SHA256SUMS'
            review.write_bytes(b'SYNTHETIC_REVIEW');pre.write_bytes(b'SYNTHETIC_PREREG')
            inv={'experiment':'VIS3_CONTROLLED_SOFT_SPLICE_V2R1','repository':'/home/narolski/smad-next','prereg_path':str(pre)}
            invraw=json.dumps(inv).encode();ip.write_bytes(invraw)
            old=b'a'*64+b'  safe.py\n';manifest.write_bytes(b'b'*64+b'  replacement.py\n')
            grant={'issued_by':'root','phase':'construct','decision':'GO_VIS3_PRIVATE_CPU_CONSTRUCTION','author':'author','reviewer':'other',
                   'inventory_sha256':digest(invraw),'independent_review_path':str(review),'independent_review_sha256':digest(review.read_bytes()),
                   'prereg_sha256':digest(pre.read_bytes()),'private_noncommercial_only':True,'publication_allowed':False,'render_allowed':False,
                   'source_pixel_export_allowed':True,'source_manifest_sha256':digest(old)}
            for unsafe in [False,True]:
                if unsafe:
                    bad=b'a'*64+b'  ../unsafe.py\n';manifest.write_bytes(bad);grant['source_manifest_sha256']=digest(bad)
                raw=json.dumps(grant).encode();rp.write_bytes(raw)
                with patch.object(K,'__file__',str(root/'contracts.py')),patch.object(K,'sha') as scientific_hash,patch.object(D,'exact_rgb') as decode,patch.object(Path,'mkdir') as effect:
                    with self.assertRaises(ValueError):K.authority(ip,rp,'construct',expected_release_sha256=digest(raw))
                    scientific_hash.assert_not_called();decode.assert_not_called();effect.assert_not_called()

    def test_downstream_control_badsha_precedes_image_decode_output(self):
        # Actual downstream function, not mocked hash/parse. Wrong captured receipt hash is fatal.
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=root/'CONSTRUCTION_RECEIPT.json';p.write_bytes(b'{"status":"UNTRUSTED"}')
            inv={'construction_output':str(root)};grant={'construction_receipt_path':str(p),'construction_receipt_sha256':'0'*64}
            with patch.object(K,'sha') as scientific_hash,patch.object(D,'exact_rgb') as decode,patch.object(Path,'mkdir') as effect:
                with self.assertRaises(ValueError):N.construction_admission(inv,grant,'1'*64)
                scientific_hash.assert_not_called();decode.assert_not_called();effect.assert_not_called()


if __name__=='__main__':unittest.main()
