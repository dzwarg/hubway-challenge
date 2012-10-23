from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.db import connection
from django.conf import settings

# routing!
from graphserver.ext.osm import osmdb
from graphserver.graphdb import GraphDatabase
from graphserver.core import State, WalkOptions
from time import time

import logging

logger = logging.getLogger(__name__)

logger.debug('Loading street OSM network...')
nodedb = osmdb.OSMDB(settings.DATA_DIR+'/boston.osmdb')

logger.debug('Loading street network graph...')
gdb = GraphDatabase(settings.DATA_DIR+'/boston.gdb')
graph = gdb.incarnate()

logger.debug('Loading station/trip network...')
tripdb = osmdb.OSMDB(settings.DATA_DIR+'/trip_data.db')

st = State(1,time())
wo = WalkOptions()

def home(request):
    """
    The initial page for the web application.
    """
    return render_to_response('map/index.html', mimetype='text/html')
    
def districts(request):
    """
    Serve a static geojson file.
    """
    d = open(settings.DATA_DIR + '/va.geojson','r')

    lines = d.read()

    d.close()

    return HttpResponse(lines, content_type='application/json');
    
def bounds(request):
    """
    Get the overall bounds of the map.
    """
    rsp = '{"bounds":[%s,%s,%s,%s]}' % nodedb.bounds()
    
    return HttpResponse(rsp, content_type='application/json')

def routes(request):
    """
    Get the parameters from the request, call _spt, and JSON serialize the results.
    """
    offset = 0
    if 'offset' in request.GET:
        try:
            offset = int(request.GET['offset'])
        except:
            pass
    logger.info('offset of routes to calculate is %d' % offset)
    
    limit = 10
    if 'limit' in request.GET:
        try:
            limit = int(request.GET['limit'])
        except:
            pass
    logger.info('limit of routes to calculate is %d' % limit)

    all_geom = []

    cursor = tripdb.get_cursor()
    
    tripcount = 0
    
    # For each station
    for tnode in tripdb.nodes():
        lat1 = float(tnode[2])
        lng1 = float(tnode[3])
        
        # find origin node on the street network
        orig = nodedb.nearest_node(lat1, lng1)
        
        # get all trips departing this station
        tedges = cursor.execute("select * from edges where start_nd = ?", [tnode[0]])
        
        # For each trip
        for tedge in tedges:
            if tedge[3] == '':
                logger.warn('Edge %s has no destination node.' % tedge[0])
                continue
                
            dnode = tripdb.node(tedge[3])
            
            lat2 = float(dnode[2])
            lng2 = float(dnode[3])
            
            if lat2 == lat1 and lng2 == lng1:
                # Do not route something that ends where it begins
                logger.warn('Begin and end node are the same (%s, %s).' % (orig[0], dnode[0]))
            else:
                if tripcount < offset:
                    tripcount += 1
                    continue
                    
                # find the destination node on the street network
                dest = nodedb.nearest_node(lat2, lng2)
            
                # route!
                geom = _spt(orig, dest)

                all_geom.append((tripcount,geom))
            
                tripcount += 1
            
            if tripcount >= offset + limit:
                break
        
        if tripcount >= offset + limit:
            break
            
    return render_to_response('map/featurecollection.json', {'features':all_geom}, mimetype='application/json')
                

def _spt(orig, dest):
    """
    Use graphserver to calculate the shortest path tree between two nodes.
    """
    spt = graph.shortest_path_tree('osm-'+orig[0], 'osm-'+dest[0], st, wo)

    # get the path vertices and edges
    pvert, pedges = spt.path('osm-'+dest[0])

    # convert the results to geometries
    allgeom = []
    for e in pedges:
        dbedge = nodedb.edge(e.payload.name)
        if e.payload.reverse_of_source:
            allgeom.extend( reversed( dbedge[5] ) )
        else:
            allgeom.extend( dbedge[5] )

    return allgeom
