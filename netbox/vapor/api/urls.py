from rest_framework import routers

from . import views


class VaporRootView(routers.APIRootView):
    """
    Vapor API root view
    """
    def get_view_name(self):
        return 'Vapor'


router = routers.DefaultRouter()
router.APIRootView = VaporRootView

router.register(r'customers', views.CustomerViewSet)

app_name = 'vapor-api'
urlpatterns = router.urls
