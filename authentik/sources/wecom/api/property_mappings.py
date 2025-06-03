"""Plex source property mappings API"""

from rest_framework.viewsets import ModelViewSet

from authentik.core.api.property_mappings import PropertyMappingFilterSet, PropertyMappingSerializer
from authentik.core.api.used_by import UsedByMixin
from authentik.sources.wecom.models import WeComSourcePropertyMapping


class WeComSourcePropertyMappingSerializer(PropertyMappingSerializer):
    """WeComSourcePropertyMapping Serializer"""

    class Meta(PropertyMappingSerializer.Meta):
        model = WeComSourcePropertyMapping


class WeComSourcePropertyMappingFilter(PropertyMappingFilterSet):
    """Filter for WeComSourcePropertyMapping"""

    class Meta(PropertyMappingFilterSet.Meta):
        model = WeComSourcePropertyMapping


class WeComSourcePropertyMappingViewSet(UsedByMixin, ModelViewSet):
    """WeComSourcePropertyMapping Viewset"""

    queryset = WeComSourcePropertyMapping.objects.all()
    serializer_class = WeComSourcePropertyMappingSerializer
    filterset_class = WeComSourcePropertyMappingFilter
    search_fields = ["name"]
    ordering = ["name"]
