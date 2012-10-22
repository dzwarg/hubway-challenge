#!/usr/bin/python

#  This file needs to read trips.csv and stations.csv from the hubway challenge data set.
#  Execute the code in the same directory as these files
#  Output:  one "gexf" file used in Gephi, and on "sqlite3" file for Zwarg
#  Can also uncomment the activity portion to see daily trips; it prints to stdout

import collections
from lxml import etree
import math
import sqlite3

def multi_dimensions(n, type):
    """ Creates an n-dimensional dict where the n-th diimension is of type 'type'
    """
    if n<= 1:
        return type()
    return collections.defaultdict(lambda:multi_dimensions(n-1,type)) 
    

### Write out gefx file for edgematrix
def write_gexf_file(matrix,stations):
    fgexf = open('edgematrix.gexf','w')

    gexf = etree.Element("gexf", xmlns="http://www.gexf.net/1.2draft", version="1.2")
    graph = etree.SubElement(gexf,"graph", mode="static", defaultedgetype="directed")
    NODES = etree.SubElement(graph,"nodes")
    EDGES = etree.SubElement(graph,"edges")
    
    count = 0
    tmpdict = {}
    for start in matrix:
    	for end in matrix[start]:
    		edge = etree.SubElement(EDGES,"edge",id=str(count),source=start,target=end,weight=str(math.log(int(matrix[start][end]))))
    		count +=1
    		### Less than ideal, simply write nodes for all keys outside of these nested loops
    		if start not in tmpdict:
				node = etree.SubElement(NODES,"node",id=start,label=str('\"'+stations[start]['name']+'\"'))
				tmpdict[start]=1
                
    fgexf.write( etree.tostring(gexf, pretty_print=True, xml_declaration=True) )
    #print etree.tostring(gexf, pretty_print=True, xml_declaration=True)
    
### Create database
conn = sqlite3.connect('trip_data.db')
conn.execute('''CREATE TABLE nodes (id TEXT UNIQUE, tags TEXT, lat FLOAT, lon FLOAT, endnode_refs INTEGER DEFAULT 1);''')
conn.execute('''CREATE TABLE edges (id TEXT, parent_id TEXT, start_nd TEXT, end_nd TEXT, dist FLOAT, geom TEXT);''')
conn.execute('''CREATE TABLE ways (id TEXT UNIQUE, tags TEXT, nds TEXT);''')

#CREATE TABLE ways (id TEXT UNIQUE, tags TEXT, nds TEXT);
point = ('1','','')
conn.execute('INSERT INTO ways VALUES (?,?,?)', point)

activity = {}
adjmatrix = multi_dimensions(2,dict)

#Stations
stations = multi_dimensions(2,dict)
s = open("stations.csv","rb")
slines = s.readlines()
s.close()
for line in slines[1:]:
	cols = line.split(',')
	stations[cols[0]]['name']=cols[2]
	stations[cols[0]]['status']=cols[1]
	stations[cols[0]]['lat']=cols[6]
	stations[cols[0]]['lng']=cols[7]
	#print cols[6]
	#print cols[0],line

	#CREATE TABLE nodes (id TEXT UNIQUE, tags TEXT, lat FLOAT, lon FLOAT, endnode_refs INTEGER DEFAULT 1);
	npoint = (cols[0],'',stations[cols[0]]['lat'],stations[cols[0]]['lng'],1)
	conn.execute('INSERT INTO nodes VALUES (?,?,?,?,?)', npoint)

#Trips
f = open("trips.csv","rb")
lines = f.readlines()
f.close()

for line in lines[1:]:
	cols = line.split(',')
	tripid = cols[0]
	duration = cols[2]
	start_date = cols[3]
	start_station = cols[4].split("\"")[1]
	end_station = cols[6].split("\"")[1]
	day = start_date.split(" ")[0]+'\"'
	
	if start_station != "" and end_station != "":
		if start_station in adjmatrix and end_station in adjmatrix[start_station]:
			adjmatrix[start_station][end_station] += 1
		else:
			adjmatrix[start_station][end_station] = 1
			#print start_station,end_station
	
	if start_station in stations:
		#CREATE TABLE edges (id TEXT, parent_id TEXT, start_nd TEXT, end_nd TEXT, dist FLOAT, geom TEXT);
		epoint = (tripid,'1',start_station,end_station,duration,'')
		conn.execute('INSERT INTO edges VALUES (?,?,?,?,?,?)', epoint)
	#lse:
	#	print start_station
	
	#if day in activity:
	#	activity[day] += 1
	#else:
	#	activity[day] = 1
	#print duration,start_date

conn.commit()
conn.close()

write_gexf_file(adjmatrix,stations)
	
#for d in sorted(activity.iterkeys()):
#	print d,activity[d]
	
	
	
	
	
	
	