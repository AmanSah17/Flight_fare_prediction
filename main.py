from flask import Flask, request, render_template
from flask_cors import cross_origin
import pickle
import pandas as pd

app = Flask(__name__)
model = pickle.load(open("fare_prediction.pkl", "rb"))

@app.route("/about")
def about():
    return render_template("aboutus.html")

@app.route("/")
@cross_origin()
def home():
    return render_template("home.html")

def parse_date_time(date_time_str):
    dt = pd.to_datetime(date_time_str, format="%Y-%m-%dT%H:%M")
    return dt.day, dt.month, dt.hour, dt.minute

def airline_mapping(airline):
    # Create a dictionary to map airlines to corresponding values
    airline_map = {
        'Jet Airways': 1,
        'IndiGo': 2,
        'Air India': 3,
        # ... Add other airlines
    }
    return airline_map.get(airline, 0)  # Default to 0 if not found

def source_destination_mapping(location, location_map):
    # Create a dictionary to map locations to corresponding values
    return location_map.get(location, [0, 0, 0, 0])

@app.route("/predict", methods=["GET", "POST"])
@cross_origin()
def predict():
    if request.method == "POST":
        Journey_day, Journey_month, Dep_hour, Dep_min = parse_date_time(request.form["Dep_Time"])
        Arrival_hour, Arrival_min = parse_date_time(request.form["Arrival_Time"])
        dur_hour, dur_min = abs(Arrival_hour - Dep_hour), abs(Arrival_min - Dep_min)
        Total_stops = int(request.form["stops"])
        airline = request.form['airline']
        Airline = airline_mapping(airline)

        Source = request.form["Source"]
        source_mapping = {'Chennai': [0, 0, 0, 1], 'Delhi': [1, 0, 0, 0], 'Kolkata': [0, 1, 0, 0], 'Mumbai': [0, 0, 1, 0]}
        Source_encoded = source_destination_mapping(Source, source_mapping)

        Destination = request.form["Destination"]
        destination_mapping = {'Cochin': [1, 0, 0, 0], 'Delhi': [0, 1, 0, 0], 'Hyderabad': [0, 0, 1, 0], 'Kolkata': [0, 0, 0, 1]}
        Destination_encoded = source_destination_mapping(Destination, destination_mapping)

        prediction = model.predict([[Total_stops, Journey_day, Journey_month, Dep_hour, Dep_min, Arrival_hour,
                                     Arrival_min, dur_hour, dur_min, Airline, Source_encoded[0], Source_encoded[1],
                                     Source_encoded[2], Source_encoded[3], Destination_encoded[0], Destination_encoded[1],
                                     Destination_encoded[2], Destination_encoded[3]]])

        output = round(prediction[0], 2)
        return render_template('home.html', prediction_text="Your Flight price is Rs. {}".format(output))

    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)
