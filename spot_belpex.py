#!/usr/bin/env python3

import requests
import json
import pprint
from flask import Flask

from datetime import datetime
from datetime import timedelta
from pymemcache.client import base
from pymemcache import serde

url = 'https://griddata.elia.be/eliabecontrols.prod/interface/Interconnections/daily/auctionresults/'

cache = base.Client(
    ('127.0.0.1', 11211),
    serde=serde.pickle_serde,
    connect_timeout=0.2,
    timeout=0.2
)

app = Flask(__name__)

@app.route('/')
def index():
    now = datetime.utcnow()

    date_today = now.strftime('%Y-%m-%d')
    date_tommorow = now + timedelta(days=1)
    date_tommorow = date_tommorow.strftime('%Y-%m-%d')

    try:
        cached_data = cache.get(date_today)
    except:
        cached_data=None

    if cached_data is None:
        print("No cache found for today - build cache")
        data_today = requests.get(url=url + date_today)
        try:
            output = data_today.json()
            try:
                print("Setting cache")
                cache.set(date_today, output, 3600)
            except:
                None

        except Exception as e:
            print(e)
            output=[]
    else:
        print("HIT for today")
        output = cached_data

    try:
        cached_data = cache.get(date_tommorow)
    except:
        cached_data=None

    if cached_data is None:
        print("No cache found for tommorow - build cache")
        data_tommorow = requests.get(url=url + date_tommorow)
        try:
            output = output + data_tommorow.json()
            try:
                cache.set(date_tommorow, output, 3600)
            except:
                None
        except Exception as e:
            print(e)
            output=output + []

    else:
        print("HIT for tommorow")
        output = output + cached_data


    rdata=""
    for delta in range(24):
        time_at_delta = now + timedelta(hours=delta)

        rdata=rdata+"hour_{}:".format(delta)
        try:
            current_price=[x for x in output if x['dateTime'] == time_at_delta.strftime('%Y-%m-%dT%H:00:00Z')][0]['price']
        except:
            current_price=0
            
        rdata=rdata+str(current_price)+"\n"

    return rdata

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=81)
