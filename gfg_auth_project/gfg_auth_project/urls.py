from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('gfg_auth_app.urls')),  # This routes all traffic to your app
]
