from rest_framework.viewsets import ModelViewSet

from authentik.core.api.sources import (
    UserSourceConnectionSerializer,
    UserSourceConnectionViewSet,
)
from authentik.sources.wecom.models import UserWeComSourceConnection


class UserWeComSourceConnectionSerializer(UserSourceConnectionSerializer):
    class Meta(UserSourceConnectionSerializer.Meta):
        model = UserWeComSourceConnection
        fields = UserSourceConnectionSerializer.Meta.fields
        extra_kwargs = {
            **UserSourceConnectionSerializer.Meta.extra_kwargs,
        }


class UserWeComSourceConnectionViewSet(UserSourceConnectionViewSet, ModelViewSet):
    queryset = UserWeComSourceConnection.objects.all()
    serializer_class = UserWeComSourceConnectionSerializer
