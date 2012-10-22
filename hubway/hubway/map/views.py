from django.shortcuts import render_to_response
from django.db import connection

import logging

logger = logging.getLogger(__name__)

def home(request):
    """
    The initial page for the web application.
    """
    return render_to_response('map/index.html', mimetype='text/html')
    
def trips(request):
    return render_to_response('map/index.html', mimetype='text/html')