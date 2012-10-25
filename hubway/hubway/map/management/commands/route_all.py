from django.core.management.base import BaseCommand, CommandError
from django.template import loader, Template, Context
from django.conf import settings
from optparse import make_option

from graphserver.ext.osm import osmdb
from graphserver.graphdb import GraphDatabase
from graphserver.core import State, WalkOptions
from time import time

class Command(BaseCommand):
    help = 'Route all network trips.'
    option_list = BaseCommand.option_list + (
        make_option('-n', '--number',
            action='store',
            dest='number',
            default=100,
            type=int,
            help='The number of routes in a single batch.'),

        make_option('-o', '--output',
            action='store',
            dest='output',
            default='data',
            help='The output folder for the route GeoJSON files.'),
        )

    # we'll need these later
    nodedb = None
    graph = None
    tpl = loader.get_template('map/featurecollection.json')

    def handle(self, *args, **options):
        self.stdout.write('Loading boston.osmdb\n')
        self.nodedb = osmdb.OSMDB(settings.DATA_DIR+'/boston.osmdb')

        self.stdout.write('Importing Boston street network...\n')
        gdb = GraphDatabase(settings.DATA_DIR+'/boston.gdb')
        self.graph = gdb.incarnate()

        self.stdout.write('Importing trip network...\n')
        tripdb = osmdb.OSMDB(settings.DATA_DIR+'/trip_data.db')
        
        
        batchgeom = []
        count = 0

        # For each station
        for tnode in tripdb.nodes():
            lat1 = float(tnode[2])
            lng1 = float(tnode[3])
            
            # get all trips departing this station
            cursor = tripdb.get_cursor()
            tedges = cursor.execute("select * from edges where start_nd = ?", [tnode[0]])
            
            # For each trip
            for tedge in tedges:
                if tedge[3] == '':
                    if int(options['verbosity']) > 1:
                        self.stdout.write('Start and end nodes are the same.\n')
                    continue

                dnode = tripdb.node(tedge[3])

                lat2 = float(dnode[2])
                lng2 = float(dnode[3])

                dnode = None

                if lat2 == lat1 and lng2 == lng1:
                    continue

                geom = self._spt(lat1, lng1, lat2, lng2)
                count += 1

                batchgeom.append((count,geom,))
                
                if len(batchgeom) >= options['number']:
                    self.dropfile(batchgeom, count, **options)
                    batchgeom = []

                geom = None


            # Don't keep a history of the execute tranactions
            tedges = None
            cursor = None
           
    def _spt(self, lat1, lng1, lat2, lng2):
        """
        Calculate the shortest path tree, and return the geometry.
        """
        # find origin node on the street network
        orig = self.nodedb.nearest_node(lat1, lng1)
        dest = self.nodedb.nearest_node(lat2, lng2)
            
        # route!
        spt = self.graph.shortest_path_tree('osm-'+orig[0], 'osm-'+dest[0], State(1,time()), None)

        # get the path vertices and edges
        pvert, pedges = spt.path('osm-'+dest[0])
    
        orig = None
        dest = None

        # convert the results to geometries
        allgeom = []
        for e in pedges:
            dbedge = self.nodedb.edge(e.payload.name)
            if e.payload.reverse_of_source:
                allgeom.extend( reversed( dbedge[5] ) )
            else:
                allgeom.extend( dbedge[5] )

        spt.destroy()

        return allgeom

    def dropfile(self, geom, count, **options):
        ctx = Context({'features':geom})
        txt = self.tpl.render(ctx)

        filename = '%s/routes-%d.json' % (options['output'], count,)
        out = open(filename, 'w')
        out.write(txt)
        out.close()

        if int(options['verbosity']) > 0:
            self.stdout.write('Wrote route file: "%s"\n' % filename)

        out = None
        txt = None
        ctx = None
