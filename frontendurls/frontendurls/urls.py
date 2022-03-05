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
from pages.views import (countries_view, home_view, country_cases_view, country_regions_view,
                         region_cases_view, region_districts_view, district_cases_view, country_districts_cases_view,
                         country_regions_cases_view, region_districts_cases_view, region_vaccination_view,
                         sources_view, country_vaccination_view, district_vaccination_view,
                         country_strain_view, region_strain_view, district_strain_view,
                         country_population_view, region_population_view, district_population_view,
                         country_ages_view, region_ages_view, district_ages_view)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('countries/', countries_view),
    path('', home_view),
    path('country-cases/', country_cases_view),
    path('country-regions-cases/', country_regions_cases_view),
    path('region-cases/', region_cases_view),
    path('country-districts-cases/', country_districts_cases_view),
    path('region-districts/', region_districts_cases_view),
    path('district-cases/', district_cases_view),
    path('country-regions/', country_regions_view),
    path('region-districts/', region_districts_view),
    path('country-vaccinations/', country_vaccination_view),
    path('region-vaccinations/', region_vaccination_view),
    path('district-vaccinations/', district_vaccination_view),
    path('country-strains/', country_strain_view),
    path('region-strains/', region_strain_view),
    path('district-strains/', district_strain_view),
    path('country-population/', country_population_view),
    path('region-population/', region_population_view),
    path('district-population/', district_population_view),
    path('country-ages/', country_ages_view),
    path('region-ages/', region_ages_view),
    path('district-ages/', district_ages_view),
    path('sources/', sources_view)
]
