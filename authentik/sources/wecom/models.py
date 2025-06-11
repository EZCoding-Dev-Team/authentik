"""Plex source"""

from typing import Any

from django.db import models
from django.http.request import HttpRequest
from django.templatetags.static import static
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from rest_framework.fields import CharField
from rest_framework.serializers import Serializer

from authentik.core.models import (
    PropertyMapping,
    Source,
    UserSourceConnection,
)
from authentik.core.types import UILoginButton, UserSettingSerializer
from authentik.flows.challenge import Challenge, ChallengeResponse
from authentik.stages.identification.stage import LoginChallengeMixin


class WeComLoginChallenge(LoginChallengeMixin, Challenge):
    """Challenge for WeCom shown to the user in identification stage"""

    corp_id = CharField()
    agent_id = CharField()
    component = CharField(default="ak-source-wecom")
    slug = CharField()
    state = CharField()
    callback_uri = CharField()
    mobile_uri = CharField()


class WeComChallengeResponse(ChallengeResponse):
    """Pseudo class for WeCom response"""

    component = CharField(default="ak-source-wecom")


class WeComSource(Source):
    """Login using a WeCom provider."""

    corp_id = models.TextField(
        help_text=_("Corp identifier used to talk to WeCom."),
    )
    agent_id = models.TextField(
        help_text=_("Agent identifier used to talk to WeCom."),
    )
    secret = models.TextField(
        help_text=_("Secret used to talk to WeCom."),
    )

    @property
    def component(self) -> str:
        return "ak-source-wecom-form"

    @property
    def serializer(self) -> type[Serializer]:
        from authentik.sources.wecom.api.source import WeComSourceSerializer

        return WeComSourceSerializer

    @property
    def property_mapping_type(self) -> type[PropertyMapping]:
        return WeComSourcePropertyMapping

    def get_base_user_properties(self, info: dict[str, Any], **kwargs):
        return {
            "username": info.get("userid"),
            "email": info.get("biz_email"),
            "name": info.get("name"),
        }

    @property
    def icon_url(self) -> str:
        icon = super().icon_url
        if not icon:
            icon = static("authentik/sources/wecom.svg")
        return icon

    def ui_login_button(self, request: HttpRequest) -> UILoginButton:
        state = get_random_string(32)
        callback = request.build_absolute_uri(reverse("authentik_sources_wecom:wecom-client-callback"))
        mobile = request.build_absolute_uri(reverse("authentik_sources_wecom:wecom-client-mobile"))
        return UILoginButton(
            name=self.name,
            challenge=WeComLoginChallenge(
                data={
                    "component": "ak-source-wecom",
                    "corp_id": self.corp_id,
                    "agent_id": self.agent_id,
                    "slug": self.slug,
                    "state": state,
                    "callback_uri": callback,
                    "mobile_uri": mobile,
                }
            ),
            icon_url=self.icon_url,
        )

    def ui_user_settings(self) -> UserSettingSerializer | None:
        return UserSettingSerializer(
            data={
                "title": self.name,
                "component": "ak-user-settings-source-wecom",
                "configure_url": self.corp_id,
                "icon_url": self.icon_url,
            }
        )

    class Meta:
        verbose_name = _("WeCom Source")
        verbose_name_plural = _("WeCom Sources")


class WeComSourcePropertyMapping(PropertyMapping):
    """Map WeCom properties to User of Group object attributes"""

    @property
    def component(self) -> str:
        return "ak-property-mapping-source-wecom-form"

    @property
    def serializer(self) -> type[Serializer]:
        from authentik.sources.wecom.api.property_mappings import WeComSourcePropertyMappingSerializer

        return WeComSourcePropertyMappingSerializer

    class Meta:
        verbose_name = _("WeCom Source Property Mapping")
        verbose_name_plural = _("WeCom Source Property Mappings")


class UserWeComSourceConnection(UserSourceConnection):
    """Connect user and WeCom source"""

    @property
    def serializer(self) -> type[Serializer]:
        from authentik.sources.wecom.api.source_connection import UserWeComSourceConnectionSerializer

        return UserWeComSourceConnectionSerializer

    class Meta:
        verbose_name = _("User WeCom Source Connection")
        verbose_name_plural = _("User WeCom Source Connections")
