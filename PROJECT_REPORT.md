# India Weather App — Project Report

## 1. Project Overview

A full-stack web application that displays real-time weather data for any location across India. Users can either type a city name in the search bar or click directly on an interactive map to get live weather information including temperature, humidity, wind speed, visibility, and weather conditions.

---

## 2. Project Structure

```
Python Capstone/
├── app.py                  # Flask backend (routes, API calls)
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html          # Frontend (HTML + CSS + JavaScript)
└── static/
    └── lib/
        ├── leaflet.js      # Map library (locally hosted)
        └── leaflet.css     # Map library styles (locally hosted)
```

---

## 3. Technology Stack

### Backend
| Technology | Version | Purpose |
|---|---|---|
| Python | 3.x | Core programming language |
| Flask | Latest | Web framework / server |
| Requests | Latest | HTTP calls to OpenWeatherMap API |

### Frontend
| Technology | Purpose |
|---|---|
| HTML5 | Page structure |
| CSS3 | Styling, animations, layout |
| Vanilla JavaScript | Map interaction, API calls, DOM updates |
| Leaflet.js v1.9.4 | Interactive map rendering |
| OpenStreetMap Tiles | Map tile images |
| Font Awesome 6.5 | Weather & UI icons |
| Google Fonts (Inter) | Typography |

### External API
| Service | Usage |
|---|---|
| OpenWeatherMap API v2.5 | Real-time weather data |
| OpenStreetMap | Map tile images |

---

## 4. Backend — app.py

### Framework: Flask
Flask is a lightweight Python web framework. It handles HTTP requests, renders HTML templates using Jinja2, and serves JSON responses.

### Routes

#### `GET /` and `POST /`
- `GET` — Loads the homepage with an empty weather panel
- `POST` — Receives a city name from the search form, calls OpenWeatherMap with `city,IN` (restricts to India), and passes weather data to the template

#### `GET /weather-by-coords?lat=&lon=`
- Called by JavaScript when user clicks on the map
- Accepts latitude and longitude as query parameters
- Returns a JSON response with weather data
- Used for AJAX-style updates without page reload

### Helper Function: `parse_weather(data)`
Extracts and returns only the required fields from the raw OpenWeatherMap API response:
- `city` — Location name
- `temp` — Current temperature in °C
- `feels_like` — Apparent temperature
- `humidity` — Humidity percentage
- `description` — Weather condition text
- `icon` — Icon code for weather image
- `wind` — Wind speed in m/s
- `visibility` — Visibility in metres

### Error Handling
| HTTP Status | Meaning | Message Shown |
|---|---|---|
| 200 | Success | Weather data displayed |
| 401 | Invalid API key | Key error message |
| 404 | City not found | City not found message |
| Other | Unknown error | Raw API error message |

---

## 5. Frontend — index.html

### Layout
The page is split into two sections using CSS Flexbox:
- **Left (flex: 1)** — Full-height interactive Leaflet map
- **Right (320px fixed)** — Sidebar showing weather results

### Header
- App logo with Font Awesome cloud-sun icon
- Search form (POST to `/`) with city input and search button
- Hint text prompting user to click the map

### Sidebar States
The sidebar has 4 possible states, toggled by JavaScript:
1. **Placeholder** — Shown on first load, prompts user to interact
2. **Loading spinner** — Shown while API call is in progress (CSS animation)
3. **Error message** — Shown on API failure with red styled box
4. **Weather card** — Shown on success with full weather details

### Weather Card Contents
- City name + coordinates (lat/lon for map clicks)
- Weather icon from OpenWeatherMap (with blue glow CSS filter)
- Large temperature display
- Weather description
- 2×2 detail grid:
  - Feels Like (orange icon)
  - Humidity (blue icon)
  - Wind Speed (purple icon)
  - Visibility (green icon)

### CSS Highlights
- Dark theme using `#0d1117` base (GitHub dark style)
- Glassmorphism header with `backdrop-filter: blur`
- `fadeIn` keyframe animation on weather card appearance
- Spinning loader using CSS `@keyframes` and `border-top-color`
- Responsive detail grid using `display: grid`

### Jinja2 + JavaScript Data Passing
To avoid JS linter errors caused by Jinja2 `{{ }}` syntax inside `<script>` blocks, server data is injected using hidden `<script type="application/json">` tags:

```html
<script type="application/json" id="server-weather">{{ weather | tojson }}</script>
<script type="application/json" id="server-error">{{ error | tojson }}</script>
```

JavaScript reads these safely:
```js
var serverWeather = JSON.parse(document.getElementById('server-weather').textContent);
```

This is the industry-standard pattern for passing server-side data to client-side JS in Flask/Django apps.

