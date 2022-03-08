import string
from typing import Dict, Set
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.db import connection
import json

from sqlalchemy import true

# Create your views here.
areas:Set = {'countries', 'regions', 'districts'} # areas that we can attain information
info_types:Set = {'cases', 'vaccinations', 'strains', 'population', 'age'} # different types of Covid information
plural_to_singular:Dict = {'countries': 'country', 'regions': 'region', 'districts': 'district'}

# homepage for testing
def home_view(request:HttpRequest):
    return HttpResponse("<h1> welcome to the introductory testing homepage </h1>" +  
    "<h2> type in requested url to see the mock up response we would give </h2/")

# returns all given rows of output for the given table
# table is case insensitive, and must be one from areas or 'source
def all_from_table_view(request:HttpRequest):
    if ('table' in request.GET):
        table:string = request.GET['table'].lower()
        if (table in areas or table == 'sources'):
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM " + table)
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
            results = []
            for row in rows:
                results.append(dict(zip(columns, row)))
            return HttpResponse(json.dumps(results))
        else:
            return HttpResponseBadRequest('you gave a table parameter that does not reflect a valid table'
                                         + 'valid options are ' + str(areas) + ' or sources')
    else:
        return HttpResponseBadRequest("You need to provide a table parameter, given options are " 
                                    + str(areas) + " and sources")

# returns all given rows of output for the given area
# regarding the given info_type 
# both area and info-type are case insensitive
# and both must reside in the respect areas and info_types
# you can also give an optional param 'sources'
# must be a list in the form (#, #, #) where # is a source.source_id
# also can take in an optional param of country-name
# country-name can be used only if area = 'countries'
# country-name will be used to distinguish what country in question
# else you should use area-code to distinguish what specific area in the area table
# you want information queried on
def info_from_area_view(request:HttpRequest):
    if ('area' in request.GET and 'info-type' in request.GET):
        area:string = request.GET['area'].lower()
        info_type:string = request.GET['info-type'].lower()
        if (area in areas and info_type in info_types):    
            area_code_name:string = plural_to_singular[area] + "_code"
            area_table_code:string = area + "." + area_code_name
            info_table = info_type + "_Per_" + plural_to_singular[area]
            info_table_code:string = info_table + "." + area_code_name
            info_table_source:string = info_table + ".source_id"
            sources_sub_section:string = "true" # dummy value if no sources param
            if ('sources' in request.GET):
                sources_sub_section = "sources.source_id in " + str(request.GET['sources'])
                area_id_val:string = "" # will be used to identify the area row in question
                area_table_identifier:string = "" # will be the attribute of the given area table
            if ('country-name' in request.GET and area == 'countries'):
                area_table_identifier = 'country_name'
                area_id_val = request.GET['country-name']
            elif ('country-name' in request.GET):
                return HttpResponseBadRequest('country-name can only be a param if given country for area param, not ' + area)
            elif ('area-code' in request.GET):
                area_table_identifier = area + "." + area_code_name
                area_id_val = request.GET['area-code']
            else:
                return HttpResponseBadRequest('you must give an area-code if not using country-name with area = countries')
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM sources, " + area + ", " + info_table 
                + " WHERE " + area_table_identifier + " = %s COLLATE NOCASE AND "
                + area_table_code + " = " + info_table_code 
                + " AND " + sources_sub_section + " AND sources.source_id = " + info_table_source, [area_id_val])
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
            results = []
            for row in rows:
                results.append(dict(zip(columns, row)))
            return HttpResponse(json.dumps(results))
        else:
            return HttpResponseBadRequest('you gave an area or info_type parameter that does not reflect a valid table'
                                         + 'valid options for area are ' + str(areas) +
                                        'and valid options for info-type are' + str(info_types))
    else:
        return HttpResponseBadRequest("You need to provide an area parameter" 
        + "and an info-type parameter and given area options are " + str(areas) 
        + " and given info-type options are " + str(info_types))

