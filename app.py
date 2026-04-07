from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

API_KEY = "6d76615fa92c3a69179885fd825ffff7"
BASE_URL     = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

def parse_weather(data):
    return {
        "city": data["name"],
        "temp": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"].capitalize(),
        "icon": data["weather"][0]["icon"],
        "wind": data["wind"]["speed"],
        "visibility": data.get("visibility", 0),
    }

@app.route("/", methods=["GET", "POST"])
def index():
    weather = None
    error = None

    if request.method == "POST":
        city = request.form.get("city", "").strip()
        if city:
            response = requests.get(BASE_URL, params={
                "q": f"{city},IN",
                "appid": API_KEY,
                "units": "metric"
            })
            data = response.json()
            if response.status_code == 200:
                weather = parse_weather(data)
            elif response.status_code == 401:
                error = "Invalid API key. Please update your API key in app.py."
            elif response.status_code == 404:
                error = "City not found. Please try another city in India."
            else:
                error = f"Error: {data.get('message', 'Something went wrong.')}"

    return render_template("index.html", weather=weather, error=error)

@app.route("/weather-by-coords")
def weather_by_coords():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    if not lat or not lon:
        return jsonify({"error": "Missing coordinates"}), 400

    response = requests.get(BASE_URL, params={
        "lat": lat, "lon": lon,
        "appid": API_KEY,
        "units": "metric"
    })
    data = response.json()
    if response.status_code == 200:
        return jsonify(parse_weather(data))
    return jsonify({"error": data.get("message", "Failed to fetch weather")}), response.status_code

def parse_forecast(data):
    # Group by day, pick the noon entry (or first available)
    days = {}
    for item in data["list"]:
        date = item["dt_txt"].split(" ")[0]
        if date not in days:
            days[date] = item
        elif "12:00:00" in item["dt_txt"]:
            days[date] = item
    # Return next 5 days excluding today
    from datetime import datetime
    today = datetime.utcnow().strftime("%Y-%m-%d")
    result = []
    for date, item in sorted(days.items()):
        if date == today:
            continue
        result.append({
            "date": date,
            "day": datetime.strptime(date, "%Y-%m-%d").strftime("%a, %d %b"),
            "temp_max": round(item["main"]["temp_max"]),
            "temp_min": round(item["main"]["temp_min"]),
            "description": item["weather"][0]["description"].capitalize(),
            "icon": item["weather"][0]["icon"],
            "humidity": item["main"]["humidity"],
            "wind": item["wind"]["speed"],
        })
        if len(result) == 5:
            break
    return result

@app.route("/forecast-by-coords")
def forecast_by_coords():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    city = request.args.get("city")
    params = {"appid": API_KEY, "units": "metric"}
    if city:
        params["q"] = f"{city},IN"
    elif lat and lon:
        params["lat"] = lat
        params["lon"] = lon
    else:
        return jsonify({"error": "Missing parameters"}), 400
    response = requests.get(FORECAST_URL, params=params)
    data = response.json()
    if response.status_code == 200:
        return jsonify(parse_forecast(data))
    return jsonify({"error": data.get("message", "Failed to fetch forecast")}), response.status_code

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
