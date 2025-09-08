def envelope_ok(data=None, meta=None):
 from datetime import datetime,timezone
 return {'status':'ok','data':data or {},'error':None,'meta':{'ts':datetime.now(timezone.utc).isoformat(),**(meta or {})}}

def envelope_error(code,message,details=None,meta=None):
 from datetime import datetime,timezone
 return {'status':'error','data':None,'error':{'code':code,'message':message,'details':details or {}},'meta':{'ts':datetime.now(timezone.utc).isoformat(),**(meta or {})}}
