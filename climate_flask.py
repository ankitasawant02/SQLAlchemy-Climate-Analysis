
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

#########################################################
# DATABASE SETUP
#########################################################

engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#########################################################
# FLASK SETUP
#########################################################

app = Flask(__name__)

#########################################################
# FLASK ROUTES
#########################################################

@app.route("/")
def welcome():
    """List all available API routes."""   
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def percipitation():
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    # Calculate the date 1 year ago from the last data point in the database

    # last_data_point = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago = dt.date(2017,8,23) - dt.timedelta(days= 365)

    prcp_year = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= year_ago, Measurement.prcp!= None).\
    order_by(Measurement.date).all()

    # date_prcp = []

    # for dtprcp in prcp_year:
    #     dtprcp_dict = {}
    #     dtprcp_dict["date"]= dtprcp.date
    #     dtprcp_dict["prcp"]= dtprcp.prcp
    #     date_prcp.append(dtprcp_dict)

    return jsonify(dict(prcp_year))

@app.route("/api/v1.0/stations")
def stations():
    # Design a query to show how many stations are available in this dataset?
    session.query(Measurement.station).distinct().count()

    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    # act_sta = []
    # for st_dict in active_stations:
    #     stat_dict= {}
    #     stat_dict["station"] = st_dict.station
    #     act_sta.append(stat_dict)

    return jsonify(dict(active_stations))

@app.route("/api/v1.0/tobs")
def tobs():

    year_ago = dt.date(2017,8,23) - dt.timedelta(days= 365)
    year_temp = session.query(Measurement.tobs).filter(Measurement.date >= year_ago, Measurement.station == 'USC00519281').\
    order_by(Measurement.tobs).all()

    yr_temp = []
    for y_t in year_temp:
        yrtemp = {}
        yrtemp["tobs"]= y_t.tobs
        yr_temp.append(yrtemp)

    return jsonify(yr_temp)


def calc_start_temps(start_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start_date).all() 

@app.route("/api/v1.0/<start>")
def start_date(start):
    
    calc_start_temp = calc_start_temps(start)
    t_temp= list(np.ravel(calc_start_temp))

    tmin = t_temp[0]
    tmax = t_temp[2]
    tavg = t_temp[1]
    tdict = {'Minimum temperature': tmin, 'Maximum temperature': tmax, 'Avg temperature': tavg}

    return jsonify(tdict)

def calc_start_end_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    Args:
    start_date (string): A date string in the format %Y-%m-%d
    end_date (string): A date string in the format %Y-%m-%d
    Returns:
    TMIN, TAVE, and TMAX
    """
    return session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
    filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    
    calc_start_end_temp = calc_start_end_temps(start, end)
    t_temp1= list(np.ravel(calc_start_end_temp))

    temp_min = t_temp1[0]
    temp_max = t_temp1[2]
    temp_avg = t_temp1[1]
    temp_dict = { 'Minimum temperature': temp_min, 'Maximum temperature': temp_max, 'Avg temperature': temp_avg}

    return jsonify(temp_dict)



if __name__ == '__main__':
    app.run(debug=True)
