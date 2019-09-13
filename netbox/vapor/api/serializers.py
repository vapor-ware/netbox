from rest_framework import serializers
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField

from extras.api.customfields import CustomFieldModelSerializer
from tenancy.models import Tenant, TenantGroup
from utilities.api import ValidatedModelSerializer
from dcim.api.nested_serializers import NestedDeviceSerializer
from tenancy.api.nested_serializers import NestedTenantGroupSerializer

#
# Customers
#

class CustomerSerializer(TaggitSerializer, CustomFieldModelSerializer):
    group = NestedTenantGroupSerializer(required=False)
    tags = TagListSerializerField(required=False)
    devices = NestedDeviceSerializer(required=False, many=True)

    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'slug', 'group', 'description', 'comments', 'tags', 'custom_fields', 'created',
            'last_updated', 'devices',
        ]
