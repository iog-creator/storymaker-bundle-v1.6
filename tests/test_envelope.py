from services.common.envelope import envelope_ok,envelope_error
def test_ok(): e=envelope_ok({'k':1},{'actor':'t'}); assert e['status']=='ok' and e['data']['k']==1
