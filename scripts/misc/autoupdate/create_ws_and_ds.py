#!/home/mdiener/.venvs/geonde/bin python
import os
from geoserver.catalog import Catalog

# user and pwd
user = "admin"
pwd = "geoserver"
cat = Catalog("http://localhost:8080/geoserver/rest", user, pwd)


prefix_db_schema = "golfgis_"
prefix_workspace = "ws_"
prefix_datastore = "ds_"
prefix_uri = r"http://golfgis.com/"

list_golfclubs = ["zurich", "breitenloo", "seltenheim", "moosburg", "koestenberg", "thalersee"]

# create workspaces => uncomment if you need to create the workspace first!
for golfclub in list_golfclubs:
    ws = cat.create_workspace(prefix_workspace + golfclub, prefix_uri + golfclub) # here we concatenate the names together with +
    print "creating workspace: " + prefix_workspace + golfclub

# # get workspace and create datastore
for golfclub in list_golfclubs:
    # get workspace
    ws = cat.get_workspace(prefix_workspace + golfclub)

    # create datastore
    ds = cat.create_datastore(prefix_datastore + golfclub, ws)

    # add connection parameters
    ds.connection_parameters.update(
        host="localhost",
        port="5433",
        database="golfgis",
        user="geonode",
        passwd="geonode", # change pwd
        schema=prefix_db_schema + golfclub,
        dbtype="postgis")

    # save the datastore
    print "creating datastore: " + prefix_datastore + golfclub
    cat.save(ds)

