# Imports
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from datetime import date
import pandas as pd
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

def first_date():
    session = Session(engine)

    # Find the most recent date in the data set.
    recent_date = session.query(func.max(Measurement.date)).first()[0]

    date = dt.date.fromisoformat(recent_date)
    
    session.close()

    return(date)

def prev_year():
    session = Session(engine)

    # Calculate the date one year from the last date in data set.
    year_ago = first_date() - dt.timedelta(days=365)

    session.close()

    return(year_ago)

@app.route("/")
def index():
    """List all available api routes."""
    return ("""
        <title>Surf's Up!</title>
        <h1>Welcome to the Climate API!<br/></h1>
        <h2>Available Routes:<br/></h2>
        <strong>Precipitation results:</strong> /api/v1.0/precipitation<br/>
        <strong>Stations results:</strong> /api/v1.0/stations<br/>
        <strong>Temperature observations (past 12 months):</strong> /api/v1.0/tobs<br/><br/>
        <strong>For a range of dates (replace date in yyyy-mm-dd format):</strong><br/>
        <strong>Just a start date:</strong> /api/v1.0/&ltstart&gt<br/>
        <strong>A start and end date:</strong> /api/v1.0/&ltstart&gt/&ltend&gt<br/>
    """)

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation results of last 12 months"""
    # Query all precipitation results
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date <= first_date()).\
        filter(Measurement.date >= prev_year()).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_prec
    all_prec = []
    for date, prcp in results:
        prec_dict = {}
        prec_dict["date"] = date
        prec_dict["prcp"] = prcp
        all_prec.append(prec_dict)

    return jsonify(all_prec)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations
    stations = session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for id, station, name, latitude, longitude, elevation in stations:
        station_dict = {}
        station_dict["id"] = id
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        all_stations.append(station_dict)

    return jsonify(all_stations)
    
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of data for most active station"""
    # Query last 12 months temps
    temp_12_months = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date >= prev_year()).all()
    
    session.close()

    # Create a dictionary from the row data and append to a list of all_tobs
    all_tobs = []
    for date, tobs in temp_12_months:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def startend(start=None, end=None):
    """Fetch the minimum temperature, the average temperature, and the maximum temperature for a specified start range, or a 404 if not."""
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # If statement for if an end date is specified
    if end == None:

        # Query from date onwards
        start_date = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
        
        # Create a dictionary from the row data and append to a list
        start_list = []
        for min, avg, max in start_date:
            start_dict = {}
            start_dict["min"] = min
            start_dict["avg"] = avg
            start_dict["max"] = max
            start_list.append(start_dict)
        
        session.close()

        return jsonify(start_list)
    
    # If the end date was specified
    else: 
        
        # Query date range
        start_end_dates = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
        
        # Create a dictionary from the row data and append to a list
        start_end_list = []
        for min, avg, max in start_end_dates:
            start_end_dict = {}
            start_end_dict["min"] = min
            start_end_dict["avg"] = avg
            start_end_dict["max"] = max
            start_end_list.append(start_end_dict)

        session.close()

        return jsonify(start_end_list)

# Define main behaviour
if __name__ == "__main__":
    app.run(debug=True)