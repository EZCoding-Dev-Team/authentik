"""authentik wecom config"""

from django.apps import AppConfig


class AuthentikSourceWeComConfig(AppConfig):
    """authentik source wecom config"""

    name = "authentik.sources.wecom"
    label = "authentik_sources_wecom"
    verbose_name = "authentik Sources.WeCom"
    mountpoint = "source/wecom/"
