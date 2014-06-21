import os, json, subprocess, itertools, re

def shapefile2geojson(shapefilepath):
    '''Converts a shapefile to a geojson file with spherical mercator.
    '''
    geojsonfilepath = '{0}.geojson'.format(shapefilepath)

    args = 'ogr2ogr -t_srs EPSG:4326  -f GeoJSON ___ ___'.split()
    args[-2:] = geojsonfilepath, shapefilepath
    if os.path.exists(geojsonfilepath):
        os.remove(geojsonfilepath)
    subprocess.check_call(args)
    geojson_data = open(geojsonfilepath)
    geojson = json.load(geojson_data)
    geojson_data.close()
    return geojson

def segments_transform(raw_geojson, steward):
    ''' Return a new GeoJSON structure, with standard fields guessed from properties.
    '''
    opentrails_geojson = {'type': 'FeatureCollection', 'features': []}
    id_counter = itertools.count(1)

    for old_segment in raw_geojson['features']:
        old_properties = old_segment['properties']
    
        new_segment = {
         "type" : "Feature",
         "geometry" : old_segment['geometry'],
         "properties" : {
             "id" : find_segment_id(old_properties) or id_counter.next(),
             "stewardId" : None,
             "name" : None,
             "vehicles" : None,
             "foot" : find_segment_foot_use(old_properties),
             "bicycle" : find_segment_bicycle_use(old_properties),
             "horse" : find_segment_horse_use(old_properties),
             "ski" : None,
             "wheelchair" : None,
             "osmTags" : None
         }
        }
        opentrails_geojson['features'].append(new_segment)

    return opentrails_geojson

def find_segment_id(properties):
    ''' Return the value of a unique segment identifier from feature properties.
    
        Implements logic in https://github.com/codeforamerica/PLATS/issues/26
    '''
    keys, values = zip(*[(k.lower(), v) for (k, v) in properties.items()])
    
    for field in ('id', 'trailid', 'objectid'):
        if field in keys:
            return values[keys.index(field)]
    
    return None

def _has_listed_field(properties, fieldnames):
    ''' Return true if properties has one of the case-insensitive field names.
    '''
    keys = [k.lower() for k in properties.keys()]

    for field in fieldnames:
        if field.lower() in keys:
            return True
    
    return False

def _get_value_yes_no(properties, fieldnames):
    ''' Return yes/no value for one of the case-insensitive field names.
    '''
    yes_nos = {'y': 'yes', 'yes': 'yes', 'n': 'no', 'no': 'no'}
    
    keys, values = zip(*[(k.lower(), v) for (k, v) in properties.items()])

    for field in fieldnames:
        if field.lower() in keys:
            value = values[keys.index(field)]
            return yes_nos.get(value.lower(), None)
    
    return None

def _get_match_yes_no(properties, pattern, fieldnames):
    ''' Return yes/no value for pattern match on one of the case-insensitive field names.
    '''
    keys, values = zip(*[(k.lower(), v) for (k, v) in properties.items()])

    for field in fieldnames:
        if field.lower() in keys:
            value = values[keys.index(field)]
            
            if type(value) not in (str, unicode):
                return None
            
            return pattern.search(value) and 'yes' or 'no'
    
    return None

def find_segment_foot_use(properties):
    ''' Return the value of a segment foot use flag from feature properties.
    
        Implements logic in https://github.com/codeforamerica/PLATS/issues/28
    '''
    # Search for a hike column
    fieldnames = 'hike', 'walk', 'foot'
    
    if _has_listed_field(properties, fieldnames):
        return _get_value_yes_no(properties, fieldnames)

    # Search for a use column and look for hiking inside
    fieldnames = 'use', 'use_type', 'pubuse'
    pattern = re.compile(r'\b(multi-use|hike|foot|hiking|walk|walking)\b', re.I)
    
    if _has_listed_field(properties, fieldnames):
        return _get_match_yes_no(properties, pattern, fieldnames)
            
    return None

def find_segment_bicycle_use(properties):
    ''' Return the value of a segment bicycle use flag from feature properties.
    
        Implements logic in https://github.com/codeforamerica/PLATS/issues/29
    '''
    # Search for a bicycle column
    fieldnames = 'bike', 'roadbike', 'bikes', 'road bike', 'mtnbike'
    
    if _has_listed_field(properties, fieldnames):
        return _get_value_yes_no(properties, fieldnames)

    # Search for a use column and look for biking inside
    fieldnames = 'use', 'use_type', 'pubuse'
    pattern = re.compile(r'\b(multi-use|bike|roadbike|bicycling|bicycling)\b', re.I)
    
    if _has_listed_field(properties, fieldnames):
        return _get_match_yes_no(properties, pattern, fieldnames)
            
    return None

def find_segment_horse_use(properties):
    ''' Return the value of a segment horse use flag from feature properties.
    
        Implements logic in https://github.com/codeforamerica/PLATS/issues/30
    '''
    # Search for a horse column
    fieldnames = 'horse', 'horses', 'equestrian'
    
    if _has_listed_field(properties, fieldnames):
        return _get_value_yes_no(properties, fieldnames)

    # Search for a use column and look for horsies inside
    fieldnames = 'use', 'use_type', 'pubuse'
    pattern = re.compile(r'\b(horse|horses|equestrian)\b', re.I)
    
    if _has_listed_field(properties, fieldnames):
        return _get_match_yes_no(properties, pattern, fieldnames)
            
    return None

def portland_transform(raw_geojson):

    opentrails_geojson = {'type': 'FeatureCollection', 'features': []}

    def bicycle(properties):
        if properties['ROADBIKE'] == 'Yes' or properties['MTNBIKE'] == 'Yes':
            return "yes"
        else:
            return "no"

    def horse(properties):
        if properties['EQUESTRIAN'] == 'Yes':
            return "yes"
        else:
            return "no"

    def wheelchair(properties):
        if properties['ACCESSIBLE'] == 'Yes':
            return "yes"
        else:
            return "no"

    for old_segment in raw_geojson['features']:
        new_segment = {
         "type" : "Feature",
         "geometry" : old_segment['geometry'],
         "properties" : {
             "id" : old_segment['properties']['TRAILID'],
             "stewardId" : old_segment['properties']['AGENCYNAME'],
             "name" : old_segment['properties']['TRAILNAME'],
             "vehicles" : None,
             "foot" : old_segment['properties']['HIKE'].lower(),
             "bicycle" : bicycle(old_segment['properties']),
             "horse" : horse(old_segment['properties']),
             "ski" : None,
             "wheelchair" : wheelchair(old_segment['properties']),
             "osmTags" : None
         }
        }
        opentrails_geojson['features'].append(new_segment)

    return opentrails_geojson

def sa_transform(raw_geojson, steward_id):

    opentrails_geojson = {'type': 'FeatureCollection', 'features': []}

    trailhead_ids = 1
    for old_trailhead in raw_geojson['features']:
        new_trailhead = {
         "type" : "Feature",
         "geometry" : old_trailhead['geometry'],
         "properties" : {
            "name": old_trailhead['properties']['Name'],
            "id": trailhead_ids,
            "trailIds": None,
            "stewardId": steward_id,
            "areaId": None,
            "address": None,
            "parking": None,
            "drinkwater": None,
            "restrooms": None,
            "kiosk": None,
            "osmTags": None
         }
        }
        opentrails_geojson['features'].append(new_trailhead)
        trailhead_ids += 1

    return opentrails_geojson
