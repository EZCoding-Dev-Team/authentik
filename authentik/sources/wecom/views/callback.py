from django.http import HttpRequest, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404

from ..models import WeComSource
from ..wecom import WeComAuth, WeComSourceFlowManager


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
        source: WeComSource = get_object_or_404(
            WeComSource, slug=request.GET.get("slug", "")
        )
        auth_api = WeComAuth(source, code)
        user_info, identifier = auth_api.get_user_info()
        sfm = WeComSourceFlowManager(
            source=source,
            request=request,
            identifier=str(identifier),
            user_info={
                "info": user_info,
                "auth_api": auth_api,
            },
            policy_context={},
        )
        return sfm.get_flow()
