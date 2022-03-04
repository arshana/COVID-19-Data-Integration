from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.db import connection

# Create your views here.

# homepage for testing
def home_view(request:HttpRequest):
    return HttpResponse("<h1> welcome to the introductory testing homepage </h1>" +  
    "<h2> type in requested url to see the mock up response we would give </h2/")

# returns countries with corresponding country codes GET request
def countries_view(request:HttpRequest):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Countries")
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
    results = []
    for row in rows:
        results.append(dict(zip(columns, row)))
    return HttpResponse(results)

# returns country covid information nationally given a country name (or a country code)
def country_national_view(request:HttpRequest):
    if 'country-name' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Cases_Per_Country, " +
             "Countries WHERE Countries.country_name = %s COLLATE NOCASE"
              + " AND Countries.country_code = Cases_Per_Country.country_code", [request.GET['country-name']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    elif 'country-code' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Cases_Per_Country, " +
             "Countries WHERE Countries.country_code = %s COLLATE NOCASE"
              + " AND Countries.country_code = Cases_Per_Country.country_code", [request.GET['country-code']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    else:
        return HttpResponseBadRequest("<h1> you need either a country-name or country-code </h1>")

# returns all regional information for given country name or country code
def country_regions_covid_view(request:HttpRequest):
    if 'country-name' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Cases_Per_Region, Regions, " +
             "Countries WHERE Countries.country_name = %s COLLATE NOCASE"
              + " AND Countries.country_code = Regions.country_code AND " 
              +  "Regions.region_code = Cases_Per_Region.region_code", [request.GET['country-name']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    elif 'country-code' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Cases_Per_Region, Regions, " +
             "Countries WHERE Countries.country_code = %s COLLATE NOCASE"
              + " AND Countries.country_code = Regions.country_code AND " 
              +  "Regions.region_code = Cases_Per_Region.region_code", [request.GET['country-code']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    else:
        return HttpResponseBadRequest("<h1> you need either a country-name or country-code  for regional data</h1>")

# returns regional information for the given region number
def region_view(request:HttpRequest):
    if 'region-code' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Cases_Per_Region, Regions " +
             "WHERE Regions.region_code = %s COLLATE NOCASE"
              + " AND Regions.region_code = Cases_Per_Region.region_code", [request.GET['region-code']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    else:
        return HttpResponseBadRequest("<h1> you need the region-code for this function </h1>")
    
# returns all district information for given country name or country code
def country_districts_covid_view(request:HttpRequest):
    if 'country-name' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Cases_Per_District, Regions, " +
             "Countries, Districts WHERE Countries.country_name = %s COLLATE NOCASE"
              + " AND Countries.country_code = Regions.country_code AND " 
              +  "Regions.region_code = Districts.region_code AND "
              + "Cases_Per_District.district_code = Districts.district_code", [request.GET['country-name']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    elif 'country-code' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Cases_Per_District, Regions, " +
             "Countries, Districts WHERE Countries.country_code = %s COLLATE NOCASE"
              + " AND Countries.country_code = Regions.country_code AND " 
              +  "Regions.region_code = Districts.region_code AND "
              +  "Cases_Per_District.district_code = Districts.district_code", [request.GET['country-code']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    else:
        return HttpResponseBadRequest("<h1> you need either a country-name or country-code  for district data</h1>")

# returns all district information for the given region number
def region_districts_covid_view(request:HttpRequest):
    if 'region-code' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Cases_Per_District, Regions, " +
             "Districts WHERE Regions.region_code = %s COLLATE NOCASE"
              + " AND Regions.region_code = Districts.region_code AND " 
              +  "Districts.district_code = Cases_Per_District.district_code", [request.GET['region-code']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    else:
        return HttpResponseBadRequest("<h1> you need the region-code for this function </h1>")

# returns district covid information for the given district number
def district_view(request:HttpRequest):
    if 'district-code' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Cases_Per_District, Districts" +
             " WHERE Districts.district_code = %s COLLATE NOCASE"
              + " AND Districts.district_code = Cases_Per_District.district_code", [request.GET['district-code']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    else:
        return HttpResponseBadRequest("<h1> you need the distict-code for this function </h1>")

# shows just the region information (not covid information) for a given country name or country code
def country_regions_view(request:HttpRequest):
    if 'country-name' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Countries, Regions" +
             " WHERE Countries.country_name = %s COLLATE NOCASE"
              + " AND Countries.country_code = Regions.country_code", [request.GET['district-code']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    elif 'country-code' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Countries, Regions" +
             " WHERE Countries.country_code = %s COLLATE NOCASE"
              + " AND Countries.country_code = Regions.country_code", [request.GET['district-code']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    else:
         return HttpResponseBadRequest("<h1> you need the country-name or country-code for this function </h1>")

# shows the districts (not covid information) for a given region-code
def region_districts_view(request:HttpRequest):
    if 'region-code' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Regions, Districts" +
             " WHERE Regions.region_code = %s COLLATE NOCASE"
              + " AND Regions.region_code = Districts.region_code", [request.GET['region-code']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    else:
         return HttpResponseBadRequest("<h1> you need a region-code for this function </h1>")

# shows just the region information (not covid information) for a given country name or country code
def country_regions_view(request:HttpRequest):
    if 'country-name' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Countries, Regions" +
             " WHERE Countries.country_name = %s COLLATE NOCASE"
              + " AND Countries.country_code = Regions.country_code", [request.GET['country-name']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    elif 'country-code' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Countries, Regions" +
             " WHERE Countries.country_code = %s COLLATE NOCASE"
              + " AND Countries.country_code = Regions.country_code", [request.GET['country-code']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    else:
         return HttpResponseBadRequest("<h1> you need the country-name or country-code for this function </h1>")

# shows the vacination information for a given region
def region_vaccination_view(request:HttpRequest):
    if 'region-code' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Regions, Vaccinations_Per_Region" +
             " WHERE Regions.region_code = %s COLLATE NOCASE"
              + " AND Regions.region_code = Vaccinations_Per_Region.region_code", [request.GET['region-code']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    else:
         return HttpResponseBadRequest("<h1> you need a region-code for this function </h1>")

# shows the sources for this project
def sources_view(request:HttpRequest):
    with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Sources")
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            results = []
            for row in rows:
                results.append(dict(zip(columns, row)))
            return HttpResponse(results)

# returns country vaccine information nationally given a country name (or a country code)
def country_national_vaccination_view(request:HttpRequest):
    if 'country-name' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Vaccinations_Per_Country, " +
             "Countries WHERE Countries.country_name = %s COLLATE NOCASE"
              + " AND Countries.country_code = Vaccinations_Per_Country.country_code", [request.GET['country-name']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    elif 'country-code' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Vaccinations_Per_Country, " +
             "Countries WHERE Countries.country_code = %s COLLATE NOCASE"
              + " AND Countries.country_code = Vaccinations_Per_Country.country_code", [request.GET['country-code']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    else:
        return HttpResponseBadRequest("<h1> you need either a country-name or country-code </h1>")

# returns district vaccine information for the given district number
def district_vaccination_view(request:HttpRequest):
    if 'district-code' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Vaccinations_Per_District, Districts" +
             " WHERE Districts.district_code = %s COLLATE NOCASE"
              + " AND Districts.district_code = Vaccinations_Per_District.district_code", [request.GET['district-code']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    else:
        return HttpResponseBadRequest("<h1> you need the distict-code for this function </h1>")

# returns country strain information nationally given a country name (or a country code)
def country_national_strain_view(request:HttpRequest):
    if 'country-name' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Strains_Per_Country, " +
             "Countries WHERE Countries.country_name = %s COLLATE NOCASE"
              + " AND Countries.country_code = Strains_Per_Country.country_code", [request.GET['country-name']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    elif 'country-code' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Strains_Per_Country, " +
             "Countries WHERE Countries.country_code = %s COLLATE NOCASE"
              + " AND Countries.country_code = Strains_Per_Country.country_code", [request.GET['country-code']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    else:
        return HttpResponseBadRequest("<h1> you need either a country-name or country-code </h1>")

# shows the strain information for a given region
def region_strain_view(request:HttpRequest):
    if 'region-code' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Regions, Strains_Per_Region" +
             " WHERE Regions.region_code = %s COLLATE NOCASE"
              + " AND Regions.region_code = Strains_Per_Region.region_code", [request.GET['region-code']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    else:
         return HttpResponseBadRequest("<h1> you need a region-code for this function </h1>")

# returns district strain information for the given district number
def district_strain_view(request:HttpRequest):
    if 'district-code' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Strains_Per_District, Districts" +
             " WHERE Districts.district_code = %s COLLATE NOCASE"
              + " AND Districts.district_code = Strains_Per_District.district_code", [request.GET['district-code']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    else:
        return HttpResponseBadRequest("<h1> you need the distict-code for this function </h1>")

# returns country population information nationally given a country name (or a country code)
def country_national_population_view(request:HttpRequest):
    if 'country-name' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Population_Per_Country, " +
             "Countries WHERE Countries.country_name = %s COLLATE NOCASE"
              + " AND Countries.country_code = Population_Per_Country.country_code", [request.GET['country-name']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    elif 'country-code' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Population_Per_Country, " +
             "Countries WHERE Countries.country_code = %s COLLATE NOCASE"
              + " AND Countries.country_code = Population_Per_Country.country_code", [request.GET['country-code']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    else:
        return HttpResponseBadRequest("<h1> you need either a country-name or country-code </h1>")

# shows the population information for a given region
def region_population_view(request:HttpRequest):
    if 'region-code' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Regions, Population_Per_Region" +
             " WHERE Regions.region_code = %s COLLATE NOCASE"
              + " AND Regions.region_code = Population_Per_Region.region_code", [request.GET['region-code']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    else:
         return HttpResponseBadRequest("<h1> you need a region-code for this function </h1>")

# returns district population information for the given district number
def district_population_view(request:HttpRequest):
    if 'district-code' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Population_Per_District, Districts" +
             " WHERE Districts.district_code = %s COLLATE NOCASE"
              + " AND Districts.district_code = Population_Per_District.district_code", [request.GET['district-code']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    else:
        return HttpResponseBadRequest("<h1> you need the distict-code for this function </h1>") 

# returns country age information nationally given a country name (or a country code)
def country_national_age_view(request:HttpRequest):
    if 'country-name' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Age_Per_Country, " +
             "Countries WHERE Countries.country_name = %s COLLATE NOCASE"
              + " AND Countries.country_code = Age_Per_Country.country_code", [request.GET['country-name']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    elif 'country-code' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Age_Per_Country, " +
             "Countries WHERE Countries.country_code = %s COLLATE NOCASE"
              + " AND Countries.country_code = Age_Per_Country.country_code", [request.GET['country-code']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    else:
        return HttpResponseBadRequest("<h1> you need either a country-name or country-code </h1>")

# shows the age information for a given region
def region_age_view(request:HttpRequest):
    if 'region-code' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Regions, Age_Per_Region" +
             " WHERE Regions.region_code = %s COLLATE NOCASE"
              + " AND Regions.region_code = Age_Per_Region.region_code", [request.GET['region-code']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    else:
         return HttpResponseBadRequest("<h1> you need a region-code for this function </h1>")

# returns district age information for the given district number
def district_age_view(request:HttpRequest):
    if 'district-code' in request.GET:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Age_Per_District, Districts" +
             " WHERE Districts.district_code = %s COLLATE NOCASE"
              + " AND Districts.district_code = Age_Per_District.district_code", [request.GET['district-code']])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        return HttpResponse(results)
    else:
        return HttpResponseBadRequest("<h1> you need the distict-code for this function </h1>")   