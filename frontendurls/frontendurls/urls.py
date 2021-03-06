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
from pages.views import (home_view, all_from_table_view, info_from_area_view,
                         sources_from_info_and_area_view, regions_from_country_view, districts_from_region_view)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view),
    path('all-from-table/', all_from_table_view),
    path('info-from-area/', info_from_area_view),
    path('sources-from-info-and-area/', sources_from_info_and_area_view),
    path('regions-from-country/', regions_from_country_view),
    path('districts-from-region/', districts_from_region_view)
]
