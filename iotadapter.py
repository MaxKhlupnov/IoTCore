import os
import logging
import psycopg2
import psycopg2.errors
import datetime as dt
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

verboseLogging = eval(os.environ['VERBOSE_LOG']) ## Convert to bool

if  verboseLogging:
    logger.info('Loading msgHandler function')

def getConnString():
    """
    Extract env variables to connect to DB and return a db string
    Raise an error if the env variables are not set
    :return: string
    """
    db_hostname = os.environ['DB_HOSTNAME']
    db_port =  os.environ['DB_PORT']
    db_name = os.environ['DB_NAME']
    db_user = os.environ['DB_USER']
    db_password = os.environ['DB_PASSWORD']
    db_connection_string = f"host='{db_hostname}' port='{db_port}'  dbname='{db_name}' user='{db_user}' password='{db_password}'  sslmode='require'"
    return db_connection_string
 
def makeInsertStatement(event_json, table_name):

    event = json.loads(event_json)

   # event_datetime = dt.datetime.strftime(event['datetime'])
    insert=  f"""INSERT INTO {table_name} (device_id, event_datetime, latitude, longitude, altitude, 
                    speed, battery_voltage, cabin_temperature, fuel_level) 
                 VALUES('{event['device_id']}', '{event['datetime']}', {event['latitude']}, {event['longitude']}, {event['altitude']}, 
                 {event['speed']}, {event['battery_voltage']},{event['cabin_temperature']},{event['fuel_level']})""".replace('None','NULL')

    return insert

def makeCreateTableStatement(table_name):

    statement = f"""CREATE TABLE public.{table_name} (
	device_id varchar(50) not null,
	event_datetime timestamptz not null,
	latitude float8 null,
	longitude float8 null,
	altitude float8 null,
	speed float8 null,
	battery_voltage float8 null,
	cabin_temperature float8 null,
	fuel_level float8 null
    );"""
    return statement

"""
    Entry-point for Serverless Function.
    :param event: IoT message payload.
    :param context: information about current execution context.
    :return: sucessfull response statusCode: 200
"""
def msgHandler(event, context):
 
    logger.info(event)
    logger.info(context)

    connection_string = getConnString()
    if  verboseLogging:
        logger.info(f'Connecting: {connection_string}')
    conn = psycopg2.connect(connection_string)

    cursor = conn.cursor()
    table_name = 'iot_events'
    sql = makeInsertStatement(event, table_name) ## let's name table 'iot_events'
    if  verboseLogging:     
        logger.info(f'Exec: {sql}')
    try:
        cursor.execute(sql)
    except psycopg2.errors.UndefinedTable as error: ## table not exist - create and repeate insert
        conn.rollback()
        logger.error( error)        
        createTable = makeCreateTableStatement(table_name)
        cursor.execute(createTable)
        conn.commit()
        cursor.execute(sql)
    except Exception as error:
        logger.error( error)
    conn.commit() # <- We MUST commit to reflect the inserted data
    cursor.close()
    conn.close()

    statusCode = 200

    return {
            'statusCode': statusCode
    }

msgHandler("""{"device_id":"areb120kpg2j1kqiq23d","datetime":"05/07/2020 13:09:47","latitude":"55.70329032","longitude":"37.65472196","altitude":"429.13","speed":"0","battery_voltage":"23.5","cabin_temperature":"17","fuel_level":null}""", None)
    