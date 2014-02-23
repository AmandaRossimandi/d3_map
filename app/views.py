'''Views'''
from datetime import datetime
import tempfile
from flask import Flask, request, session, g, redirect, url_for, \
      render_template, flash
from app import app
import pandas as pd
import influxdb_flow as idb
from random import shuffle
import logging

def refresh_data():
    print 'GETTING DATA'
    client = idb.influx_init()
    logging.info('Query influx')
    data = idb.query_influx(client, 'select latitude, longitude, pageviews \
    from aggregated_user_data where time > now() - 2h;')
    print data
    print 'EXPANDING DATA'
    exp_data = pd.DataFrame(columns=['latitude', 'longitude'])
    if len(data) > 0:
        for i in range(len(data)):
            rows = int(data.loc[i].pageviews)
            latitude = data.loc[i].latitude
            longitude = data.loc[i].longitude
            for rows in range(rows):
                exp_data = exp_data.append({'latitude':latitude, 'longitude':longitude}, ignore_index=True)

        rand_index = list(exp_data.index)
        shuffle(rand_index)
        exp_data.reindex(rand_index)
    data_file = tempfile.NamedTemporaryFile(suffix='.csv', dir='./app/static', delete=False)
    data_file.name = './app/static/data.csv'
    exp_data.to_csv(data_file.name)
    data_file.flush()
    return data_file.name

@app.route('/')
def index():
    print "RELOAD: {}".format(datetime.now().strftime('%Y/%m/%d/ %H-%M-%S'))
    filename = refresh_data()
    logging.info('Rendering')
    print filename
    print 'RENDERING'
    return render_template('map.html', filename=filename)

