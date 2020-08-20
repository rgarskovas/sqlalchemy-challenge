import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import pandas as pd
import json

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"                
    )

@app.route("/api/v1.0/precipitation/")
def prcp():
     
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query all dates and precip
    results = session.query(measurement.date, measurement.prcp).all()
    
    session.close()

    weather_data = []

    # create a dictionary for the data    
    for date, prcp in results:
        weather_dict = {}
        weather_dict["date"] = date
        weather_dict["prcp"] = prcp
        weather_data.append(weather_dict)

    # Convert list of tuples into normal list
    DatesPrcp = list(np.ravel(weather_data))

    return jsonify(DatesPrcp)



@app.route("/api/v1.0/stations")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations
    results = session.query(measurement.station).all()
    StationsDF = pd.DataFrame(results,columns = ['stations',])

    # limit to unique stations
    unique_stations = StationsDF["stations"].unique()

    session.close()

    # Convert list of tuples into normal list
    unique_stations = list(np.ravel(unique_stations))

    return jsonify(unique_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query all passengers
    
    # Calculate the date 1 year ago from the last data point in the database

    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    previous_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date > previous_date).all()

    session.close()

    # Convert list of tuples into normal list
    last_year = list(np.ravel(results))

    return jsonify(last_year)



@app.route("/api/v1.0/<start>")
def starting_date(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Create sel function for min, max average
    sel = [func.min(measurement.tobs), 
       func.max(measurement.tobs), 
       func.avg(measurement.tobs),]

    # take variable from input
    start_date = start

    # make the query with filters
    results = session.query(*sel).filter(measurement.date > start_date).all()

    # close the session
    session.close()

    # Convert list of tuples into normal list
    range_results = list(np.ravel(results))
    return jsonify(range_results)


@app.route("/api/v1.0/<start>/<end>")
def date_range(start, end):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Create sel function for min, max average
    sel = [func.min(measurement.tobs),
       func.max(measurement.tobs), 
       func.avg(measurement.tobs),]

    # take variables from input
    start_date = start
    end_date = end

    # make the query with filters
    results = session.query(*sel).filter(measurement.date < end_date).filter(measurement.date > start_date).all()

    # close the session
    session.close()

    # Convert list of tuples into normal list
    range_results = list(np.ravel(results))
    return jsonify(range_results)

if __name__ == '__main__':
    app.run(debug=True)
