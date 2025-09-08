from dataclasses import dataclass
@dataclass
class Interval: start:int; end:int

def relation(a:Interval,b:Interval)->str:
 if a.end<b.start: return 'before'
 if a.start==b.start and a.end==b.end: return 'equal'
 if a.start<b.start<a.end<b.end: return 'overlaps'
 if b.start<=a.start and a.end<=b.end: return 'during'
 if a.end==b.start: return 'meets'
 if a.start>b.end: return 'after'
 return 'unknown'

def path_consistent(a:Interval,b:Interval,c:Interval)->bool:
 rab=relation(a,b); rbc=relation(b,c); rac=relation(a,c)
 if rab in ('before','meets') and rbc in ('before','meets'): return rac in ('before','meets')
 if rab=='during' and rbc=='during': return rac=='during'
 return True
