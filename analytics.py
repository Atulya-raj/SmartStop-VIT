import os
from datetime import datetime, timedelta
import json
from collections import defaultdict
import io
import base64
from dateutil.parser import parse
from config import Config

try:
    import matplotlib.pyplot as plt
    import numpy as np
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    print("Warning: matplotlib not available. Visualization features will be disabled.")

DATA_DIR = Config.DATA_DIR
BUS_DATA_FILE = os.path.join(DATA_DIR, "bus_data.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
FEEDBACK_FILE = os.path.join(DATA_DIR, "feedback.json")
REPORTS_DIR = os.path.join(DATA_DIR, "reports")

os.makedirs(REPORTS_DIR, exist_ok=True)

def load_json(file_path, default=None):
    """Load JSON file or return default if it doesn't exist."""
    if default is None:
        default = {}
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(f"Error decoding JSON from {file_path}, returning default")
                return default
    return default

def save_json(file_path, data):
    """Save data to JSON file."""
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def get_bus_utilization(days=7):
    """Get bus utilization statistics for the last N days."""
    history = load_json(HISTORY_FILE, default={"occupancy_patterns": {}})
    
    if "occupancy_patterns" not in history:
        return {
            "average_occupancy": 0,
            "peak_time": "N/A",
            "peak_occupancy": 0,
            "busiest_bus": "N/A",
            "busiest_bus_avg": 0,
            "least_busy_bus": "N/A",
            "least_busy_bus_avg": 0,
            "hourly_averages": {}
        }
    
    now = datetime.now()
    cutoff_date = now - timedelta(days=days)
    
    occupancy_sum = defaultdict(int)
    occupancy_count = defaultdict(int)
    hourly_data = defaultdict(list)
    
    for bus_id, patterns in history["occupancy_patterns"].items():
        for time_key, entries in patterns.items():
            for entry in entries:
                try:
                    timestamp = parse(entry["timestamp"])
                    if timestamp >= cutoff_date:
                        occupancy_pct = (entry["occupancy"] / entry["capacity"]) * 100
                        
                        occupancy_sum[bus_id] += occupancy_pct
                        occupancy_count[bus_id] += 1
                        
                        hour = timestamp.hour
                        hourly_data[hour].append(occupancy_pct)
                except Exception as e:
                    print(f"Error processing entry: {e}")
                    continue
    
    bus_averages = {}
    for bus_id in occupancy_sum.keys():
        if occupancy_count[bus_id] > 0:
            bus_averages[bus_id] = occupancy_sum[bus_id] / occupancy_count[bus_id]
    
    hourly_averages = {}
    for hour, values in hourly_data.items():
        if values:
            hourly_averages[hour] = sum(values) / len(values)
    
    busiest_bus = ("N/A", 0)
    least_busy_bus = ("N/A", 0)
    
    if bus_averages:
        busiest_bus = max(bus_averages.items(), key=lambda x: x[1])
        least_busy_bus = min(bus_averages.items(), key=lambda x: x[1])
    
    peak_hour = ("N/A", 0)
    if hourly_averages:
        peak_hour = max(hourly_averages.items(), key=lambda x: x[1])
    
    all_values = [value for values in hourly_data.values() for value in values]
    average_occupancy = sum(all_values) / len(all_values) if all_values else 0
    
    return {
        "average_occupancy": round(average_occupancy, 1),
        "peak_time": f"{peak_hour[0]}:00" if peak_hour[0] != "N/A" else "N/A",
        "peak_occupancy": round(peak_hour[1], 1) if peak_hour[1] != 0 else 0,
        "busiest_bus": busiest_bus[0],
        "busiest_bus_avg": round(busiest_bus[1], 1) if busiest_bus[1] != 0 else 0,
        "least_busy_bus": least_busy_bus[0],
        "least_busy_bus_avg": round(least_busy_bus[1], 1) if least_busy_bus[1] != 0 else 0,
        "hourly_averages": {h: round(avg, 1) for h, avg in sorted(hourly_averages.items())}
    }

def get_route_performance(days=7):
    """Analyze route performance based on ETA accuracy and travel times."""
    history = load_json(HISTORY_FILE, default={"travel_times": {}})
    
    if "travel_times" not in history:
        return {
            "routes": {},
            "average_eta_accuracy": 0,
            "fastest_route": "N/A",
            "fastest_route_time": 0,
            "slowest_route": "N/A",
            "slowest_route_time": 0
        }
    
    now = datetime.now()
    cutoff_date = now - timedelta(days=days)
    
    route_times = defaultdict(list)
    route_distances = defaultdict(list)
    
    for route_key, entries in history["travel_times"].items():
        for entry in entries:
            try:
                timestamp = parse(entry["timestamp"])
                if timestamp >= cutoff_date:
                    eta_parts = entry["estimated_time"].split(":")
                    estimated_minutes = int(eta_parts[0]) * 60 + int(eta_parts[1])
                    
                    route_times[route_key].append(estimated_minutes)
                    route_distances[route_key].append(entry["distance"])
            except Exception as e:
                print(f"Error processing route entry: {e}")
                continue
    
    route_stats = {}
    for route_key in route_times.keys():
        if route_times[route_key]:
            avg_time = sum(route_times[route_key]) / len(route_times[route_key])
            avg_distance = sum(route_distances[route_key]) / len(route_distances[route_key])
            avg_speed = avg_distance / (avg_time / 60)  # km/h
            
            route_stats[route_key] = {
                "avg_time_minutes": round(avg_time, 1),
                "avg_distance_km": round(avg_distance, 2),
                "avg_speed_kmh": round(avg_speed, 1),
                "samples": len(route_times[route_key])
            }
    
    fastest_route = ("N/A", {"avg_time_minutes": 0})
    slowest_route = ("N/A", {"avg_time_minutes": 0})
    
    if route_stats:
        try:
            fastest_route = min(route_stats.items(), key=lambda x: x[1]["avg_time_minutes"])
            slowest_route = max(route_stats.items(), key=lambda x: x[1]["avg_time_minutes"])
        except Exception as e:
            print(f"Error finding fastest/slowest routes: {e}")
    
    return {
        "routes": route_stats,
        "fastest_route": fastest_route[0],
        "fastest_route_time": fastest_route[1]["avg_time_minutes"],
        "slowest_route": slowest_route[0],
        "slowest_route_time": slowest_route[1]["avg_time_minutes"]
    }

def generate_utilization_chart():
    """Generate a chart showing bus utilization by hour of day."""
    if not PLOTTING_AVAILABLE:
        return None
        
    stats = get_bus_utilization()
    
    if not stats["hourly_averages"]:
        return None
    
    plt.figure(figsize=(10, 6))
    
    hours = list(stats["hourly_averages"].keys())
    values = list(stats["hourly_averages"].values())
    
    plt.bar(hours, values, color=Config.COLORS["primary"])
    plt.axhline(y=stats["average_occupancy"], color='r', linestyle='-', label=f'Average ({stats["average_occupancy"]}%)')
    
    plt.xlabel('Hour of Day')
    plt.ylabel('Average Occupancy (%)')
    plt.title('Bus Occupancy by Hour of Day')
    plt.xticks(range(min(hours) if hours else 0, max(hours)+1 if hours else 24))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()
    
    return image_base64

def generate_route_performance_chart():
    """Generate a chart showing performance of different routes."""
    if not PLOTTING_AVAILABLE:
        return None
        
    stats = get_route_performance()
    
    if not stats["routes"]:
        return None
    
    routes = list(stats["routes"].keys())
    times = [stats["routes"][r]["avg_time_minutes"] for r in routes]
    speeds = [stats["routes"][r]["avg_speed_kmh"] for r in routes]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
    
    bars1 = ax1.bar(routes, times, color=Config.COLORS["primary"])
    ax1.set_ylabel('Average Travel Time (minutes)')
    ax1.set_title('Average Travel Time by Route')
    ax1.set_xticklabels(routes, rotation=45, ha='right')
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.1f}',
                ha='center', va='bottom', rotation=0)
    
    bars2 = ax2.bar(routes, speeds, color=Config.COLORS["info"])
    ax2.set_ylabel('Average Speed (km/h)')
    ax2.set_title('Average Speed by Route')
    ax2.set_xticklabels(routes, rotation=45, ha='right')
    ax2.grid(axis='y', linestyle='--', alpha=0.7)
    
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.1f}',
                ha='center', va='bottom', rotation=0)
    
    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()
    
    return image_base64

