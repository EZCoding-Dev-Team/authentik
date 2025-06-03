"""WeCom Source Serializer"""
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.fields import CharField
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.viewsets import ModelViewSet
from structlog.stdlib import get_logger

from authentik.core.api.sources import SourceSerializer
from authentik.core.api.used_by import UsedByMixin
from authentik.core.api.utils import PassiveSerializer
from authentik.flows.challenge import RedirectChallenge
from authentik.flows.views.executor import to_stage_response
from authentik.rbac.decorators import permission_required
from authentik.sources.wecom.models import WeComSource, UserWeComSourceConnection
from authentik.sources.wecom.wecom import WeComAuth, WeComSourceFlowManager, CODE_CACHE_KEY

LOGGER = get_logger()


class WeComSourceSerializer(SourceSerializer):
    """WeCom Source Serializer"""

    class Meta:
        model = WeComSource
        fields = SourceSerializer.Meta.fields + [
            "corp_id",
            "agent_id",
            "secret",
        ]


class WeComCodeValidationSerializer(PassiveSerializer):
    """Serializer to validate a WeCom code"""

    state = CharField()


class WeComSourceViewSet(UsedByMixin, ModelViewSet):
    """WeCom source Viewset"""

    queryset = WeComSource.objects.all()
    serializer_class = WeComSourceSerializer
    lookup_field = "slug"
    filterset_fields = [
        "pbm_uuid",
        "name",
        "slug",
        "enabled",
        "authentication_flow",
        "enrollment_flow",
        "policy_engine_mode",
        "user_matching_mode",
        "corp_id",
        "agent_id",
    ]
    search_fields = ["name", "slug"]
    ordering = ["name"]

    @permission_required(None)
    @extend_schema(
        request=WeComCodeValidationSerializer(),
        responses={
            200: RedirectChallenge(),
            400: OpenApiResponse(description="No code found"),
            403: OpenApiResponse(description="Access denied"),
        },
        parameters=[
            OpenApiParameter(
                name="slug",
                location=OpenApiParameter.QUERY,
                type=OpenApiTypes.STR,
            )
        ],
    )
    @action(
        methods=["POST"],
        detail=False,
        pagination_class=None,
        filter_backends=[],
        permission_classes=[AllowAny],
    )
    def validate_code(self, request: Request) -> Response:
        source: WeComSource = get_object_or_404(
            WeComSource, slug=request.query_params.get("slug", "")
        )
        state = request.data.get("state", None)
        if not state:
            raise PermissionDenied("Access denied")
        cache_key = f"{CODE_CACHE_KEY}:{state}"
        code = cache.get(cache_key)
        if not code:
            raise ValidationError("No code found")
        cache.delete(cache_key)
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
        return to_stage_response(request, sfm.get_flow())
