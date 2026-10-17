import pathlib,subprocess,sys,tempfile,json,hashlib,shutil
PYTHON=pathlib.Path(sys.argv[1]).absolute()
SOURCE=pathlib.Path(__file__).absolute().parent
COMMAND=PYTHON.parent/"obj-island-audit"
with tempfile.TemporaryDirectory() as td:
 work=pathlib.Path(td)
 def run(args,code=0):
  p=subprocess.run([str(COMMAND),*map(str,args)],cwd=work,text=True,capture_output=True,timeout=20)
  assert p.returncode==code,(args,p.returncode,p.stdout,p.stderr)
  if code==2:
   assert not p.stdout and p.stderr,(p.stdout,p.stderr)
   return None
  return json.loads(p.stdout)
 help_result=subprocess.run([str(COMMAND),"--help"],cwd=work,capture_output=True,text=True,timeout=10)
 assert help_result.returncode==0 and "usage:" in help_result.stdout
 installed=subprocess.run([str(PYTHON),"-I","-c","import obj_island_audit,pathlib,hashlib;print(hashlib.sha256(pathlib.Path(obj_island_audit.__file__).read_bytes()).hexdigest())"],cwd=work,capture_output=True,text=True,check=True).stdout.strip()
 assert installed==hashlib.sha256((SOURCE/"obj_island_audit.py").read_bytes()).hexdigest()
 for p in SOURCE.glob("example.*"):shutil.copyfile(p,work/p.name)
 r=run(['example.obj']);assert len(r['components'])==2 and all(c['closed_edge_surface'] for c in r['components'])
 assert r['input_faces']==8 and not r['has_findings']
 (work/'open.obj').write_text('v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n')
 assert len(run(['open.obj'],1)['defects']['boundary_edges'])==3
 (work/'bad.obj').write_text('v 0 0 0\nf 1 2 3\n');run(['bad.obj'],2)
 (work/'large.obj').write_bytes(b' '*(2*1024*1024+1));run(['large.obj'],2)
print(json.dumps({"installed_command":"obj-island-audit","outside_checkout":True,"source_identity_matched":True,"contract_checks":"passed"}))
