from datetime import date
from typing import Optional,Tuple

def check_interval(start: Optional[str], end: Optional[str])->Tuple[bool,Optional[str]]:
 if not start or not end: return True,None
 try:
  y1,m1,d1=map(int,start.split('-'))
  y2,m2,d2=map(int,end.split('-'))
  d1=date(y1,m1,d1); d2=date(y2,m2,d2)
 except Exception:
  return False,'INVALID_DATE_FORMAT'
 return (d1<=d2, None if d1<=d2 else 'START_AFTER_END')
