import json,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=json.load(open('_verify_paid.json',encoding='utf-8'))
print(json.dumps(d.get('ol'),ensure_ascii=False)[:3500])