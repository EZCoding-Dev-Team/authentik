from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext as _
from django.shortcuts import render

from authentik.sources.wecom.wecom import CODE_CACHE_KEY


@method_decorator(csrf_exempt, name="dispatch")
class CallbackView(View):
    kind = ""

    def dispatch(self, request: HttpRequest, *_, **kwargs) -> HttpResponse:
        code = request.GET.get("code")
        state = request.GET.get("state")
        if code is None or state is None:
            return render(
                request,
                "auth_result.html",
                {"success": False}
            )
        cache_key = f"{CODE_CACHE_KEY}:{state}"
        cache.set(cache_key, code, timeout=10)
        return render(
            request,
            "auth_result.html",
            {"success": True}
        )
