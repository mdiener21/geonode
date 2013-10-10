#!/home/mdiener/.venvs/geonde/bin python
import os
import psycopg2 # for postgres
from geoserver.catalog import Catalog
#from geonode.maps.models import Layer
from geonode.layers.models import Layer
import uuid

from geonode.layers.models import Layer

# user and pwd
user = "admin"
pwd = "geoserver"
cat = Catalog("http://localhost:8080/geoserver/rest", user, pwd)

prefix_db_schema = "golfgis_"
prefix_workspace = "ws_"
prefix_datastore = "ds_"
prefix_uri = r"http://golfgis.com/"

golfclubs_list = ["zurich", "breitenloo", "seltenheim", "moosburg", "koestenberg", "thalersee"]

# more geoserver settings (needed for cURL)
host_geoserver = 'localhost'
user_geoserver = 'admin'
pass_geoserver = 'geoserver'
path_geoserver = '/var/geonode-data/styles/'
geoserver_url = "http://localhost:8080/geoserver/rest/workspaces/"

#curl -u admin:geoserver -v -XPOST -H 'Content-Type:text/xml' -d '<featureType><name>green</name></featureType>' http://localhost:8080/geoserver/rest/workspaces/ws_zurich/datastores/ds_zurich/featuretypes;

# function to add layers to geoserver
def addLayer2Geoserver(layer_name, workspace_name, datastore_name):
    curlstring = "curl -u " + user_geoserver + ":" + pass_geoserver + \
                 " -v -XPOST -H 'Content-type: text/xml' -d '<featureType><name>" + \
                 layer_name + "</name></featureType>' http://localhost:8080/geoserver/rest/workspaces/" + \
                 workspace_name + "/datastores/" + datastore_name + "/featuretypes;"
    return os.system(curlstring)
    print "\n processing layer " + layer_name + "\n curlstring call is: "+ curlstring

# need connection to db
conn = psycopg2.connect("dbname=golfgis user=geonode host=localhost password=geonode port=5433")

#test is addLayer working yes
#addLayer2Geoserver("green", "ws_zurich","ds_zurich")

for golfclub in golfclubs_list:
    # get db and table names
    cur = conn.cursor()


    #fetch all table names fron one golfgis_schema
    #cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = '" + prefix_db_schema + golfclub + "'")
    cur.execute("SELECT f_table_name FROM geometry_columns where f_table_schema = '" + prefix_db_schema + golfclub + "'")

    # get all table names
    all_golfgis_tables = cur.fetchall()
    layer_name_new = 'now new layer exists'
    print("all tables area: " + str(all_golfgis_tables))
    for table in all_golfgis_tables:
        print ("first table name is: " + str(table))
        cur.execute("SELECT relnamespace  FROM pg_class WHERE relname = 'bunker';") # returns a list of all dbschemas
        db_schemas_all = cur.fetchall()

        for rel_id in db_schemas_all:
            cur.execute("SELECT count(attname) FROM pg_attribute WHERE attrelid = (SELECT oid FROM pg_class WHERE relname = '" + rel_id[0] + "') AND attname = 'geom';")
            print("we execute here and made the select query")

            ress = cur.fetchall()
            print("result ress : " + str(ress[0]))

            res = ress[0]
            con_geom = res[0]
            print("con_geom is it 0 : " + str(con_geom))

           # if con_geom == 1:

            layer_name_src = rel_id[0]
            typename_src = workspace_name + ':' + layer_name_src
            uuid_str = str(uuid.uuid1())
            la = Layer(workspace=workspace_name, store=datastore_name, name=layer_name_src, typename=typename_src,
                       storeType='dataStore', uuid=uuid_str)
            layer_src = Layer.objects.filter(typename=typename_src)
            if layer_src.count() == 0:
                addLayer2Geoserver(str(layer_name_src), workspace_name, datastore_name)#add layer to geoserver
                la.save() # add layer to geonode
                print("we save to geoserver: " + str(layer_name_src))
            #else:
            #    print("con_geom is null or 0")




#  curl -u mdiener:Gis2012mrdSnlw -v -XPOST -H 'Content-Type:text/xml' -d '<featureType><name>' + layer_name + ' \
#   </name></featureType>' http://localhost:8080/geoserver/rest/workspaces/' + workspace + ' \
#   /datastores/' + datastore + '/featuretypes


# add layers to geondode
# python manage.py updatelayers #do this as root! # i did this in the terminal!

# ATTENTION: be aware of duplicate layers => change layer_name to individual name!
