from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.db import connection
from django.conf import settings

import logging, json

logger = logging.getLogger(__name__)

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
    rsp = '{"bounds":[%s,%s,%s,%s]}' % (-71.24645, 42.21182, -70.9357002, 42.48643,)
    #rsp = '{"bounds":[%s,%s,%s,%s]}' % nodedb.bounds()

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
    
    rsp = open('%s/routes-%d.json' % (settings.DATA_DIR, offset,), 'r')
    fc = json.load(rsp)
    rsp.close()

    resolution = 0.00001
    if 'scale' in request.GET:
        try:
            resolution = float(request.GET['scale'])
        except:
            pass

    length = 0
    nstrides = 0
    # trim excess coords

    return HttpResponse(json.dumps(fc), content_type='application/json')
