from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

API_KEY = "6d76615fa92c3a69179885fd825ffff7"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

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

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
