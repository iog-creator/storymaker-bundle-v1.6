from services.guards.allen_lite import Interval,relation,path_consistent

def test_rel():
 a=Interval(1,2); b=Interval(3,4); assert relation(a,b) in ('before','meets')

def test_chain():
 a=Interval(1,2); b=Interval(2,3); c=Interval(3,4); assert path_consistent(a,b,c)
