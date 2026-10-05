from collections import defaultdict,deque
from threading import Lock
from time import monotonic
from fastapi import HTTPException,Request
class SimpleRateLimiter:
    def __init__(self,limit=120,window_seconds=60): self.limit=limit; self.window=window_seconds; self.events=defaultdict(deque); self.lock=Lock()
    async def __call__(self,request,call_next):
        key=request.client.host if request.client else "unknown"; now=monotonic()
        with self.lock:
            queue=self.events[key]
            while queue and now-queue[0]>self.window: queue.popleft()
            if len(queue)>=self.limit: raise HTTPException(status_code=429,detail="Rate limit exceeded")
            queue.append(now)
        return await call_next(request)
rate_limiter=SimpleRateLimiter()
