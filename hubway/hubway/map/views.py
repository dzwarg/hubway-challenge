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
gdb = GraphDatabase(DATA_DIR+'/boston.gdb')
graph = gdb.incarnate()

logger.debug('Loading station/trip network...')
tripdb = osmdb.OSMDB(DATA_DIR+'/trip_data.db')

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

def route(request):
    """
    Get the parameters from the request, call _spt, and JSON serialize the results.
    """
    pass

def _spt(orig, dest):
    """
    Use graphserver to calculate the shortest path tree between two nodes.
    """
    spt = graph.shortest_path_tree('osm-'+orig[0], 'osm-'+dest[0], State(1,time()), WalkOptions())

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
