from services.narrative.ledger import compute_promise_payoff,trope_budget_ok

def test_pp():
 l=compute_promise_payoff([{'promises_made':['fog origin']},{'promises_paid':['minor']}])
 assert 'fog origin' in l['orphans'] and 'minor' in l['extraneous']

def test_trope():
 ok,_=trope_budget_ok('chosen one ' * 10, ['chosen one'], max_per_1k=1)
 assert not ok
