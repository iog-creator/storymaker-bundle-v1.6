
import sys, json, os
from services.worldcore.dal import WorldCoreDAL
def main():
    dsn = os.environ.get("POSTGRES_DSN")
    if not dsn: raise SystemExit("POSTGRES_DSN is required")
    dal = WorldCoreDAL(dsn)
    for path in sys.argv[1:]:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            cid = f"b3:{abs(hash(data.get('id',path)))% (10**8):08d}...{abs(hash(data.get('name','')))% (10**6):06d}"
            dal.propose(data, cid); dal.approve(cid)
            print(f"Seeded {data.get('id', path)}")
if __name__ == "__main__": main()
