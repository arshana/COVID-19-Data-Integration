from urllib.request import HTTPBasicAuthHandler
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render

# Create your views here.

# homepage for testing
def home_view(request:HttpRequest):
    return HttpResponse("<h1> welcome to the introductory testing homepage </h1>" +  
    "<h2> type in requested url to see the mock up response we would give </h2/")

# returns countries with corresponding country codes GET request
def countries_view(request:HttpRequest):
    return HttpResponse("<h1> Where our countries will go </h>")

# returns country covid information nationally given a country name (or a country code)
def country_national_view(request:HttpRequest):
    if 'country-name' in request.GET:
        return HttpResponse("<h1> we will return info using " + request.GET['country-name'] + "</h1>")
    elif 'country-code' in request.GET:
        return HttpResponse("<h1> we will return info using " + request.GET['country-code'] + "</h1>")
    else:
        return HttpResponseBadRequest("<h1> you need either a country-name or country-code </h1>")

# returns all regional information for given country name or country code
def country_regions_view(request:HttpRequest):
    if 'country-name' in request.GET:
        return HttpResponse("<h1> we will return regional info using " + request.GET['country-name'] + "</h1>")
    elif 'country-code' in request.GET:
        return HttpResponse("<h1> we will return regional info using " + request.GET['country-code'] + "</h1>")
    else:
        return HttpResponseBadRequest("<h1> you need either a country-name or country-code  for regional data</h1>")

# returns regional information for the given region number
def region_view(request:HttpRequest):
    if 'region-code' in request.GET:
        return HttpResponse("<h1> will return all information on given region code " + request.GET['region-code'] + "</h1>")
    else:
        return HttpResponseBadRequest("<h1> you need the region-code for this function </h1>")
    
# returns all district information for given country name or country code
def country_districts_view(request:HttpRequest):
    if 'country-name' in request.GET:
        return HttpResponse("<h1> we will return district info using " + request.GET['country-name'] + "</h1>")
    elif 'country-code' in request.GET:
        return HttpResponse("<h1> we will return district info using " + request.GET['country-code'] + "</h1>")
    else:
        return HttpResponseBadRequest("<h1> you need either a country-name or country-code  for district data</h1>")

# returns all district information for the given region number
def region_districts_view(request:HttpRequest):
    if 'region-code' in request.GET:
        return HttpResponse("<h1> will return all information on districts using given region code " + request.GET['region-code'] + "</h1>")
    else:
        return HttpResponseBadRequest("<h1> you need the region-code for this function </h1>")

# returns regional information for the given district number
def district_view(request:HttpRequest):
    if 'district-code' in request.GET:
        return HttpResponse("<h1> will return all information on given district code " + request.GET['district-code'] + "</h1>")
    else:
        return HttpResponseBadRequest("<h1> you need the distict-code for this function </h1>")