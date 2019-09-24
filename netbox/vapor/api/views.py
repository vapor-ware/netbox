
from rest_framework.response import Response
from rest_framework.decorators import action

from dcim.api.views import CableTraceMixin
from dcim.models import Interface
from extras.api.views import CustomFieldModelViewSet
from tenancy.models import Tenant as Customer
from utilities.api import ModelViewSet
from vapor import filters

from . import serializers


class CustomerViewSet(CustomFieldModelViewSet):
    queryset = Customer.objects.prefetch_related(
        'group', 'tags', 'devices'
    )
    serializer_class = serializers.CustomerSerializer
    filterset_class = filters.CustomerFilter


class InterfaceViewSet(CableTraceMixin, ModelViewSet):
    queryset = Interface.objects.prefetch_related(
        'device', '_connected_interface', '_connected_circuittermination', 'cable', 'ip_addresses', 'tags'
    ).filter(
        device__isnull=False
    )
    serializer_class = serializers.InterfaceSerializer
    filterset_class = filters.InterfaceFilter

    @action(detail=True)
    def graphs(self, request, pk=None):
        """
        A convenience method for rendering graphs for a particular interface.
        """
        interface = get_object_or_404(Interface, pk=pk)
        queryset = Graph.objects.filter(type=GRAPH_TYPE_INTERFACE)
        serializer = RenderedGraphSerializer(queryset, many=True, context={'graphed_object': interface})
        return Response(serializer.data)
