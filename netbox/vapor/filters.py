import django_filters
from django.db.models import Q

from extras.filters import CustomFieldFilterSet
from utilities.filters import NameSlugSearchFilterSet, NumericInFilter, TagFilter
from tenancy.models import Tenant, TenantGroup
from dcim.models import Device



class CustomerFilter(CustomFieldFilterSet):
    id__in = NumericInFilter(
        field_name='id',
        lookup_expr='in'
    )
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=TenantGroup.objects.all(),
        label='Group (ID)',
    )
    group = django_filters.ModelMultipleChoiceFilter(
        field_name='group__slug',
        queryset=TenantGroup.objects.all(),
        to_field_name='slug',
        label='Group (slug)',
    )
    tag = TagFilter()

    device = django_filters.ModelMultipleChoiceFilter(
        field_name='device__slug',
        queryset=Device.objects.all(),
        to_field_name='slug',
        label='Device (slug)',
    )

    class Meta:
        model = Tenant
        fields = ['name', 'slug']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(slug__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        )
