"""Inspect edge-connected OBJ triangle islands and explicit topology defects."""
from __future__ import annotations
import argparse
import json
import math
import re
import sys
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_EVEN, InvalidOperation
from fractions import Fraction
from pathlib import Path

MAX_BYTES=2*1024*1024
NUMBER=re.compile(r'[+-]?(?:[0-9]{1,12}(?:\.[0-9]{0,12})?|\.[0-9]{1,12})(?:[eE][+-]?[0-9]{1,2})?\Z')

def number(s):
    if not NUMBER.fullmatch(s):raise ValueError('unsupported coordinate literal')
    d=Decimal(s)
    if not d.is_finite() or abs(d)>10**9 or (d and abs(d)<Decimal('1e-12')):raise ValueError('nonzero coordinates require magnitude 1e-12..1e9')
    return d

def analyze(text, weld_decimals=None):
    if len(text.encode('utf-8'))>MAX_BYTES:raise ValueError('OBJ exceeds 2 MiB')
    if weld_decimals is not None and (type(weld_decimals) is not int or not 0<=weld_decimals<=9):raise ValueError('weld decimals must be 0..9 or absent')
    vertices=[];faces=[];vt=vn=0;ignored=defaultdict(int)
    def index(raw,count):
        if not re.fullmatch(r'-?[0-9]{1,8}',raw) or int(raw)==0:raise ValueError('invalid OBJ index')
        i=int(raw);i=i-1 if i>0 else count+i
        if not 0<=i<count:raise ValueError('index absent at this face declaration')
        return i
    for line in text.splitlines():
        parts=line.split('#',1)[0].split()
        if not parts:continue
        tag,*args=parts
        if tag=='v':
            if len(args)!=3 or len(vertices)>=20000:raise ValueError('three coordinates required; vertex limit 20000')
            vertices.append(tuple(number(x) for x in args))
        elif tag in ('vt','vn'):
            if not ((1<=len(args)<=3) if tag=='vt' else len(args)==3):raise ValueError('unsupported texture/normal record')
            for x in args:number(x)
            if tag=='vt':vt+=1
            else:vn+=1
            if max(vt,vn)>60000:raise ValueError('attribute record limit')
        elif tag=='f':
            if len(args)!=3 or len(faces)>=30000:raise ValueError('triangles only; face limit 30000')
            f=[]
            for a in args:
                ref=a.split('/')
                if len(ref)>3 or not ref[0]:raise ValueError('invalid face reference')
                f.append(index(ref[0],len(vertices)))
                if len(ref)>=2 and ref[1]:index(ref[1],vt)
                if len(ref)==3 and ref[2]:index(ref[2],vn)
                if len(ref)>1 and not ref[-1]:raise ValueError('empty trailing attribute index')
            faces.append(tuple(f))
        elif tag in ('o','g','s','usemtl','mtllib'):ignored[tag]+=1
        else:raise ValueError('unsupported OBJ directive '+tag)
    if not vertices or not faces:raise ValueError('vertices and triangle faces required')
    point_ids={};points=[];mapping=[]
    for v in vertices:
        key=v if weld_decimals is None else tuple(x.quantize(Decimal(1).scaleb(-weld_decimals),rounding=ROUND_HALF_EVEN) for x in v)
        if key not in point_ids:point_ids[key]=len(points);points.append(key)
        mapping.append(point_ids[key])
    degenerate=[];duplicate=[];seen={};usable={};edges=defaultdict(list);areas={}
    for fid,f in enumerate(faces,1):
        f=tuple(mapping[i] for i in f);pts=[points[i] for i in f]
        u=[Fraction(pts[1][i])-Fraction(pts[0][i]) for i in range(3)];v=[Fraction(pts[2][i])-Fraction(pts[0][i]) for i in range(3)]
        cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
        if len(set(f))!=3 or not any(cross):degenerate.append(fid);continue
        key=tuple(sorted(f))
        if key in seen:duplicate.append({'face':fid,'same_vertices_as':seen[key]});continue
        seen[key]=fid;usable[fid]=f;areas[fid]=math.sqrt(sum(float(c*c) for c in cross))/2
        for a,b in zip(f,f[1:]+f[:1]):edges[tuple(sorted((a,b)))].append((fid,1 if a<b else -1))
    parent={f:f for f in usable}
    def find(x):
        while x!=parent[x]:parent[x]=parent[parent[x]];x=parent[x]
        return x
    for incidence in edges.values():
        for f,_ in incidence[1:]:
            a,b=find(incidence[0][0]),find(f)
            if a!=b:parent[max(a,b)]=min(a,b)
    groups=defaultdict(list)
    for f in usable:groups[find(f)].append(f)
    grouped_edges=defaultdict(list)
    for edge,incidence in edges.items():grouped_edges[find(incidence[0][0])].append((edge,incidence))
    components=[];face_component={}
    for cid,(root,ids) in enumerate(sorted(groups.items()),1):
        for f in ids:face_component[f]=cid
        local=grouped_edges[root]
        verts=sorted({v for f in ids for v in usable[f]})
        components.append({'component':cid,'faces':sorted(ids),'vertices':verts,'area_approx':math.fsum(areas[f] for f in ids),
            'boundary_edges':sum(len(inc)==1 for _,inc in local),'nonmanifold_edges':sum(len(inc)>2 for _,inc in local),
            'orientation_conflicts':sum(len(inc)==2 and inc[0][1]==inc[1][1] for _,inc in local),
            'closed_edge_surface':all(len(inc)==2 for _,inc in local),
            'bounds':[[float(min(points[v][i] for v in verts)) for i in range(3)],[float(max(points[v][i] for v in verts)) for i in range(3)]]})
    contacts=defaultdict(set)
    for f,verts in usable.items():
        for v in verts:contacts[v].add(face_component[f])
    vertex_contacts=[{'vertex':v,'components':sorted(c)} for v,c in sorted(contacts.items()) if len(c)>1]
    defects={'degenerate_faces':degenerate,'duplicate_faces':duplicate,'vertex_contacts':vertex_contacts,
             'boundary_edges':[list(e) for e,inc in sorted(edges.items()) if len(inc)==1],
             'nonmanifold_edges':[{'edge':list(e),'faces':[f for f,_ in inc]} for e,inc in sorted(edges.items()) if len(inc)>2],
             'orientation_conflicts':[list(e) for e,inc in sorted(edges.items()) if len(inc)==2 and inc[0][1]==inc[1][1]]}
    return {'input_vertices':len(vertices),'input_faces':len(faces),'weld_decimals':weld_decimals,'welded_vertices':len(points),
        'vertex_mapping':mapping,'components':components,'defects':defects,'has_findings':any(defects.values()),'ignored_metadata':dict(sorted(ignored.items())),
        'scope':'Edge-connected triangle islands after exact-coordinate welding, or explicit decimal-grid quantization (half-even). No mesh repair, self-intersection test, solid-volume or printability guarantee. Attribute references are validated but attributes/material files are not loaded.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input');p.add_argument('--weld-decimals',type=int);a=p.parse_args()
    try:
        with Path(a.input).open('rb') as f:raw=f.read(MAX_BYTES+1)
        if len(raw)>MAX_BYTES:raise ValueError('OBJ exceeds 2 MiB')
        r=analyze(raw.decode('utf-8-sig'),a.weld_decimals);print(json.dumps(r,sort_keys=True,indent=2));return int(r['has_findings'])
    except (ValueError,OSError,UnicodeError,InvalidOperation,OverflowError) as e:
        print(json.dumps({'error':str(e)}),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
