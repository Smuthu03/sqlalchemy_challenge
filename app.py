# Import the dependencies.

import numpy as np
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify, request, url_for
from sqlalchemy.sql import func
#from flask_restful import Api, Resource
#from flask_sqlalchemy import SQLAlchemy


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)
Base.classes.keys()
# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# HomePage with list of  homepage with list all the available routes.

@app.route("/")
def homepage():
    """List all the available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

# app route to retrieving the last 12 months of data presipitation data

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return last 12 months of precipitation data"""
    # Query precepitation last 12 months
    recent_dt = session.query(Measurement.date).order_by((Measurement.date.desc())).first().date

    mnths_bfr = dt.datetime.strptime(recent_dt, '%Y-%m-%d') - dt.timedelta(days=365)
    
    results = session.query(Measurement.date, Measurement.prcp).order_by((Measurement.date.desc())).\
	          filter(Measurement.date > mnths_bfr).all()
  	
	# Convert list of tuples into normal list
    lst_pst_yr = list(np.ravel(results))

    return jsonify(lst_pst_yr)
	
session.close()

# app route for stations summary and count and ordered from large to small

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""
    
	# Query station list
    
    activ_stn = session.query(Measurement.station,func.count(Measurement.station)).\
                order_by(func.count(Measurement.station).desc()).\
                group_by(Measurement.station)
    
    all_station = []
    
    for record in activ_stn:
        stn_dict = {}
        stn_dict["station"] = record[0]
        stn_dict["numstn"] =  record[1]
        all_station.append(stn_dict)
    return jsonify(all_station)
    
session.close()
	
# app route to retrieving the last 12 months of temparature data for the most frequent station USC00519281
	
@app.route("/api/v1.0/tobs")
def tobs():

    tobs_for_mnts = session.query(Measurement.date, Measurement.tobs).\
			    filter(Measurement.station == 'USC00519281').\
			    filter(Measurement.date > '2016-08-18').\
			    filter(Measurement.date <= '2017-08-18').all()
    
    # Convert list of tuples into normal list
    tobs_mnts = list(np.ravel(tobs_for_mnts))
    
    return jsonify(tobs_mnts)

session.close()

# app route that takes date input for start date to display the min, max and avg temp for timeframe after a given day
# for start date input date in YYYY-MM-DD format please do not add string in the url just the year-month-day e.g 2016-08-23

@app.route('/api/v1.0/<start>')	
def reqstrtdt(start):
    
    start = dt.datetime.strptime(start, '%Y-%m-%d').date()

    tobs_agg = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
               filter(Measurement.date >= start).all()
    
    tobs_agg = list(np.ravel(tobs_agg))

    return jsonify(tobs_agg)

session.close()

# app route that takes date input for start date and end date to display the min, max and avg temp for timeframe between the the two dates
# for start date and end date, input date in YYYY-MM-DD format, separate by /. Please do not add string in the url just the year-month-day e.g 2016-08-30/2017-05-01

@app.route('/api/v1.0/<start>/<end>')
def reqstrtenddt(start, end):
    start = dt.datetime.strptime(start, '%Y-%m-%d').date()
    end = dt.datetime.strptime(end, '%Y-%m-%d').date()
    
    tobs_agg1 = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
               filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    tobs_agg1 = list(np.ravel(tobs_agg1))
    return jsonify(tobs_agg1)

session.close()		

if __name__ == '__main__':
    app.run(debug=True)

