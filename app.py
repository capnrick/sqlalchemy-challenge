from flask import Flask, jsonify



import numpy as np
import pandas as pd
import datetime as dt
from pprint import pprint

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect



#Setting up access to the database
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#reflect the database
Base=automap_base()
#reflect the tables
Base.prepare(engine, reflect=True)

#saving references to tables
Measurement=Base.classes.measurement
Station=Base.classes.station


#setting up Flask
app = Flask(__name__)



#Flask Routes
@app.route("/")
def home():
        print("Server received request for 'Home' page...")
        return (
                f"Welcome to the SQLAlchemy API Homepage!<br/><br/>"
                f"Available routes:<br/>"
                f"/api/v1.0/precipitation<br/>"
                f"/api/v1.0/stations<br/>"
                f"/api/v1.0/tobs<br>"
                f"/api/v1.0/start-date<br/>"
                f"/api/v1.0/start-date/end-date<br/>"
                f"start and end dates should be in YYYY-MM-DD format, e.g. /api/v1.0/2016-11-30/2017-01-22"

        )

        
#Convert the query results to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.


@app.route("/api/v1.0/precipitation")
def precipitation():
        session = Session(engine)
        results=session.query(Measurement.date, Measurement.prcp).all()
        session.close()

        precip_dict={}

        for date, prcp in results:
                precip_dict[date]=prcp

        return jsonify(precip_dict)        
        


# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
        session = Session(engine)
        station_data=[Station.id,Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
        results = session.query(*station_data).all()
        session.close() 
        
        stations=[]
               
        for sindex,station, name, lat, lon,el in results:
                station_list={}
                station_list["Station ID"]=sindex
                station_list["station"]=station
                station_list["Name"] = name    
                station_list["Latitude"]=lat              
                station_list["Longitude"]=lon             
                station_list["Elevation"]=el
                stations.append(station_list)
       
        return jsonify(stations)
            


# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
        session = Session(engine)


        #code from climate_starter.ipynb used here        
        #finding most recent date in data set
        most_recent=session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
        dt_most_recent= dt.datetime.strptime(most_recent, "%Y-%m-%d")
        # Calculate the date one year from the last date in data set.
        dt_first_date=dt_most_recent-dt.timedelta(days=365)
        dt_first_date

        #query to find most active stations
        ma_stations=session.query(Measurement.station, Station.name, func.count(Measurement.id)).filter(Measurement.station == Station.station).group_by (Measurement.station).order_by(func.count(Measurement.id).desc()).all()
              
        #combining last two steps to find most active stations in most recent 12 months
        active_stations=session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > dt_first_date).filter(Measurement.station == ma_stations[0][0]).order_by(Measurement.date).all()

        session.close()

        
        #store data into list and jsonify
        tobs_api = []
        for date, tobs in active_stations:
                tobs_list = {}
                tobs_list["Date"] = date
                tobs_list["Temp"] = tobs
                tobs_api.append(tobs_list)

                
        return jsonify(tobs_api)
        
        
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.        
@app.route("/api/v1.0/<start>")
def temp_data_start(start):
        
        session = Session(engine)
        queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
        session.close()

        tobs_api = []
        for min,avg,max in queryresult:
                tobs_list = {}
                tobs_list["Min"] = min
                tobs_list["Average"] = avg
                tobs_list["Max"] = max
                tobs_api.append(tobs_list)

        return jsonify(tobs_api)



# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def temp_data_start_end(start,end):
        
        session = Session(engine)
        queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
        session.close()

        tobs_api = []
        for min,avg,max in queryresult:
                tobs_list = {}
                tobs_list["Min"] = min
                tobs_list["Average"] = avg
                tobs_list["Max"] = max
                tobs_api.append(tobs_list)

        return jsonify(tobs_api)

if __name__ == "__main__":
    app.run(debug=True)