import json,os,sys
sys.path.insert(0,'backend')
from app.db.session import SessionLocal
from app.services.pipeline import run_processing_job
def main():
 import redis
 r=redis.from_url(os.environ['REDIS_URL'])
 while True:
  item=r.blpop('svamitrai:jobs',timeout=5)
  if not item:continue
  p=json.loads(item[1]);db=SessionLocal()
  try:run_processing_job(db,p['job_id'],p.get('checkpoint'))
  finally:db.close()
if __name__=='__main__':main()
