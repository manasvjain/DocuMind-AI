import json
from app.core.config import get_settings
from app.workers.executor import executor
class JobQueue:
    def __init__(self): self.settings=get_settings()
    def submit(self,job_id,checkpoint=None):
        if self.settings.redis_url:
            try:
                import redis
                redis.from_url(self.settings.redis_url).rpush("svamitrai:jobs",json.dumps({"job_id":job_id,"checkpoint":checkpoint})); return
            except Exception: pass
        executor.submit(job_id,checkpoint)
queue=JobQueue()
