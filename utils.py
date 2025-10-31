import json
import os
from datetime import datetime, timedelta
from geopy.distance import geodesic
import qrcode
from dateutil.parser import parse
import random

# ==========================================================
# JSON UTILITIES
# ==========================================================
def load_json(file_path, default=None):
    """Load a JSON file or return a default if it doesn’t exist or is invalid."""
    if default is None:
        default = {}
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"[ERROR] Failed to decode JSON from {file_path}. Returning default.")
            return default
    else:
        print(f"[INFO] {file_path} not found. Returning default.")
    return default


def save_json(file_path, data):
    """Save data to a JSON file safely."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"[INFO] Data saved to {file_path}")


# ==========================================================
# QR CODE GENERATION
# ==========================================================
def generate_qr_code(bus_id, file_path):
    """Generate and save a QR code image for a bus."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(bus_id)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(file_path)
        print(f"[INFO] QR code generated for {bus_id} at {file_path}")
    except Exception as e:
        print(f"[ERROR] Failed to generate QR for {bus_id}: {e}")


# ==========================================================
# ETA AND DISTANCE CALCULATIONS
# ==========================================================
def calculate_eta(start_coords, end_coords, speed_kmh, last_update=None, traffic_factor=1.0):
    """
    Calculate ETA based on distance, speed, and traffic factor.
    Returns tuple: (ETA string, distance_km)
    """
    try:
        distance_km = geodesic(start_coords, end_coords).km
    except Exception as e:
        print(f"[ERROR] Failed to calculate distance: {e}")
        distance_km = 0.0

    adjusted_speed = max(speed_kmh / max(traffic_factor, 0.1), 0.1)
    time_minutes = (distance_km / adjusted_speed) * 60

    try:
        last_update_time = parse(last_update) if last_update else datetime.now()
    except Exception:
        last_update_time = datetime.now()

    # Add a small random buffer
    time_minutes = max(1, time_minutes + random.uniform(-2, 2))
    eta_time = last_update_time + timedelta(minutes=time_minutes)
    return eta_time.strftime("%H:%M:%S"), round(distance_km, 2)


# ==========================================================
# TRAFFIC FACTOR
# ==========================================================
def get_traffic_factor(time_of_day, day_of_week):
    """Return a traffic multiplier based on the time of day and day of week."""
    weekend_factor = 0.8 if day_of_week >= 5 else 1.0

    if 7 <= time_of_day <= 10:      # Morning rush
        time_factor = 1.5
    elif 16 <= time_of_day <= 19:   # Evening rush
        time_factor = 1.4
    elif 11 <= time_of_day <= 15:   # Midday
        time_factor = 1.2
    elif 20 <= time_of_day <= 22:   # Light evening
        time_factor = 1.1
    else:
        time_factor = 0.9

    return round(time_factor * weekend_factor, 2)


# ==========================================================
# OCCUPANCY UTILITIES
# ==========================================================
def calculate_occupancy(current_occupancy, max_capacity, boarding=True, passengers=1):
    """Update occupancy when passengers board or alight."""
    if boarding:
        return min(current_occupancy + passengers, max_capacity)
    return max(current_occupancy - passengers, 0)


def get_occupancy_color(occupancy, capacity):
    """Return a color based on occupancy percentage."""
    if capacity == 0:
        return "gray"
    pct = (occupancy / capacity) * 100
    if pct < 50:
        return "green"
    elif pct < 80:
        return "orange"
    return "red"


def get_occupancy_status(occupancy, capacity):
    """Return descriptive occupancy status."""
    if capacity == 0:
        return "Unknown"
    pct = (occupancy / capacity) * 100
    if pct < 30:
        return "Empty"
    elif pct < 50:
        return "Light"
    elif pct < 80:
        return "Moderate"
    elif pct < 95:
        return "Crowded"
    return "Full"


# ==========================================================
# ARRIVAL ESTIMATION
# ==========================================================
def estimate_arrival_time(route, current_time=None):
    """Estimate arrival time for a route with random buffer (5–20 min)."""
    if current_time is None:
        current_time = datetime.now()
    minutes_to_add = random.randint(5, 20)
    arrival_time = current_time + timedelta(minutes=minutes_to_add)
    return arrival_time.strftime("%H:%M:%S")


# ==========================================================
# ROUTE HANDLING
# ==========================================================
def get_route_info(route_id, routes_data):
    """Fetch route details safely."""
    if not routes_data or route_id not in routes_data:
        print(f"[WARN] Route '{route_id}' not found in routes.json")
        return {"route_name": "Unknown", "start": "Unknown", "end": "Unknown", "waypoints": []}
    return routes_data[route_id]


def get_start_and_end_from_route(route_id, routes_data):
    """Return the start and end point names for a given route."""
    route = get_route_info(route_id, routes_data)
    return route.get("start", "Unknown"), route.get("end", "Unknown")