def get_feedback_statistics():
    """Analyze user feedback."""
    feedback = load_json(FEEDBACK_FILE, default={"feedbacks": []})
    
    if not feedback["feedbacks"]:
        return {
            "total_feedback": 0,
            "average_rating": 0,
            "bus_ratings": {}
        }
    
    total = len(feedback["feedbacks"])
    ratings_sum = sum(entry["rating"] for entry in feedback["feedbacks"])
    average_rating = ratings_sum / total if total > 0 else 0
    
    # Group by bus
    bus_ratings = defaultdict(list)
    for entry in feedback["feedbacks"]:
        bus_ratings[entry["bus_id"]].append(entry["rating"])
    
    bus_avg_ratings = {}
    for bus_id, ratings in bus_ratings.items():
        bus_avg_ratings[bus_id] = sum(ratings) / len(ratings)
    
    return {
        "total_feedback": total,
        "average_rating": round(average_rating, 2),
        "bus_ratings": {bus: round(rating, 2) for bus, rating in bus_avg_ratings.items()}
    }

def generate_daily_report():
    """Generate a comprehensive daily report."""
    today = datetime.now().strftime("%Y-%m-%d")
    report_file = os.path.join(REPORTS_DIR, f"report_{today}.json")
    
    utilization = get_bus_utilization()
    route_performance = get_route_performance()
    feedback = get_feedback_statistics()
    
    current_data = load_json(BUS_DATA_FILE)
    
    utilization_chart = None
    route_performance_chart = None
    
    if PLOTTING_AVAILABLE:
        utilization_chart = generate_utilization_chart()
        route_performance_chart = generate_route_performance_chart()
    
    report = {
        "date": today,
        "timestamp": str(datetime.now()),
        "utilization": utilization,
        "route_performance": route_performance,
        "feedback": feedback,
        "active_buses": len(current_data.get("buses", {})),
        "charts": {
            "utilization_chart": utilization_chart,
            "route_performance_chart": route_performance_chart
        }
    }
    
    save_json(report_file, report)
    
    return report

if __name__ == "__main__":
    report = generate_daily_report()
    print(f"Report generated: {report['date']}")
    print(f"Active buses: {report['active_buses']}")
    print(f"Average occupancy: {report['utilization']['average_occupancy']}%")
    print(f"Busiest bus: {report['utilization']['busiest_bus']} ({report['utilization']['busiest_bus_avg']}%)")
    print(f"Busiest time: {report['utilization']['peak_time']} ({report['utilization']['peak_occupancy']}%)")
    print(f"Feedback received: {report['feedback']['total_feedback']}")
    print(f"Average rating: {report['feedback']['average_rating']}/5")