SELECT attname FROM pg_attribute 
WHERE attrelid = (SELECT oid FROM pg_class WHERE relname = 'green' and relnamespace = 21301)
AND attname = 'geom';

SELECT relname, relnamespace  FROM pg_class WHERE relname = 'bunker';
SELECT relnamespace  FROM pg_class WHERE relname = 'bunker';

select nspname from pg_catalog.pg_namespace where nspname like 'golf%';

SELECT tablename FROM pg_tables WHERE schemaname = 'golfgis_zurich' and ;
SELECT f_table_schema, f_table_name FROM geometry_columns where f_table_schema = 'golfgis_zurich' order by f_table_name;

SELECT f_table_name FROM geometry_columns where f_table_schema = 'golfgis_zurich' order by f_table_name;