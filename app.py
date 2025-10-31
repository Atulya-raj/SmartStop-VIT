from flask import Flask, render_template, jsonify, request
import os
import random
import io
import base64
import matplotlib.pyplot as plt
from datetime import datetime
from utils import generate_qr_code  # Make sure utils.py has this function
import json

app = Flask(__name__)

# --------------------------------------------------
# Helper functions for live data
# --------------------------------------------------
def load_buses():
    try:
        with open("data/bus_data.json", "r") as f:
            data = json.load(f)
        return data.get("buses", {}), data.get("last_updated", "")
    except Exception:
        return {}, ""

def load_routes():
    try:
        with open("data/routes.json", "r") as f:
            routes = json.load(f)
        return routes
    except Exception:
        return {}

# --------------------------------------------------
# Routes
# --------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/buses")
def get_buses():
    buses, last_updated = load_buses()
    return jsonify({
        "buses": buses,
        "last_updated": last_updated
    })

# Example in your app.py

autos_data = [
    {"id": "A101", "location": "Near Main Gate", "phone": "9876543210"},
    {"id": "A102", "location": "Near SJT", "phone": "9876543222"},
    # ...add more autos...
]

@app.route("/api/autos")
def get_autos():
    return {"autos": autos_data}

@app.route("/api/book_auto", methods=["POST"])
def book_auto():
    auto_id = request.form.get("autoId")
    pickup = request.form.get("pickupLocation")
    drop = request.form.get("dropLocation")
    phone = request.form.get("phone")
    # Simple check/demo. In a real app, you’d check and update database.
    for auto in autos_data:
        if auto["id"] == auto_id:
            return {"status": "success", "message": f"Auto {auto_id} booked. You'll be contacted soon by driver {auto['phone']}."}
    return {"status": "error", "message": "Auto not found. Please select a valid auto."}

@app.route("/api/routes")
def get_routes():
    routes = load_routes()
    return jsonify(routes)

@app.route("/api/bus/<bus_id>")
def get_bus(bus_id):
    buses, _ = load_buses()
    routes = load_routes()
    if bus_id not in buses:
        return jsonify({"status": "error", "message": "Bus not found"}), 404

    bus = buses[bus_id]
    route_info = routes.get(bus["route_id"], {})
    bus_data = {
        "bus_id": bus_id,
        "route_id": bus.get("route_id", ""),
        "occupancy": bus.get("occupancy", 0),
        "capacity": bus.get("capacity", 0),
        "eta": bus.get("eta", ""),
        "status": bus.get("status", ""),
        "on_time": bus.get("on_time", True),
        "distance_to_destination": bus.get("distance_to_destination", round(random.uniform(1.0, 8.0), 2)),
        "destination": route_info.get("end", "Unknown"),
        "last_update": bus.get("last_update", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    }
    return jsonify({"status": "success", "data": bus_data})

@app.route("/feedback", methods=["POST"])
def feedback():
    # Placeholder for feedback submission
    return jsonify({"status": "success", "message": "Feedback recorded."})

# --------------------------------------------------
# Analytics Page
# --------------------------------------------------
@app.route("/analytics")
def analytics():
    selected_days = int(request.args.get("days", 7))
    buses, _ = load_buses()
    routes = load_routes()

    # --- Mock data generation ---
    utilization_data = {
        "labels": [f"{hour}:00" for hour in range(6, 22)],
        "data": [random.randint(20, 95) for _ in range(16)]
    }

    # Generate Utilization Chart (Base64)
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(utilization_data["labels"], utilization_data["data"], color="#0062cc", marker="o")
    ax.set_title("Bus Occupancy by Hour")
    ax.set_ylabel("Occupancy (%)")
    ax.set_xlabel("Time")
    ax.grid(True, alpha=0.3)
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)
    utilization_chart_base64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)

    # Route performance mock data
    route_labels = list(routes.keys())
    route_times = [random.randint(10, 30) for _ in route_labels]

    # Generate Route Chart
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.bar(route_labels, route_times, color="#3498db")
    ax.set_title("Average Route Times")
    ax.set_ylabel("Minutes")
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)
    route_chart_base64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)

    report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "last_updated": datetime.now().strftime("%H:%M:%S"),
        "active_buses": len(buses),

        "utilization": {
            "average_occupancy": round(sum(utilization_data["data"]) / len(utilization_data["data"]), 1),
            "peak_time": "8:00 AM",
            "peak_occupancy": max(utilization_data["data"]),
            "busiest_bus": random.choice(list(buses.keys())) if buses else "N/A",
            "busiest_bus_avg": random.randint(70, 95) if buses else 0
        },

        "route_performance": {
            "fastest_route": random.choice(route_labels) if route_labels else "N/A",
            "fastest_route_time": min(route_times) if route_times else 0,
            "slowest_route": random.choice(route_labels) if route_labels else "N/A",
            "slowest_route_time": max(route_times) if route_times else 0,
            "routes": {
                r: {
                    "avg_time_minutes": route_times[i] if i < len(route_times) else 0,
                    "avg_distance_km": round(random.uniform(2.5, 5.5), 1),
                    "avg_speed_kmh": round(random.uniform(10, 18), 1),
                    "samples": random.randint(5, 20)
                } for i, r in enumerate(route_labels)
            }
        },

        "feedback": {
            "average_rating": round(random.uniform(3.5, 5.0), 1),
            "total_feedback": random.randint(20, 200),
            "bus_ratings": {
                bus_id: round(random.uniform(3.0, 5.0), 1) for bus_id in buses
            }
        },

        "charts": {
            "utilization_chart": utilization_chart_base64,
            "route_performance_chart": route_chart_base64
        }
    }

    return render_template("analytics.html", report=report, selected_days=selected_days)

# --------------------------------------------------
# QR Code generation
# --------------------------------------------------
if __name__ == "__main__":
    # Generate QR codes for all buses if not exist
    buses, _ = load_buses()
    qr_dir = os.path.join("static", "qr_codes")
    os.makedirs(qr_dir, exist_ok=True)

    for bus_id in buses.keys():
        qr_path = os.path.join(qr_dir, f"{bus_id}.png")
        if not os.path.exists(qr_path):
            generate_qr_code(bus_id, qr_path)

    app.run(debug=True)
