import json

import bart_api.bart_api as bart_api
import flask
app = flask.Flask(__name__)

@app.route('/')
def index():
    return """<html><body>
<li><a href="http://flag.is9.co/traintime/next_trains/CIVC/WCRK">Go Home</a>
<li><a href="http://flag.is9.co/traintime/next_trains/WCRK/CIVC">Go Work</a>
</body></html>"""


@app.route('/next_trains/<start>/<end>')
def next_trains(start, end):
    bart = bart_api.BartApi()
    status = bart.system_status()
    departures, prev_station, next_station = bart.get_departures(start.upper(), end.upper())
    return flask.render_template('app.html', trains=departures, 
        start=start.upper(), 
        end=end.upper(), prev_station=prev_station, 
        next_station=next_station, status=status)



if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
