from django.conf import settings
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User
from django.contrib.sites.admin import SiteAdmin
from django.contrib.sites.models import Site
from allauth.socialaccount.admin import (
    SocialApp,
    SocialAppAdmin,
    SocialAccount,
    SocialAccountAdmin,
    SocialToken,
    SocialTokenAdmin,
)


class NetBoxAdminSite(AdminSite):
    """
    Custom admin site
    """
    site_header = 'NetBox Administration'
    site_title = 'NetBox'
    site_url = '/{}'.format(settings.BASE_PATH)
    index_template = 'django_rq/index.html'


admin_site = NetBoxAdminSite(name='admin')

# Register external models
admin_site.register(Group, GroupAdmin)
admin_site.register(User, UserAdmin)
admin_site.register(Site, SiteAdmin)

# Register allauth models
admin_site.register(SocialApp, SocialAppAdmin)
admin_site.register(SocialAccount, SocialAccountAdmin)
admin_site.register(SocialToken, SocialTokenAdmin)
