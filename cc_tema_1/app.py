import json

import prometheus_client

from config import *
import requests
from flask import Flask, Response, render_template
from helpers.middleware import setup_metrics
import logging
import random

app = Flask(__name__)
setup_metrics(app)

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('test.log', 'w', 'utf-8')
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'))
root_logger.addHandler(handler)


@app.route('/use/<country_text>')
def country_event(country_text):
    r = requests.get('https://restcountries.eu/rest/v2/name/' + country_text)
    jsonObj = json.loads(r.text)
    app.logger.info(
        "Raspunsul dat de restcountries are latenta " + str(r.elapsed.total_seconds()) + " secunde si este: " + r.text)

    if type(jsonObj) is list:
        country = jsonObj[0]['name']
        if len(jsonObj[0]['latlng']) < 2:
            r = requests.get(
                'https://nominatim.openstreetmap.org/search.php?q=' + country.split(' ')[0] + '&format=json')

            app.logger.info(
                "Raspunsul dat de nominatim.openstreetmap.org are latenta " + str(
                    r.elapsed.total_seconds()) + " secunde si este: " + r.text)

            jsonObj = json.loads(r.text)
            if len(jsonObj) == 0:
                return render_template('NoCountry.html')
            lat = jsonObj[0]['lat']
            lon = jsonObj[0]['lon']

        else:
            lat = jsonObj[0]['latlng'][0]
            lon = jsonObj[0]['latlng'][1]
    else:
        return render_template('NoCountry.html')

    payload = {
        "jsonrpc": "2.0",
        "method": "generateIntegers",
        "params": {
            "apiKey": get_random_key(),
            "n": 1,
            "min": 1,
            "max": 100
        },
        "id": 1
    }
    r = requests.post('https://api.random.org/json-rpc/2/invoke', json=payload)

    number = r.json()['result']['random']['data'][0] if r.status_code != 403 else random.randint(1, 100)
    app.logger.info(
        "Raspunsul dat de random.org are latenta " + str(r.elapsed.total_seconds()) + " secunde si este: " + r.text)

    meetUpHeaders = {
        'Authorization': get_meetup_key(),
        'Content-Type': 'application/json'
    }

    r = requests.get(
        'https://api.meetup.com/find/upcoming_events?&page=' + str(number) + '&text=' + country + '&lon=' + str(
            lon) + '&lat=' + str(lat),
        headers=meetUpHeaders)
    app.logger.info(
        "Raspunsul dat de meetup are latenta " + str(r.elapsed.total_seconds()) + " secunde si este: " + r.text)

    jsonObj = json.loads(r.text)
    links = [event['link'] for event in jsonObj["events"]] if "events" in jsonObj.keys() else []
    return render_template('CountryFound.html', country=country, links=links)


@app.route('/metrics/')
def metrics():
    return Response(prometheus_client.generate_latest(), mimetype=str('text/plain; version=0.0.4; charset=utf-8'))


if __name__ == '__main__':
    app.run()
