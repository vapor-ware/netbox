from rest_framework import serializers
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField

from extras.api.customfields import CustomFieldModelSerializer
from dcim.api.nested_serializers import (
    NestedDeviceSerializer,
    NestedInterfaceSerializer,
    NestedCableSerializer,
)
from dcim.api.serializers import (
    InterfaceConnectionSerializer,
    ConnectedEndpointSerializer,
    IFACE_TYPE_CHOICES,
    IFACE_MODE_CHOICES,
)
from dcim.models import Interface
from ipam.api.nested_serializers import NestedVLANSerializer
from ipam.models import VLAN
from tenancy.api.nested_serializers import NestedTenantGroupSerializer
from utilities.api import ChoiceField, ValidatedModelSerializer, SerializedPKRelatedField
from tenancy.models import Tenant as Customer


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
    type = ChoiceField(choices=IFACE_TYPE_CHOICES, required=False)
    # TODO: Remove in v2.7 (backward-compatibility for form_factor)
    form_factor = ChoiceField(choices=IFACE_TYPE_CHOICES, required=False)
    lag = NestedInterfaceSerializer(required=False, allow_null=True)
    mode = ChoiceField(choices=IFACE_MODE_CHOICES, required=False, allow_null=True)
    untagged_vlan = NestedVLANSerializer(required=False, allow_null=True)
    tagged_vlans = SerializedPKRelatedField(
        queryset=VLAN.objects.all(),
        serializer=NestedVLANSerializer,
        required=False,
        many=True
    )
    cable = NestedCableSerializer(read_only=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Interface
        fields = [
            'id', 'device', 'name', 'type', 'form_factor', 'enabled', 'lag', 'mtu', 'mac_address', 'mgmt_only',
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
