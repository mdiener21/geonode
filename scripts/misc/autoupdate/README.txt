30.08.2013
----------

import_golfgis.py => mein originalscript; nur müsste man immer aus und ein kommentieren, drum hab ich
es aufgeteilt in:

- create_ws_and_ds.py: erstellt für jedes schema in der db golfgis einen eigenen workstore und einen datastore mit den entsprechenden connection parameters
- create_layers.py: sucht sich aus der db golfgis (�ber psycopg2) alle namen der tabellen und erstellt mit hilfe der funktion addlayers2geoserver in einer schleife alle layers aus der db golfgis


Sind allerdings beide hardcodiert (sorry, meine python kenntnisse sind ziemlich m��ig...)!

ACHTUNG bei create_layers.py => da in allen sechs schemas tabellen vorkommen, welche den selben Namen haben,
sollte der layername noch ver�ndert werden (zb. ds + layername); bei mir hat das allerdings grad nicht mehr funktioniert
drum hab ich�s so gelassen! F�r geoserver ist es eh kein problem, weil unterschiedliche ds und ws,
aber "python manage.py updatelayers" erstellt bei namensgleichheit keinen neuen layer, sonder macht nur ein "update".
