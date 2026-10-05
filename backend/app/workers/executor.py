from concurrent.futures import ThreadPoolExecutor
from app.db.session import SessionLocal
from app.services.pipeline import run_processing_job
class LocalJobExecutor:
    def __init__(self,max_workers:int=2): self.executor=ThreadPoolExecutor(max_workers=max_workers,thread_name_prefix="svamitrai-job")
    def submit(self,job_id,checkpoint=None): self.executor.submit(self._run,job_id,checkpoint)
    @staticmethod
    def _run(job_id,checkpoint):
        db=SessionLocal()
        try: run_processing_job(db,job_id,checkpoint)
        finally: db.close()
executor=LocalJobExecutor()
