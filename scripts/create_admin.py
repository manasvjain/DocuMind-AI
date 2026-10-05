import argparse,sys
sys.path.insert(0,'backend')
from app.db.session import SessionLocal
from app.services.admin import ensure_admin
p=argparse.ArgumentParser();p.add_argument('--email',required=True);p.add_argument('--password',required=True);p.add_argument('--name',default='System Administrator');a=p.parse_args();db=SessionLocal()
try: print(ensure_admin(db,a.email,a.password,a.name).email)
finally: db.close()
