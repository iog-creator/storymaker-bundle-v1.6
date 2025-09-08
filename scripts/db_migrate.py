import os,sys,psycopg

dsn=os.environ.get('POSTGRES_DSN')
if not dsn: raise SystemExit('POSTGRES_DSN is required')
path=sys.argv[1] if len(sys.argv)>1 else 'sql/001_init.sql'
sql=open(path,'r',encoding='utf-8').read()
with psycopg.connect(dsn) as c:
  with c.cursor() as cur:
    cur.execute(sql)
  c.commit()
print('Migration applied')
