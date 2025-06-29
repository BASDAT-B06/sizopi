"""
URL configuration for sizopi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from datasatwa import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', views.home, name='home'),  
    path('datasatwa/', include('datasatwa.urls')), 
    path('datahabitat/', include('datahabitat.urls')),
    path('profil/', include('profil.urls')),
    path("", include("main.urls")),
    path('kesehatan_hewan/', include('kesehatan_hewan.urls')), 
    path('pakan_hewan/', include('pakan_hewan.urls')), 
    path("auth/", include("authentication.urls")),
    path("atraksi_wahana/", include("atraksi_wahana.urls")),
    path("booking_tiket/", include("booking_tiket.urls")),
    path('dashboard/', include('dashboard.urls')),
    path('adopsi/', include('adopsi.urls')),
]
