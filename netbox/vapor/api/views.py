
from rest_framework.response import Response

from extras.api.views import CustomFieldModelViewSet
from tenancy.models import Tenant
from vapor import filters

from . import serializers


class CustomerViewSet(CustomFieldModelViewSet):
    queryset = Tenant.objects.prefetch_related(
        'group', 'tags', 'devices'
    )
    serializer_class = serializers.CustomerSerializer
    filterset_class = filters.CustomerFilter
