#!/usr/bin/env python
from graphserver.ext.osm import osmdb
from graphserver.graphdb import GraphDatabase
from graphserver.core import State, WalkOptions
from time import time
import argparse

DATA_DIR = '../data/'

def main(count):
    print 'Loading boston.osmdb'
    nodedb = osmdb.OSMDB(DATA_DIR+'boston.osmdb')

    print 'Importing Boston street network...'
    gdb = GraphDatabase(DATA_DIR+'boston.gdb')
    graph = gdb.incarnate()

    print 'Importing trip network...'
    tripdb = osmdb.OSMDB(DATA_DIR+'trip_data.db')
    
    stime = time()
    wo = WalkOptions()
    
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
            dnode = tripdb.node(tedge[3])
            
            lat2 = float(dnode[2])
            lng2 = float(dnode[3])
            
            if lat2 == lat1 and lng2 == lng1:
                # Do not route something that ends where it begins
                print 'Begin and end node are the same.'
            else:
                # find the destination node on the street network
                dest = nodedb.nearest_node(lat2, lng2)
            
                # route!
                spt = graph.shortest_path_tree('osm-'+orig[0], 'osm-'+dest[0], State(1,stime), wo)
            
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
            
                print allgeom
            
            tripcount += 1
            
            if tripcount >= count:
                break
        
        if tripcount >= count:
            break
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Route hubway bike trips.')
    parser.add_argument('count', metavar='C', type=int, default=1,
        help='The number of trips to calculate.')
        
    args = parser.parse_args()
    
    main(args.count)