import brotli
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse


class BrotliMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        accept_encoding = request.headers.get("Accept-Encoding", "")
        if "br" in accept_encoding and isinstance(response, HttpResponse):
            if not response.streaming and "Content-Encoding" not in response:
                response.content = brotli.compress(response.content)
                response["Content-Encoding"] = "br"
        return response
