from django import urls
from django.urls.resolvers import URLPattern
from .views import AdminViewSet, GetCsrfToken, Getdata, StaffViewSet, UserViewSet,LoginView,LogoutView
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt

router = DefaultRouter()
router.register('users',UserViewSet,basename='User'),
router.register('admin',AdminViewSet,basename='Admin')
router.register('staff',StaffViewSet,basename='Staff')

urlpatterns = [
    path('user/',include(router.urls) ),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('json/',csrf_exempt(Getdata.as_view())),
    path('csftoken/',GetCsrfToken.as_view())
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
