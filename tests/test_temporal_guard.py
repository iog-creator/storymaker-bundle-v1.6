from services.guards.temporal import check_interval

def test_ok(): ok,msg=check_interval('1203-05-21','1203-05-21'); assert ok

def test_fail(): ok,msg=check_interval('1203-05-22','1203-05-21'); assert not ok and msg=='START_AFTER_END'
