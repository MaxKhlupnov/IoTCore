import os
import logging
import psycopg2
import psycopg2.errors
import datetime as dt
import json
import base64

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

def num(s):  
    try:
        s.replace(',','.')
        return  "{:10.4f}".format(float(s))
    except (AttributeError, ValueError):
        return "NULL"

def makeInsertStatement(event_id, enqueue_datetime, payload_json, table_name):

    event = json.loads(payload_json)

   # event_datetime = dt.datetime.strftime(event['datetime'])
    insert=  f"""INSERT INTO {table_name} (event_id, device_id, enqueue_datetime, event_datetime, processed_datetime, 
                 latitude, longitude, altitude, speed, battery_voltage, cabin_temperature, fuel_level) 
                 VALUES('{event_id}','{event['device_id']}', '{enqueue_datetime}','{event['datetime']}', CURRENT_TIMESTAMP,
                 {event['latitude']}, {event['longitude']}, {event['altitude']}, 
                 {num(event['speed'])}, {num(event['battery_voltage'])},
                 {num(event['cabin_temperature'])},{num(event['fuel_level'])})"""

    return insert

def makeCreateTableStatement(table_name):

    statement = f"""CREATE TABLE public.{table_name} (
    event_id varchar(24) not null,
	device_id varchar(50) not null,
    enqueue_datetime timestamptz not null,
	event_datetime timestamptz not null,
    processed_datetime  timestamptz not null,
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
    statusCode = 500 ## Error response by default
    logger.info(event)
    logger.info(context)

    connection_string = getConnString()
    if  verboseLogging:
        logger.info(f'Connecting: {connection_string}')
    conn = psycopg2.connect(connection_string)

    cursor = conn.cursor()
    json_msg = json.loads(event)
    payload = base64.b64decode(json_msg["messages"][0]["details"]["payload"])
    event_id = json_msg["messages"][0]["event_metadata"]["event_id"]
    enqueue_time = json_msg["messages"][0]["event_metadata"]["created_at"]

    table_name = 'iot_events'
    sql = makeInsertStatement(event_id, enqueue_time, payload, table_name) ## let's name table 'iot_events'
    if  verboseLogging:     
        logger.info(f'Exec: {sql}')
    try:
        cursor.execute(sql)
        statusCode = 200
    except psycopg2.errors.UndefinedTable as error: ## table not exist - create and repeate insert
        conn.rollback()
        logger.error( error)        
        createTable = makeCreateTableStatement(table_name)
        cursor.execute(createTable)
        conn.commit()
        cursor.execute(sql)
        statusCode = 200
    except Exception as error:
        logger.error( error)
    conn.commit() # <- We MUST commit to reflect the inserted data
    cursor.close()
    conn.close()

    

    return {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'isBase64Encoded': False
    }
''''
#### PAYLOAD EXAMPLE FOR LOCAL DEBUGGING ### 
msgHandler("""{
	"messages": [
		{
			"event_metadata": {
				"event_id": "160d239876d9714800",
				"event_type": "yandex.cloud.events.iot.IoTMessage",
				"created_at": "2020-05-08T19:16:21.267616072Z",
				"folder_id": "b1gvp43cei68d5sfhsu7"
			},
			"details": {
				"registry_id": "areba24s6jn8lrc0d5pa",
				"device_id": "areb120kpg2j1kqiq23d",
				"mqtt_topic": "$devices/areb120kpg2j1kqiq23d/events",
				"payload": "eyJkZXZpY2VfaWQiOiJhcmViMTIwa3BnMmoxa3FpcTIzZCIsImRhdGV0aW1lIjoiMDUvMDgvMjAyMCAyMjoxNjoyMSIsImxhdGl0dWRlIjoiNTUuNzAzMjkwMzIiLCJsb25naXR1ZGUiOiIzNy42NTQ3MjE5NiIsImFsdGl0dWRlIjoiNDI5LjEzIiwic3BlZWQiOiIwIiwiYmF0dGVyeV92b2x0YWdlIjoiMjMsNSIsImNhYmluX3RlbXBlcmF0dXJlIjoiMTciLCJmdWVsX2xldmVsIjpudWxsfQ=="
			}
		}
	]
}""", None)
'''
    