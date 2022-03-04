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
                         region_view, region_districts_view, district_view, country_districts_covid_view,
                         country_regions_covid_view, region_districts_covid_view, region_vaccination_view,
                         sources_view, country_national_vaccination_view, district_vaccination_view,
                         country_national_strain_view, region_strain_view, district_strain_view,
                         country_national_population_view, region_population_view, district_population_view,
                         country_national_age_view, region_age_view, district_age_view)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('countries/', countries_view),
    path('', home_view),
    path('country-national/', country_national_view),
    path('country-regional/', country_regions_covid_view),
    path('region/', region_view),
    path('country-district/', country_districts_covid_view),
    path('region-district/', region_districts_covid_view),
    path('district/', district_view),
    path('country-regions/', country_regions_view),
    path('region-districts/', region_districts_view),
    path('region-vaccinations/', region_vaccination_view),
    path('sources/', sources_view),
    path('country-national-vaccinations/', country_national_vaccination_view),
    path('district-vaccinations/', district_vaccination_view),
    path('country-national-strains/', country_national_strain_view),
    path('region-strains/', region_strain_view),
    path('district-strains/', district_strain_view),
    path('country-national-population/', country_national_population_view),
    path('region-population/', region_population_view),
    path('district-population/', district_population_view),
    path('country-national-age/', country_national_age_view),
    path('region-age/', region_age_view),
    path('district-age/', district_age_view),
]
