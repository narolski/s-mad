"""NEXT technical metadata only. Production CLI requires exact root release.

No scientific imports. Unknown JSON values are lexically skipped, not decoded.
Only constant-key booleans/counts/status codes and opaque hashes cross output.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat
import tarfile
import native_metadata_predicates_v2 as predicates

MAX_MEMBER = 8 * 1024 * 1024
MAX_TOTAL = 256 * 1024 * 1024
MAX_HEADERS = 100000


class Refused(Exception):
    pass


def require(condition, code):
    if not condition:
        raise Refused(code)


def digest(data):
    return hashlib.sha256(data).hexdigest()


class SelectiveJSON:
    """Decode only schema-selected leaves; skip other scalars without conversion.

    Duplicate keys, including inside ignored objects, fail. No input fragments
    are included in exceptions. Container depth/token/string sizes are bounded
    by member byte limit and depth64. Lists only decode a schema's '*' subtree.
    """
    token = re.compile(r'-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?|true|false|null')

    def __init__(self, data):
        try:
            self.s = data.decode('utf-8')
        except UnicodeError:
            raise Refused('ENCODING') from None
        self.i = 0

    def ws(self):
        while self.i < len(self.s) and self.s[self.i] in ' \r\n\t':
            self.i += 1

    def string(self, decode):
        start = self.i
        require(self.s[self.i:self.i+1] == '"', 'JSON_SYNTAX')
        self.i += 1
        while self.i < len(self.s):
            c = self.s[self.i]
            self.i += 1
            if c == '"':
                if not decode:
                    return None
                try:
                    return json.loads(self.s[start:self.i])
                except (ValueError, UnicodeError):
                    raise Refused('JSON_SYNTAX') from None
            require(ord(c) >= 32, 'JSON_SYNTAX')
            if c == '\\':
                require(self.i < len(self.s), 'JSON_SYNTAX')
                esc = self.s[self.i]; self.i += 1
                require(esc in '"\\/bfnrtu', 'JSON_SYNTAX')
                if esc == 'u':
                    require(re.fullmatch('[0-9a-fA-F]{4}', self.s[self.i:self.i+4]) is not None, 'JSON_SYNTAX')
                    self.i += 4
        raise Refused('JSON_SYNTAX')

    def value(self, schema, depth=0):
        require(depth <= 64, 'JSON_DEPTH')
        self.ws(); c = self.s[self.i:self.i+1]
        if c == '{':
            self.i += 1; seen = set(); result = {}; self.ws()
            if self.s[self.i:self.i+1] == '}':
                self.i += 1; return result if schema is not None else None
            while True:
                self.ws(); key = self.string(True)
                require(key not in seen, 'JSON_DUPLICATE'); seen.add(key)
                self.ws(); require(self.s[self.i:self.i+1] == ':', 'JSON_SYNTAX'); self.i += 1
                sub = schema.get(key) if isinstance(schema, dict) else None
                v = self.value(sub, depth+1)
                if sub is not None: result[key] = v
                self.ws(); end = self.s[self.i:self.i+1]; self.i += 1
                if end == '}': break
                require(end == ',', 'JSON_SYNTAX')
            return result if schema is not None else None
        if c == '[':
            self.i += 1; out = []; self.ws()
            sub = schema.get('*') if isinstance(schema, dict) else None
            if self.s[self.i:self.i+1] == ']':
                self.i += 1; return out if schema is not None else None
            while True:
                v = self.value(sub, depth+1)
                if sub is not None: out.append(v)
                self.ws(); end = self.s[self.i:self.i+1]; self.i += 1
                if end == ']': break
                require(end == ',', 'JSON_SYNTAX')
            return out if schema is not None else None
        if c == '"': return self.string(schema is not None)
        match = self.token.match(self.s, self.i)
        require(match is not None, 'JSON_SYNTAX')
        self.i = match.end()
        if schema is None: return None
        try:
            return json.loads(match.group())
        except ValueError:
            raise Refused('JSON_SYNTAX') from None

    def parse(self, schema):
        result = self.value(schema); self.ws()
        require(self.i == len(self.s), 'JSON_SYNTAX')
        return result


def json_checks(value, schema):
    """Return structure containing schema keys and booleans, never raw values."""
    if isinstance(schema, dict) and '*' in schema:
        if not isinstance(value, list): return {'type_ok': False}
        return {'type_ok': True, 'count': len(value), 'items': [json_checks(v, schema['*']) for v in value]}
    if isinstance(schema, dict) and 'type' not in schema:
        if not isinstance(value, dict): return {'type_ok': False}
        return {k: json_checks(value.get(k), spec) for k, spec in schema.items()}
    typ = schema['type']
    ok = {'int': type(value) is int, 'bool': type(value) is bool,
          'str': type(value) is str, 'number': type(value) in (int, float)}[typ]
    if ok and typ == 'number': ok = math.isfinite(value)
    result = {'type_ok': ok}
    if 'equals' in schema: result['equals_expected'] = ok and value == schema['equals']
    if 'one_of' in schema: result['in_registered_set'] = ok and value in schema['one_of']
    if schema.get('emit_registered'):
        result['registered_identity'] = value if ok and value in schema['one_of'] else None
    if schema.get('nonnegative'): result['nonnegative'] = ok and value >= 0
    if schema.get('sha256'): result['sha256_shape'] = ok and re.fullmatch('[0-9a-f]{64}', value) is not None
    if schema.get('emit_hex'):result['technical_sha256']=value if ok and re.fullmatch('[0-9a-f]{64}',value) else None
    if schema.get('emit_version'):result['technical_version']=value if ok and re.fullmatch(r'[0-9]{1,3}(?:\.[0-9]{1,3}){1,3}(?:\+[a-zA-Z0-9.]{1,24})?',value) else None
    if schema.get('emit_gpu'):result['technical_gpu']='H100' if ok and 'H100' in value else None
    return result


def inspect_member(raw, spec):
    kind = spec['kind']
    if kind == 'opaque': return {'status': 'HASH_ONLY', 'expected_digest_matches': digest(raw)==spec['expected_sha256']}
    if kind == 'json':
        return {'checks': json_checks(SelectiveJSON(raw).parse(spec['schema']), spec['schema'])}
    try: text = raw.decode('utf-8')
    except UnicodeError: raise Refused('ENCODING') from None
    if kind == 'loss':
        return predicates.loss_predicate(text)
    if kind == 'guard':
        return {'pre_marker': 'RZ1 GUARD pre ok' in text, 'post_marker': 'RZ1 GUARD post ok' in text}
    if kind == 'gpu': return {'h100_identity_present': 'H100' in text}
    if kind == 'env':
        lines = text.splitlines()
        return {'checks': {k: sum(x.startswith(k+'=') for x in lines) == 1 and lines.count(k+'='+str(v)) == 1 for k,v in spec['expected'].items()}}
    if kind == 'tokens':
        tokens = text.split(); checks = {}
        for k, expected in spec['expected'].items():
            indices = [i for i,t in enumerate(tokens) if t == k]
            checks[k] = len(indices) == 1 and tokens[indices[0]+1:indices[0]+1+len(expected)] == expected
        return {'checks': checks}
    if kind == 'tasks':
        lines = text.splitlines()
        return {'registered_tasks_exact': len(lines)==len(set(lines)) and set(lines)==set(spec['expected']), 'count': len(lines)}
    if kind == 'scripts':
        found = {}; valid = True
        for line in text.splitlines():
            fields = line.split()
            if len(fields)!=2: valid=False; continue
            h,p = fields; name=PurePosixPath(p).name
            if name in found: valid=False
            found[name]=h
        return {'pinned_scripts_exact': valid and found==spec['expected']}
    if kind == 'count':
        try:
            n=int(text)
            return {'conversion_ok':True,'nonnegative':n>=0,'count':n if n>=0 else None}
        except (ValueError,OverflowError):return {'conversion_ok':False,'reason':'INT_CONVERSION_ERROR'}
    if kind == 'technical_env':
        tokens=text.split();out={}
        for key in ('torch','cuda','tf32'):
            ix=[i for i,t in enumerate(tokens) if t==key]
            value=tokens[ix[0]+1] if len(ix)==1 and ix[0]+1<len(tokens) else None
            if key=='tf32':out[key]=True if value=='True' else False if value=='False' else None
            else:out[key]=value if value and re.fullmatch(r'[0-9]{1,3}(?:\.[0-9]{1,3}){1,3}(?:\+[a-zA-Z0-9.]{1,24})?',value) else None
        return {'typed_technical_fields':out,'scoring_process_TF32':'UNKNOWN_FRESH_ENV_PROCESS_IS_NOT_SCORER'}
    raise Refused('UNKNOWN_PARSER')


def normalize(name):
    p = PurePosixPath(name)
    require(not p.is_absolute() and '..' not in p.parts, 'TAR_PATH')
    return str(p)


def collect_archive(record):
    """Public only for synthetic tests; production CLI calls after release gate."""
    result = {'status':'HOLD', 'members':{}}
    evidence={}
    try:
        path=Path(record['archive'])
        require(path.is_absolute() and path.resolve()==path, 'ARCHIVE_PATH')
        fd=os.open(path,os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd,'rb') as stream:
            require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), 'ARCHIVE_TYPE')
            require(hashlib.file_digest(stream,'sha256').hexdigest()==record['sha256'], 'ARCHIVE_HASH')
            stream.seek(0); seen=set(); total=0; count=0
            with tarfile.open(fileobj=stream,mode='r:') as tf:
                for member in tf:
                    count+=1; require(count<=MAX_HEADERS,'TAR_HEADERS')
                    name=normalize(member.name)
                    require(name not in seen,'TAR_DUPLICATE'); seen.add(name)
                    require((member.isfile() or member.isdir()) and not member.issparse(),'TAR_TYPE')
                    if name not in record['members']: continue
                    if record['members'][name]['kind']=='header':
                        result['members'][name]={'status':'HEADER_ONLY','regular_file':member.isfile(),'nonempty':member.size>0}
                        continue
                    require(member.isfile() and 0<=member.size<=MAX_MEMBER,'MEMBER_SIZE')
                    total+=member.size; require(total<=MAX_TOTAL,'PARSE_BUDGET')
                    with tf.extractfile(member) as f: raw=f.read(MAX_MEMBER+1)
                    require(len(raw)==member.size,'MEMBER_TRUNCATED')
                    try:
                        spec=record['members'][name]
                        item=inspect_member(raw,spec)
                        evidence[name]=SelectiveJSON(raw).parse(spec['schema']) if spec['kind']=='json' else raw if spec['kind']=='opaque' else raw.decode('utf-8')
                        if name=='config.json':evidence['_config_digest']=digest(raw)
                    except Refused as exc: item={'status':'HOLD','reason':str(exc)}
                    except Exception: item={'status':'HOLD','reason':'PARSER_ERROR'}
                    item['opaque_sha256']=digest(raw); result['members'][name]=item
            for name in record['members']:
                result['members'].setdefault(name,{'status':'HOLD','reason':'MEMBER_MISSING'})
            result['status']='COLLECTED_TECHNICAL_ONLY'
    except Refused as exc: result['reason']=str(exc)
    except Exception: result['reason']='ARCHIVE_ERROR'
    try:result['native_predicate_matrix']=predicates.evaluate(record,evidence)
    except Exception:result['native_predicate_matrix']=[{'native_status':'UNKNOWN','strict_integrity_status':'UNKNOWN','reason':'PREDICATE_EVALUATION_ERROR'}]
    result['native_eligibility']='PENDING_REGISTERED_PAYLOAD_AND_OTHER_GATES'
    if record.get('kernel_support_metadata'):
        result['kernel_support_descriptors']={'archive':record['archive'],'archive_sha256':record['sha256'],**record['kernel_support_metadata']}
    return result


def main():
    p=argparse.ArgumentParser(description='Metadata-only collector; exact root release required')
    p.add_argument('--packet',required=True);p.add_argument('--release',required=True);p.add_argument('--output',required=True)
    args=p.parse_args()
    try:
        packet_bytes=Path(args.packet).read_bytes(); packet=json.loads(packet_bytes)
        release=json.loads(Path(args.release).read_bytes()); out=Path(args.output)
        require(release.get('decision')=='GO_NEXT_TECHNICAL_METADATA_V2R1_ONLY','RELEASE_REQUIRED')
        require(release.get('packet_sha256')==digest(packet_bytes),'RELEASE_PACKET')
        require(release.get('collector_sha256')==digest(Path(__file__).read_bytes()),'RELEASE_SOURCE')
        require(release.get('predicates_sha256')==digest(Path(predicates.__file__).read_bytes()),'RELEASE_PREDICATES')
        require(release.get('whole_log_original_regex_boolean_only') is True,'LOSS_SCOPE_RELEASE')
        require(release.get('output')==str(out) and out.is_absolute() and out.resolve()==out,'RELEASE_OUTPUT')
        require(release.get('cpu_only') is True and not os.environ.get('CUDA_VISIBLE_DEVICES'),'RESOURCE_GATE')
        review=Path(release['implementation_review'])
        require(digest(review.read_bytes())==release['implementation_review_sha256'],'REVIEW_HASH')
        require('GO_NEXT_TECHNICAL_V2R1_IMPLEMENTATION '+digest(Path(__file__).read_bytes()) in review.read_text().splitlines(),'REVIEW_DECISION')
        require(packet['schema']=='next-typed-technical-scope-v2r1' and len(packet['archives'])==77,'ROSTER_SCHEMA')
        for path,h in packet['pins'].items(): require(digest(Path(path).read_bytes())==h,'SOURCE_PIN')
        require(not out.exists(),'OUTPUT_EXISTS'); out.mkdir(parents=False)
        results={k:collect_archive(v) for k,v in packet['archives'].items()}
        payload={'schema':'next-technical-metadata-only-v2r1','scientific_admission':False,'planned_seed_denominator':5,'packet_sha256':digest(packet_bytes),'release_sha256':digest(Path(args.release).read_bytes()),'collector_sha256':digest(Path(__file__).read_bytes()),'predicates_sha256':digest(Path(predicates.__file__).read_bytes()),'archives':results}
        def durable(name,content):
            temp=out/(name+'.partial')
            with temp.open('x') as f:f.write(content);f.flush();os.fsync(f.fileno())
            os.rename(temp,out/name)
        durable('TECHNICAL_METADATA.json',json.dumps(payload,indent=2,allow_nan=False)+'\n')
        durable('SHA256SUMS',digest((out/'TECHNICAL_METADATA.json').read_bytes())+'  TECHNICAL_METADATA.json\n')
        durable('TECHNICAL_WRITE_COMPLETE','NOT_SCIENTIFIC_ADMISSION\n')
        fd=os.open(out,os.O_RDONLY);os.fsync(fd);os.close(fd)
        print('TECHNICAL_COLLECTION_WRITTEN_NOT_ADMISSION')
        return 0
    except Refused as exc: print('HOLD '+str(exc)); return 2
    except Exception: print('HOLD CONTROL_PLANE_ERROR'); return 2


if __name__=='__main__': raise SystemExit(main())
