from django.shortcuts import render_to_response
from django.db.models import Count

from models import Trip

import logging

logger = logging.getLogger(__name__)

def home(request):
    return render_to_response('index.html', mimetype='text/html')


# Create your views here.
def counts(request):
    counts = { 'counts': Trip.objects.values('bike_nr').annotate(bike_cnt=Count('bike_nr')).order_by('-bike_cnt') }

    return render_to_response('counts.json', counts, mimetype='application/json')
