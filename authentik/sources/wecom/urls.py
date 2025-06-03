"""API URLs"""
from django.urls import path

from authentik.sources.wecom.api.property_mappings import WeComSourcePropertyMappingViewSet
from authentik.sources.wecom.api.source import WeComSourceViewSet
from authentik.sources.wecom.api.source_connection import (
    UserWeComSourceConnectionViewSet,
)
from authentik.sources.wecom.views.callback import CallbackView

urlpatterns = [
    path(
        "callback/",
        CallbackView.as_view(),
        name="wecom-client-callback",
    ),
]

api_urlpatterns = [
    ("propertymappings/source/wecom", WeComSourcePropertyMappingViewSet),
    ("sources/user_connections/wecom", UserWeComSourceConnectionViewSet),
    ("sources/wecom", WeComSourceViewSet),
]
