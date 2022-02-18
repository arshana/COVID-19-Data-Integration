"""frontendurls URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path
from pages.views import (countries_view, home_view, country_national_view, country_regions_view,
                         region_view, country_districts_view, region_districts_view, district_view)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('countries/', countries_view),
    path('', home_view),
    path('country-national/', country_national_view),
    path('country-regional/', country_regions_view),
    path('region/', region_view),
    path('country-district/', country_districts_view),
    path('region-district/', region_districts_view),
    path('district/', district_view)
]
