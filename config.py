class Config:
    DEBUG = True
    SECRET_KEY = "your-secret-key"
    DATA_DIR = "data"
    STATIC_DIR = "static"
    
    CAMPUSES = {
        "Vellore": {"coords": [12.9692, 79.1559]}
    }

    # -------------------- BUILDINGS --------------------
    BUILDINGS = {
        "MB": {"name": "Main Building", "coords": [12.968778086492943, 79.15592990631848]},
        "SJT": {"name": "Silver Jubilee Tower", "coords": [12.971722015167897, 79.16355087207683]},
        "TT": {"name": "Technology Tower", "coords": [12.971157921291086, 79.15985062428524]},
        "PRP": {"name": "Pearl Research Park (Ladies Hostel)", "coords": [12.972296737254931, 79.16620814166355]},
        "GDN": {"name": "GDN Canteen", "coords": [12.969739763994825, 79.15532406117485]},
        "A-Block": {"name": "Gandhi Block", "coords": [12.972628213743711, 79.16741357993612]},
        "MG": {"name": "Main Gate", "coords": [12.968441062810065, 79.1559297465415]},
        "C-Block": {"name": "VIT 3rd Gate", "coords": [12.968700932643966, 79.15867203673623]},
        "D-Block": {"name": "Foodys", "coords": [12.969707630198013, 79.15823803449811]},
        "E-Block": {"name": "Anna Auditorium", "coords": [12.969735589979779, 79.15581973121864]}
    }

    # -------------------- HOSTELS --------------------
    HOSTELS = {
        # Mens Hostels
        "Q-Block": {"name": "Q Block (Mens Hostel)", "coords": [12.973907460187062, 79.16408354631996]},
        "M-Block": {"name": "M Block (Mens Hostel)", "coords": [12.973032511093457, 79.16369981315407]},
        "K-Block": {"name": "K Block (Mens Hostel)", "coords": [12.972633681748777, 79.16137689016004]},
        "G-Block": {"name": "G Block (Mens Hostel)", "coords": [12.974240501910693, 79.15846734839572]},
        "B-Block": {"name": "B Block (Mens Hostel)", "coords": [12.97438318215479, 79.15682645258096]},
        "P-Block": {"name": "P Block (Mens Hostel)", "coords": [12.974890601663047, 79.15866972254265]},
        # Ladies Hostels
        "PRP": {"name": "Pearl Research Park (Ladies Hostel)", "coords": [12.972296737254931, 79.16620814166355]},
        "A-Block": {"name": "A Block (Ladies Hostel)", "coords": [12.972188, 79.164841]},
        "C-Block": {"name": "C Block (Ladies Hostel)", "coords": [12.973532, 79.167640]},
        "E-Block": {"name": "E Block (Ladies Hostel)", "coords": [12.974092, 79.165890]},
        "F-Block": {"name": "F Block (Ladies Hostel)", "coords": [12.974670, 79.164760]},
        # Other/Mixed/Legacy
        "H": {"name": "H Block", "coords": [12.972070691331993, 79.15748266144281]}
    }

    # -------------------- BUS CONFIG --------------------
    DEFAULT_SPEED_KMH = 20 
    DEFAULT_CAPACITY = 40  
    MAX_OCCUPANCY = 45     

    # -------------------- ROUTE GROUPS --------------------
    BUS_ROUTES = {
        "ladies": {
            "route_name": "Ladies Hostel Shuttle",
            "stops": ["PRP", "SJT", "C-Block", "MG"],
            "color": "#FF69B4",
            "bus_ids": ["bus_L1", "bus_L2", "bus_L3", "bus_L4"]
        },
        "mens": {
            "route_name": "Mens Hostel Shuttle",
            "stops": ["Q-Block", "M-Block", "K-Block", "G-Block", "B-Block", "P-Block", "MG"],
            "color": "#0066FF",
            "bus_ids": ["bus_M1", "bus_M2", "bus_M3", "bus_M4", "bus_M5", "bus_M6"]
        }
    }

    # -------------------- TRAFFIC --------------------
    TRAFFIC_PATTERNS = {
        "weekday": {
            8: 1.5, 9: 1.4, 10: 1.2, 11: 1.0, 12: 1.1, 13: 1.1, 14: 1.0,
            15: 1.0, 16: 1.2, 17: 1.5, 18: 1.4, 19: 1.2, 20: 1.0,
            21: 0.9, 22: 0.8
        },
        "weekend": {
            8: 0.9, 9: 0.9, 10: 1.0, 11: 1.1, 12: 1.2, 13: 1.2, 14: 1.1,
            15: 1.0, 16: 1.0, 17: 1.1, 18: 1.2, 19: 1.1, 20: 1.0,
            21: 0.9, 22: 0.8
        }
    }

    REFRESH_INTERVAL = 30 
    ANALYTICS_ENABLED = True
    
    MAP_DEFAULT_ZOOM = 15
    MAP_MAX_ZOOM = 18
    
    # -------------------- BUS SCHEDULE --------------------
    BUS_SCHEDULE = {
        "weekday": {"start_time": "07:00", "end_time": "22:00", "frequency": 15},
        "weekend": {"start_time": "08:00", "end_time": "20:00", "frequency": 30}
    }
    
    # -------------------- COLORS --------------------
    COLORS = {
        "primary": "#0062cc",
        "secondary": "#6c757d",
        "success": "#2ecc71",
        "danger": "#e74c3c",
        "warning": "#f39c12",
        "info": "#3498db",
        "ladies_route": "#FF69B4",
        "mens_route": "#0066FF"
    }
    
    # -------------------- CONTACTS --------------------
    EMERGENCY_CONTACTS = {
        "transport_office": "+91 1234567890",
        "security": "+91 1234567890",
        "helpdesk": "+91 1234567890"
    }
