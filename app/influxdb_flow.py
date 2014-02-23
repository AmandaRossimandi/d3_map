import json
import os
import time
from datetime import datetime
import base64
import pandas as pd
import numpy as np
import logging

from influxdb import InfluxDBClient

INFLUX_LOGIN = base64.b64decode(os.environ.get('GA_INFLUX_LOGIN'))
INFLUX_LOGIN = json.loads(INFLUX_LOGIN)

def save_to_influxdb(client, df, table):
    logging.info('Formatting data')
    data = data_to_influx_body(df, table)
    logging.info('Pushing data to Influx')
    client.write_points_with_precision(data, 's')

def influx_init():
    client = InfluxDBClient(**INFLUX_LOGIN)
    return client


def data_to_influx_body(df,table):
    '''Takes a list of points (lists), table name and column list'''

    points = [list(df.iloc[i, :]) for i in range(len(df))]
    data = [{"points": points, "name": table, "columns": list(df.columns)}]
    return data


def query_influx(client, query, parse_time=False):
    try:
        data = client.query(query)
        data_series = np.array(data[0]['points'])
        df = pd.DataFrame(data=data_series, columns=data[0]['columns'])
        if parse_time:
            df.time = df.time.apply(lambda d: datetime.fromtimestamp(float(d)))
            df.sort(columns='time', inplace=True)
        df.reset_index(drop=True, inplace=True)
    except:
        df = pd.DataFrame(columns=['time', 'data'])
    return df
