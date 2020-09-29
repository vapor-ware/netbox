from rest_framework import serializers
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField
from drf_yasg.utils import swagger_serializer_method
from dcim.constants import CONNECTION_STATUS_CHOICES

from extras.api.customfields import CustomFieldModelSerializer
from dcim.api.nested_serializers import (
    NestedDeviceSerializer,
    NestedInterfaceSerializer,
    NestedCableSerializer,
)
from dcim.api.serializers import InterfaceConnectionSerializer
from dcim.choices import InterfaceTypeChoices, InterfaceModeChoices
from dcim.models import Interface
from ipam.api.nested_serializers import NestedPrefixSerializer
from ipam.models import VLAN, Prefix
from tenancy.api.nested_serializers import NestedTenantGroupSerializer
from utilities.api import ChoiceField, ValidatedModelSerializer, SerializedPKRelatedField, WritableNestedSerializer
from tenancy.models import Tenant as Customer
from utilities.utils import dynamic_import

from netbox_virtual_circuit_plugin.models import VirtualCircuitVLAN, VirtualCircuit


def get_serializer_for_model(model, prefix=''):
    """
    Dynamically resolve and return the appropriate serializer for a model.
    """
    app_name, model_name = model._meta.label.split('.')
    serializer_name = '{}.api.serializers.{}{}Serializer'.format(
        app_name, prefix, model_name
    )

    override_serializer_name = 'vapor.api.serializers.{}VLAN{}Serializer'.format(
        prefix, model_name
    )
    try:
        return dynamic_import(override_serializer_name)
    except AttributeError:
        pass

    try:
        return dynamic_import(serializer_name)
    except AttributeError:
        raise SerializerNotFound(
            "Could not determine serializer for {}.{} with prefix '{}'".format(app_name, model_name, prefix)
        )


class NestedVirtualCircuitSerializer(ValidatedModelSerializer):
    vcid = serializers.ReadOnlyField(source='virtual_circuit.vcid')
    name = serializers.ReadOnlyField(source='virtual_circuit.name')
    status = serializers.ReadOnlyField(source='virtual_circuit.status')
    context = serializers.ReadOnlyField(source='virtual_circuit.context')

    class Meta:
        model = VirtualCircuit
        fields = ['vcid', 'name', 'status', 'context']


class NestedVaporVLANSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:vlan-detail')

    prefixes = SerializedPKRelatedField(
        queryset=Prefix.objects.all(),
        serializer=NestedPrefixSerializer,
        required=False,
        many=True,
    )

    virtual_circuit = SerializedPKRelatedField(
        source='vlan_of',
        queryset=VirtualCircuitVLAN.objects.all(),
        serializer=NestedVirtualCircuitSerializer,
        pk_field='vlan',
        required=False,
        many=False,
    )

    class Meta:
        model = VLAN
        fields = ['id', 'url', 'vid', 'name', 'display_name', 'prefixes', 'status', 'virtual_circuit']


class NestedVLANInterfaceSerializer(WritableNestedSerializer):
    device = NestedDeviceSerializer(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:interface-detail')
    connection_status = ChoiceField(choices=CONNECTION_STATUS_CHOICES, read_only=True)
    type = ChoiceField(choices=InterfaceTypeChoices, required=False)

    untagged_vlan = NestedVaporVLANSerializer(required=False, allow_null=True)
    tagged_vlans = SerializedPKRelatedField(
        queryset=VLAN.objects.all(),
        serializer=NestedVaporVLANSerializer,
        required=False,
        many=True,
    )

    class Meta:
        model = Interface
        fields = ['id', 'url', 'device', 'name', 'cable', 'connection_status', 'type', 'untagged_vlan', 'tagged_vlans']


class ConnectedEndpointSerializer(ValidatedModelSerializer):
    connected_endpoint_type = serializers.SerializerMethodField(read_only=True)
    connected_endpoint = serializers.SerializerMethodField(read_only=True)
    connection_status = ChoiceField(choices=CONNECTION_STATUS_CHOICES, read_only=True)

    def get_connected_endpoint_type(self, obj):
        if hasattr(obj, 'connected_endpoint') and obj.connected_endpoint is not None:
            return '{}.{}'.format(
                obj.connected_endpoint._meta.app_label,
                obj.connected_endpoint._meta.model_name
            )
        return None

    @swagger_serializer_method(serializer_or_field=serializers.DictField)
    def get_connected_endpoint(self, obj):
        """
        Return the appropriate serializer for the type of connected object.
        """
        if getattr(obj, 'connected_endpoint', None) is None:
            return None

        serializer = get_serializer_for_model(obj.connected_endpoint, prefix='Nested')
        context = {'request': self.context['request']}
        data = serializer(obj.connected_endpoint, context=context).data

        return data


class CustomerSerializer(TaggitSerializer, CustomFieldModelSerializer):
    group = NestedTenantGroupSerializer(required=False)
    tags = TagListSerializerField(required=False)
    devices = NestedDeviceSerializer(required=False, many=True)

    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'slug', 'group', 'description', 'comments', 'tags', 'custom_fields', 'created',
            'last_updated', 'devices',
        ]


class InterfaceSerializer(TaggitSerializer, ConnectedEndpointSerializer):
    device = NestedDeviceSerializer()
    type = ChoiceField(choices=InterfaceTypeChoices, required=False)
    lag = NestedInterfaceSerializer(required=False, allow_null=True)
    mode = ChoiceField(choices=InterfaceModeChoices, required=False, allow_null=True)
    untagged_vlan = NestedVaporVLANSerializer(required=False, allow_null=True)
    tagged_vlans = SerializedPKRelatedField(
        queryset=VLAN.objects.all(),
        serializer=NestedVaporVLANSerializer,
        required=False,
        many=True
    )
    cable = NestedCableSerializer(read_only=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Interface
        fields = [
            'id', 'device', 'name', 'type', 'enabled', 'lag', 'mtu', 'mac_address', 'mgmt_only',
            'description', 'connected_endpoint_type', 'connected_endpoint', 'connection_status', 'cable', 'mode',
            'untagged_vlan', 'tagged_vlans', 'tags', 'count_ipaddresses',
        ]

    def validate(self, data):

        # All associated VLANs be global or assigned to the parent device's site.
        device = self.instance.device if self.instance else data.get('device')
        untagged_vlan = data.get('untagged_vlan')
        if untagged_vlan and untagged_vlan.site not in [device.site, None]:
            raise serializers.ValidationError({
                'untagged_vlan': "VLAN {} must belong to the same site as the interface's parent device, or it must be "
                                 "global.".format(untagged_vlan)
            })
        for vlan in data.get('tagged_vlans', []):
            if vlan.site not in [device.site, None]:
                raise serializers.ValidationError({
                    'tagged_vlans': "VLAN {} must belong to the same site as the interface's parent device, or it must "
                                    "be global.".format(vlan)
                })

        return super().validate(data)
