from django.shortcuts import render_to_response
from django.db.models import Count, Min, Max, Q
from django.db import connection

from models import Trip

import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

def home(request):
    """
    The initial page for the web application.
    """
    return render_to_response('viz/index.html', mimetype='text/html')


# Create your views here.
def counts(request):
    """
    A web 'handler' that returns the number of rides per bike.
    """
    qset = Trip.objects.all()
    if 'g' in request.GET:
        qset = qset.filter(gender=request.GET['g'])
    lmt = None
    if 'l' in request.GET:
        try:
            lmt = min(int(request.GET['l']), 75)
        except:
            logger.warn('Incompatible value recieved for limit: "l=%s"' % request.GET['l'])

    counts = { 'counts': qset.values('bike_nr').annotate(bike_cnt=Count('bike_nr')).order_by('-bike_cnt')[:lmt] }

    return render_to_response('viz/counts.json', counts, mimetype='application/json')


def trips(request, number):
    """
    A web 'handler' that returns the trips of a single bicycle.
    """
    qset = Trip.objects.all()
    if 'g' in request.GET:
        qset = qset.filter(gender=request.GET['g'])
        
    trips = qset.filter(bike_nr=number).order_by('start_date')
    
    def to_millis(x):
        return { 
            'start_date': x.start_date.isoformat(),
            'end_date': x.end_date.isoformat(),
            'gender': x.gender
        }
        
    trips = map(to_millis, trips)
    
    trips = { 'trips': trips }
    
    return render_to_response('viz/trips.json', trips, mimetype='application/json')

def volume(request, number):
    """
    A web 'handler' that returns the total number of concurrent trips over time.
    The range of times is bounded the the first & last trip of the provided bike
    number.
    """
    qset = Trip.objects.all()
    if 'g' in request.GET:
        qset = qset.filter(gender=request.GET['g'])
        
    minmax = qset.filter(bike_nr=number).aggregate(tmin=Min('start_date'),tmax=Max('end_date'))
    resolution = 10000 # 20 rows, 500 px each

    def epoch(param):
        return 'EXTRACT(EPOCH FROM %s)' % param

    sql = """SELECT WIDTH_BUCKET(%s, %s, %s, %%s) AS BIN,
COUNT(WIDTH_BUCKET(%s, %s, %s, %%s)) AS COUNT
FROM TRIPS WHERE %s >= %s AND %s <= %s GROUP BY BIN""" % (
        epoch('START_DATE'), epoch('%s'), epoch('%s'),
        epoch('START_DATE'), epoch('%s'), epoch('%s'), 
        epoch('START_DATE'), epoch('%s'), epoch('END_DATE'), epoch('%s')
    )

    cursor = connection.cursor()
    cursor.execute(sql, [
        minmax['tmin'], minmax['tmax'], resolution, 
        minmax['tmin'], minmax['tmax'], resolution, 
        minmax['tmin'], minmax['tmax']
    ])

    tvol = { 'volume': cursor.fetchall() }

    return render_to_response('viz/volume.json', tvol, mimetype='application/json')
