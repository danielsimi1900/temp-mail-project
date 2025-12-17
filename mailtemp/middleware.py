
from django.http import JsonResponse
from .redis_client import get_redis

class SimpleRedisRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.redis = get_redis()
    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR', 'unknown')
        path = request.path
        if path.startswith('/api/generate/') or path.startswith('/api/inbox/'):
            key = f"rl:{ip}:{path}"
            limit = 100
            window = 3600
            count = self.redis.get(key)
            if count is None:
                self.redis.set(key, 1, ex=window)
            else:
                count = int(count) + 1
                self.redis.set(key, count, ex=window)
                if count > limit:
                    return JsonResponse({'detail': 'rate limit exceeded'}, status=429)
        response = self.get_response(request)
        return response
