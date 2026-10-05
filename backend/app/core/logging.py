import json,logging,sys
from datetime import datetime,timezone
class JsonFormatter(logging.Formatter):
    def format(self,record):
        payload={"timestamp":datetime.now(timezone.utc).isoformat(),"level":record.levelname,"logger":record.name,"message":record.getMessage()}
        for key in ("job_id","user_id","project_id","image_id","model_id","stage","duration_seconds","status"):
            if hasattr(record,key): payload[key]=getattr(record,key)
        if record.exc_info: payload["exception"]=self.formatException(record.exc_info)
        return json.dumps(payload,ensure_ascii=False)
def configure_logging():
    handler=logging.StreamHandler(sys.stdout); handler.setFormatter(JsonFormatter()); root=logging.getLogger(); root.handlers.clear(); root.addHandler(handler); root.setLevel(logging.INFO)