# returns all source informatoin for the given area
# regarding the given info_type 
# both area and info-type are case insensitive
# and both must reside in the respect areas and info_types
# also can take in an optional param of country-name
# country-name can be used only if area = 'countries'
# country-name will be used to distinguish what country in question
# else you should use area-code to distinguish what specific area in the area table
# you want sources information queried on
def sources_from_info_and_area_view(request:HttpRequest):
    if ('area' in request.GET and 'info-type' in request.GET):
        area:string = request.GET['area'].lower()
        info_type:string = request.GET['info-type'].lower()
        if (area in areas and info_type in info_types):    
            area_code_name:string = plural_to_singular[area] + "_code"
            area_table_code:string = area + "." + area_code_name
            info_table = info_type + "_Per_" + plural_to_singular[area]
            info_table_code:string = info_table + "." + area_code_name
            info_table_source:string = info_table + ".source_id"
            if ('country-name' in request.GET and area == 'countries'):
                area_table_identifier = 'country_name'
                area_id_val = request.GET['country-name']
            elif ('country-name' in request.GET):
                return HttpResponseBadRequest('country-name can only be a param if given country for area param, not ' + area)
            elif ('area-code' in request.GET):
                area_table_identifier = area + "." + area_code_name
                area_id_val = request.GET['area-code']
            else:
                return HttpResponseBadRequest('you must give an area-code if not using country-name with area = countries')
            with connection.cursor() as cursor:
                cursor.execute("SELECT DISTINCT sources.source_information, sources.source_id FROM sources, " + area + ", " + info_table 
                + " WHERE " + area_table_identifier + " = %s COLLATE NOCASE AND "
                + area_table_code + " = " + info_table_code 
                + " AND sources.source_id = " + info_table_source + " ORDER BY sources.source_id", [area_id_val])
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
            results = []
            for row in rows:
                results.append(dict(zip(columns, row)))
            return HttpResponse(json.dumps(results))
        else:
            return HttpResponseBadRequest('you gave an area or info_type parameter that does not reflect a valid table'
                                         + 'valid options for areas are ' + str(areas) +
                                        'and valid options for info_types are' + str(info_types))
    else:
        return HttpResponseBadRequest("You need to provide an area parameter" 
        + "and an info_type parameter and an area_code parameter, given area options are " + str(areas) 
        + " and given info_type options are " + str(info_types))

# given either country-name or country-code
# returns all regions that belong to that country
# country-name has precedence over country-code
def regions_from_country_view(request:HttpRequest):
    if 'country-name' in request.GET:
        with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM Countries, Regions" 
                + " WHERE Countries.country_name = %s COLLATE NOCASE" 
                + " AND Countries.country_code = Regions.country_code", [request.GET['country-name']])
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                results = []
                for row in rows:
                    results.append(dict(zip(columns, row)))
                return HttpResponse(json.dumps(results))
    elif 'country-code' in request.GET:
        with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM Countries, Regions" 
                + " WHERE Countries.country_code = %s COLLATE NOCASE" 
                + " AND Countries.country_code = Regions.country_code", [request.GET['country-code']])
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                results = []
                for row in rows:
                    results.append(dict(zip(columns, row)))
                return HttpResponse(json.dumps(results))
    else:
        return HttpResponseBadRequest('you must give either a country-code or a country-name for this function to work')

# given a region-code
# returns all districts that belong to that region
def districts_from_region_view(request:HttpRequest):
    if 'region-code' in request.GET:
        with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM Regions, Districts" 
                + " WHERE Regions.region_code = %s COLLATE NOCASE" 
                + " AND Regions.region_code = Districts.region_code", [request.GET['region-code']])
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                results = []
                for row in rows:
                    results.append(dict(zip(columns, row)))
                return HttpResponse(json.dumps(results))
    else:
        return HttpResponseBadRequest('you must give a region-code for this function to work')