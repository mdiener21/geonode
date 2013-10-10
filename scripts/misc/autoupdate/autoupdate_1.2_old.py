from geonode.core.models import AUTHENTICATED_USERS, ANONYMOUS_USERS
from geonode.maps.models import Map, Layer, MapLayer, Contact, ContactRole, Role, get_csw
from geonode.maps.gs_helpers import fixup_style, cascading_delete, delete_from_postgis
from geonode import geonetwork
import geoserver
from geoserver.resource import FeatureType, Coverage
import base64
from django import forms
from django.contrib.auth import authenticate, get_backends as get_auth_backends
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings
from django.template import RequestContext, loader
from django.utils.translation import ugettext as _
import json
import math
import httplib2
from owslib.csw import CswRecord, namespaces
from owslib.util import nspath
import re
from urllib import urlencode
from urlparse import urlparse
import uuid
import unicodedata
from django.views.decorators.csrf import csrf_exempt, csrf_response_exempt
from django.forms.models import inlineformset_factory
from django.db.models import Q
import logging
import urllib2
import psycopg2 # postgresql
import os, getopt
import sys

logger = logging.getLogger("geonode.maps.autoupdate")

_user, _password = settings.GEOSERVER_CREDENTIALS

DEFAULT_TITLE = ""
DEFAULT_ABSTRACT = ""

autoupdate_url = '/data/autoupdate'

# geoserver setting
host_geoserver = 'golfgis.com'
user_geoserver = 'admin'
pass_geoserver = 'geoserver'
path_geoserver = '/var/geonode-data/styles/'


@login_required
def sync(request):
    autoupdate_url = '/data/autoupdate'
    if request.method == 'GET':
        return render_to_response('maps/autoupdate.html',
                                  RequestContext(request, {"autoupdate_url": autoupdate_url}))
    elif request.method == 'POST':
        #layer_name_src = request.POST.get('layer_name', '') #this field is not used any more !!!
        dbhost = request.POST.get('dbhost', '')
        dbname = request.POST.get('dbname', '')
        dbpass = request.POST.get('dbpass', '')
        dbuser = request.POST.get('dbuser', '')

        if dbhost == '' or dbname == '' or dbpass == '' or dbuser == '':
            return render_to_response('maps/autoupdate.html',
                                      RequestContext(request, {"autoupdate_url": autoupdate_url,
                                                               "error": "All field must be filled!!! "}))
        try:
            conn_src = psycopg2.connect(
                "dbname='" + dbname + "' user='" + dbuser + "' host='" + dbhost + "' password='" + dbpass + "'")
        except:
            return render_to_response('maps/autoupdate.html',
                                      RequestContext(request, {"autoupdate_url": autoupdate_url,
                                                               "error": "Database connection error"}))

        workspace_src = dbname.replace('gis', '')
        store_src = dbname
        addWorkspace2Geoserver(workspace_src) #add workspaces
        addDatastore2Geoserver(store_src, workspace_src, dbhost, dbpass, dbuser)#add datastore

        # get a cursor to execute database statements
        cur_src = conn_src.cursor()
        # fetch all companies
        cur_src.execute("""select tablename from pg_tables where schemaname='geodata';""")
        rows_src = cur_src.fetchall()
        layer_name_src = 'no new layer exist'
        for row in rows_src:
            if row[0] == None:
                #No information is available
                return render_to_response('maps/autoupdate.html',
                                          RequestContext(request, {"autoupdate_url": autoupdate_url,
                                                                   "error": "Database is empty"}))
            else:
                #we have table
                cur_src.execute(
                    "SELECT count(attname) FROM pg_attribute WHERE attrelid = (SELECT oid FROM pg_class WHERE relname = '" +
                    row[0] + "') AND attname = 'geom';")
                ress = cur_src.fetchall()
                res = ress[0]
                con_geom = res[0]
                if con_geom == 1:#is it geometry table ?
                    layer_name_src = row[0]
                    typename_src = workspace_src + ':' + layer_name_src
                    uuid_str = str(uuid.uuid1())
                    la = Layer(workspace=workspace_src, store=store_src, name=layer_name_src, typename=typename_src,
                               storeType='dataStore', uuid=uuid_str)
                    layer_src = Layer.objects.filter(typename=typename_src)
                    if layer_src.count() == 0:
                        addLayer2Geoserver(layer_name_src, workspace_src, store_src)#add layer to geoserver
                        la.save() # add layer to geonode
                        addStyle2Layer(layer_name_src, workspace_src)# add style to layer
                        #break
                        #else :
                        #	return render_to_response('maps/autoupdate.html',
                        #  		RequestContext(request, { "autoupdate_url": autoupdate_url,
                        #					    "error":"layer exist !!!"}))

        cur_src.close()
        latest_layer_list = Layer.objects.all()
        return render_to_response('maps/autoupdate.html',
                                  RequestContext(request, {"autoupdate_url": autoupdate_url,
                                                           "layer_name": layer_name_src,
                                                           "results": latest_layer_list}))


def addLayer2Geoserver(layer_name, workspaces, datastores):
    cmd = "curl -u " + user_geoserver + ":" + pass_geoserver + " -XPOST -H 'Content-type: text/xml' -d '<featureType><name>" + layer_name
    cmd = cmd + "</name></featureType>'   http://" + host_geoserver + "/geoserver"
    cmd = cmd + "/rest/workspaces/" + workspaces + "/datastores/" + datastores + "/featuretypes"
    return os.system(cmd)


def addStyle2Layer(layer_name, workspaces):
    style_name = "golf_" + layer_name
    style_file = style_name + ".sld"
    cmd = "curl -u " + user_geoserver + ":" + pass_geoserver + " -XPUT -H 'Content-type: text/xml' -d '<layer><defaultStyle><name>" + style_name
    cmd = cmd + "</name></defaultStyle><enabled>true</enabled></layer>'   http://" + host_geoserver + "/geoserver"
    cmd = cmd + "/rest/layers/" + workspaces + ":" + layer_name
    if os.path.exists(path_geoserver + style_file):
        return os.system(cmd)
    return -1


def addWorkspace2Geoserver(workspaces):
    cmd = "curl -u " + user_geoserver + ":" + pass_geoserver + " -XPOST -H 'Content-type: text/xml' -d '<workspace><name>" + workspaces
    cmd = cmd + "</name></workspace>'  http://" + host_geoserver + "/geoserver"
    cmd = cmd + "/rest/workspaces/"
    return os.system(cmd)


def addDatastore2Geoserver(datastores_name, workspaces_name, ahost, apass, auser):
    datastorexml = """<dataStore>
                <name>""" + datastores_name + """</name>
                <connectionParameters>
                    <host>""" + ahost + """</host>
                    <port>5432</port>
                    <database>""" + datastores_name + """</database>
                <schema>geodata</schema>
                    <user>""" + auser + """</user>
                <passwd>""" + apass + """</passwd>
                    <dbtype>postgis</dbtype>
                </connectionParameters>
            </dataStore>"""
    cmd = "curl -u " + user_geoserver + ":" + pass_geoserver + " -XPOST -H 'Content-type: text/xml' -d '" + datastorexml
    cmd = cmd + "'  http://" + host_geoserver + "/geoserver"
    cmd = cmd + "/rest/workspaces/" + workspaces_name + "/datastores"
    return os.system(cmd)





