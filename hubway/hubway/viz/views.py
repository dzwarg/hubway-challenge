from django.shortcuts import render_to_response
from django.db.models import Count

from models import Trip

import logging

logger = logging.getLogger(__name__)

def home(request):
    """
    The initial page for the web application.
    """
    return render_to_response('index.html', mimetype='text/html')


# Create your views here.
def counts(request):
    """
    A web 'handler' that returns the number of rides per bike.
    """
    counts = { 'counts': Trip.objects.values('bike_nr').annotate(bike_cnt=Count('bike_nr')).order_by('-bike_cnt') }

    return render_to_response('counts.json', counts, mimetype='application/json')


def trips(request, number):
    """
    A web 'handler' that returns the trips of a single bicycle.
    """
    trips = Trip.objects.filter(bike_nr=number).order_by('start_date')
    
    def to_millis(x):
        return { 
            'start_date': x.start_date.isoformat(),
            'end_date': x.end_date.isoformat(),
            'gender': x.gender
        }
        
    trips = map(to_millis, trips)
    
    trips = { 'trips': trips }
    
    return render_to_response('trips.json', trips, mimetype='application/json')