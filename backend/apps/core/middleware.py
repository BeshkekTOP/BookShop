from __future__ import annotations
from typing import Callable
from django.http import HttpRequest, HttpResponse
from .models import AuditLog


def audit_middleware(get_response: Callable[[HttpRequest], HttpResponse]) -> Callable[[HttpRequest], HttpResponse]:
    def middleware(request: HttpRequest) -> HttpResponse:
        response = get_response(request)
        try:
            if request.method not in ("GET", "HEAD", "OPTIONS"):
                AuditLog.objects.create(
                    action=f"{request.method} {response.status_code}",
                    actor=getattr(request, 'user', None) if getattr(request, 'user', None) and request.user.is_authenticated else None,
                    path=request.path,
                    method=request.method,
                )
        except Exception:
            # Do not break response flow if audit logging fails
            pass
        return response
    return middleware