---

## 6. Interactive Map — Leaflet.js

### What is Leaflet.js?
Leaflet is an open-source JavaScript library for interactive maps. It is lightweight (~42KB), mobile-friendly, and widely used in production applications.

### Map Configuration
```js
L.map('map', {
    center: [20.5937, 78.9629],  // Geographic center of India
    zoom: 5,                      // Country-level zoom
    minZoom: 4                    // Prevents zooming out too far
});
```

### Map Tiles — OpenStreetMap
Map tiles are the image squares that make up the visible map. They are fetched from OpenStreetMap's tile server:
```
https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
```
- `{s}` — Subdomain (a/b/c) for load balancing
- `{z}` — Zoom level
- `{x}` and `{y}` — Tile coordinates

Leaflet and its CSS are hosted **locally** in `static/lib/` to avoid CDN security warnings and external dependencies.

### Click Interaction
```js
map.on('click', function(e) {
    fetchWeatherByCoords(e.latlng.lat, e.latlng.lng);
});
```
When user clicks anywhere on the map:
1. A marker is dropped at the clicked location
2. A `fetch()` call is made to `/weather-by-coords?lat=...&lon=...`
3. The sidebar updates with weather for that exact coordinate
4. A popup appears on the marker showing city name and temperature

### Marker & Popup
```js
marker = L.marker([lat, lon]).addTo(map);
marker.bindPopup('<b>CityName</b><br>27°C — Haze').openPopup();
```

---

## 7. OpenWeatherMap API

### Endpoint Used
```
https://api.openweathermap.org/data/2.5/weather
```

### Two Query Modes

**By City Name (search form):**
```
?q=Mumbai,IN&appid=API_KEY&units=metric
```
- `q=Mumbai,IN` — City name restricted to India using country code `IN`
- `units=metric` — Returns temperature in Celsius

**By Coordinates (map click):**
```
?lat=19.07&lon=72.87&appid=API_KEY&units=metric
```
- Uses exact latitude/longitude from map click

### API Response Fields Used
```json
{
  "name": "Mumbai",
  "main": {
    "temp": 27.0,
    "feels_like": 28.8,
    "humidity": 69
  },
  "weather": [{ "description": "haze", "icon": "50n" }],
  "wind": { "speed": 3.09 },
  "visibility": 5000
}
```

### Weather Icons
OpenWeatherMap provides icon codes (e.g. `50n`, `01d`) that map to hosted images:
```
https://openweathermap.org/img/wn/50n@2x.png
```
These are displayed in the weather card with a CSS glow effect.

---

## 8. Data Flow Diagram

```
User Types City          User Clicks Map
      |                        |
      v                        v
  POST /                GET /weather-by-coords
      |                   ?lat=xx&lon=yy
      |                        |
      v                        v
  Flask calls OpenWeatherMap API
      |
      v
  parse_weather() extracts fields
      |
      +---> City Search: render_template() → Jinja2 → HTML page
      |
      +---> Map Click: jsonify() → JSON → JavaScript fetch() → DOM update
```

---

## 9. How to Run

### Prerequisites
- Python 3.x installed
- OpenWeatherMap free API key from https://openweathermap.org/api

### Steps
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your API key in app.py line 6
API_KEY = "your_api_key_here"

# 3. Run the server
python app.py

# 4. Open in browser
http://127.0.0.1:8080
```

> Note: Port 5000 is occupied by macOS AirPlay Receiver, so the app runs on port 8080.

---

## 10. Key Implementation Decisions

| Decision | Reason |
|---|---|
| Flask over Django | Lightweight, minimal setup for a single-page app |
| Leaflet over Google Maps | Free, open-source, no billing required |
| OpenStreetMap tiles | Free, no API key needed for tiles |
| Leaflet hosted locally | Avoids CDN security warnings |
| `script type="application/json"` | Clean way to pass Jinja2 data to JS without linter errors |
| Port 8080 | Port 5000 blocked by macOS Control Center (AirPlay) |
| `,IN` country code in API query | Restricts search results to India only |
| Vanilla JS fetch() | No jQuery or Axios needed, keeps dependencies minimal |

---

## 11. Limitations & Possible Improvements

| Limitation | Possible Fix |
|---|---|
| API key hardcoded in app.py | Move to `.env` file using `python-dotenv` |
| No caching — every click hits the API | Add Flask-Caching with a 10-minute TTL |
| Only current weather shown | Add 5-day forecast using `/forecast` endpoint |
| No geolocation | Add browser `navigator.geolocation` to auto-detect user location |
| Not mobile responsive | Add CSS media queries for smaller screens |
