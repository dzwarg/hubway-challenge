from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.db import connection

import logging

logger = logging.getLogger(__name__)

def home(request):
    """
    The initial page for the web application.
    """
    return render_to_response('map/index.html', mimetype='text/html')
    
def districts(request):
    d = open('data/va.geojson','r')

    lines = d.read()

    d.close()

    return HttpResponse(lines, content_type='application/json');
