import numpy as np
import datetime as dt
import pandas as pd 

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:////Users/sarahb.delozier/Desktop/BCS/sqlalchemy-challenge/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Base.classes.keys()
measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """ List of all available routes """
    return (
        f"<p>Welcome my Hawaii trip weather API!</p>"
        f"<p>List of Available Routes:</p>"
        f"/api/v1.0/precipitation<br/>Returns a JSON list of precipitation data for the dates between 8/23/16 and 8/23/17<br/><br/>"
        f"/api/v1.0/stations<br/>Returns a JSON list of the weather stations<br/><br/>"
        f"/api/v1.0/tobs<br/>Returns a JSON list of the Temperature Observations (tobs) for the most active station between 8/23/16 and 8/23/17<br/><br/>"
        f"/api/v1.0/<start><br/>Returns a JSON list of min, avg, and max temperature for a given start date<br/><br/>"
        f"/api/v1.0/<start>/<end><br/>Returns a JSON list of min, avg, and max temperature for a given start/end range<br/><br/>"

    )
     

@app.route("/api/v1.0/precipitation")
def annual_precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipitation data for the last year in the database (key:date, value:prcp)"""
    # Query prcp data for all stations
    prcp_results = session.query(measurement.prcp, measurement.date)\
        .filter(measurement.date >= ('2016-08-23'))\
        .filter(measurement.date <= ('2017-08-23'))\
        .order_by(measurement.date).all()
    
    return jsonify(prcp_results)

    session.close()

    # Create a dictionary from the row data and append to a list of prcp_data
    prcp_data = []
    for result in prcp_results:
        x=list(np.ravel(result))
        date_str = dt.datetime.strftime(x,  "%Y-%m-%d")
        prcp_dict={}
        #prcp_dict[date_str] = '{:.4f}'.format(x[0])
        prcp_dict["date"] = result[0]
        prcp_dict["prcp"] = float(result[1])
        prcp_results.append(prcp_dict)

    return jsonify(prcp_data)


@app.route("/api/v1.0/stations")
def stations_list():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperature observations from the previous year for the most active station """
    # Query for all temperature observations from previous year
    results = session.query(measurement.date, measurement.tobs, measurement.station)\
        .group_by(measurement.date)\
        .filter(measurement.date <= ('2017-08-23'))\
        .filter(measurement.date >= ('2016-08-23'))\
        .filter(measurement.station == ('USC00519281')).all()

    session.close()

    tobs_list = list(np.ravel(results))
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of min, avg, max for specific dates"""
    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    if not end:
        results= session.query(*sel).filter(measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)
    
    results = session.query(*sel).filter(measurement.date >= start).filter(measurement.date <= end).all()
    temps2 = list(np.ravel(results))
    return jsonify(temps2)

if __name__ == '__main__':
    app.run()