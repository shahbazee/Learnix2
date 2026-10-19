import logging
import time

logger = logging.getLogger(__name__)


class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_respons = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_respons(request)
        duration = time.time() - start
        logger.info(f"{request.method} {request.path} -> {response.status_code} in {duration:.2f}s")
        return response