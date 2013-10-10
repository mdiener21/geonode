#!/home/mdiener/.venvs/geonde/bin python
import os
import psycopg2 # for postgres
from geoserver.catalog import Catalog

os.system("curl --head www.google.com")

# user and pwd
user = "admin"
pwd = "geoserver"
cat = Catalog("http://localhost:8080/geoserver/rest", user, pwd)

# more geoserver settings (needed for cURL)
host_geoserver = 'localhost'
user_geoserver = 'admin'
pass_geoserver = 'geoserver'
path_geoserver = '/var/geonode-data/styles/'

# schemas to be uploaded to geosever
name_schema = ["golfgis_zurich", "golfgis_breitenloo", "golfgis_seltenheim", "golfgis_moosburg", "golfgis_koestenberg",
               "golfgis_thalersee"]
count = len(name_schema)

# uris
name_uri = ["http://example1.com", "http://example2.com", "http://example3.com", "http://example4.com",
            "http://example5.com", "http://example6.com"]

# create workspaces => uncomment if you need to create the workspace first!
#for run in range(count):
#ws = cat.create_workspace(name_schema[run],name_uri[run])

# get workspace and create datastore!
for run in range(count):
    # get workspace
    ws = cat.get_workspace(name_schema[run])

    # create datastore
    #ds = cat.create_datastore(name_schema[run],ws)

    ds = cat.get_store(name_schema[run], ws)

    # add connection parameters
    ds.connection_parameters.update(
        host="localhost",
        port="5432",
        database="golfgis",
        user="postgres",
        passwd="DHM1808co",
        schema=name_schema[run],
        dbtype="postgis")

    # save the datastore
    cat.save(ds)

######################## now the layers have to be added! ######################################

# function to add layers to geoserver
def addLayer2Geoserver(layer_name, workspaces, datastores):
    cmd = "curl -u " + user_geoserver + ":" + pass_geoserver + " -XPOST -H 'Content-type: text/xml' -d '<featureType><name>" + layer_name
    cmd = cmd + "</name></featureType>'   http://" + host_geoserver + "/geoserver"
    cmd = cmd + "/rest/workspaces/" + workspaces + "/datastores/" + datastores + "/featuretypes"
    return os.system(cmd)

# need connection to db
conn = psycopg2.connect("dbname=golfgis user=postgres host=localhost password=DHM1808co")
count = 5 # count of schemas to be loaded

for run in range(count):

    # get db and table names
    cur = conn.cursor()

    if run == 0:
        cur.execute("""select tablename from pg_tables where schemaname='golfgis_breitenloo';""")
        ws_name = 'golfgis_breitenloo'
        ds_name = ws_name
    elif run == 1:
        cur.execute("""select tablename from pg_tables where schemaname='golfgis_seltenheim';""")
        ws_name = 'golfgis_seltenheim'
        ds_name = ws_name
    elif run == 2:
        cur.execute("""select tablename from pg_tables where schemaname='golfgis_zurich';""")
        ws_name = 'golfgis_zurich'
        ds_name = ws_name
    elif run == 3:
        cur.execute("""select tablename from pg_tables where schemaname='golfgis_moosburg';""")
        ws_name = 'golfgis_moosburg'
        ds_name = ws_name
    elif run == 4:
        cur.execute("""select tablename from pg_tables where schemaname='golfgis_koestenberg';""")
        ws_name = 'golfgis_koestenberg'
        ds_name = ws_name
    elif run == 5:
        cur.execute("""select tablename from pg_tables where schemaname='golfgis_thalersee';""")
        ws_name = 'golfgis_thalersee'
        ds_name = ws_name
    else:
        print("OBS: something went wrong!")

    # get all table names
    rows = cur.fetchall()

    for row in rows:
        layer_name = row[0]                    # get name out of tuple
        print(layer_name)                    # control
        addLayer2Geoserver(layer_name, ws_name, ds_name)        # add layer to geoserver

# add layers to geondode
# updatelayers --settings=geonode.settings #do this as root!

