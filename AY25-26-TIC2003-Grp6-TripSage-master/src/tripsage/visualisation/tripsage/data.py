"""Mock data matching the React TripSage app."""

user_data = {
    "name": "Juliana Silva",
    "age": 29,
    "pronouns": "She/Her",
    "avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop&crop=face",
}

destinations = [
    {"id": 1, "name": "Japan, Tokyo", "image": "tokyo", "dates": "25 July 2030 to 29 July 2030"},
    {"id": 2, "name": "Singapore, Singapore", "image": "singapore", "dates": "10 Aug 2030 to 15 Aug 2030"},
    {"id": 3, "name": "Japan, Okinawa", "image": "okinawa", "dates": "1 Sep 2030 to 5 Sep 2030"},
    {"id": 4, "name": "Korea, Jeju", "image": "jeju", "dates": "20 Sep 2030 to 25 Sep 2030"},
    {"id": 5, "name": "Japan, Kyoto", "image": "kyoto", "dates": "10 Oct 2030 to 14 Oct 2030"},
    {"id": 6, "name": "Japan, Hokkaido", "image": "hokkaido", "dates": "1 Nov 2030 to 7 Nov 2030"},
]

events = [
    {"id": 1, "name": "Sumo Showdown", "price": 85.99, "image": "sumo", "category": "Events"},
    {"id": 2, "name": "Tea Making Workshop", "price": 220.99, "image": "tea-ceremony", "category": "Food"},
    {"id": 3, "name": "Nara Tour", "price": 431.99, "image": "nara", "category": "Attractions"},
    {"id": 4, "name": "Geisha Workshops", "price": 450.99, "image": "geisha", "category": "Events"},
]

# Unsplash placeholder images for event cards
image_map = {
    "sumo": "https://images.unsplash.com/photo-1540573133985-87b6da6d54a9?w=400&h=300&fit=crop",
    "tea-ceremony": "https://images.unsplash.com/photo-1545048702-79362596cdc9?w=400&h=300&fit=crop",
    "nara": "https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=400&h=300&fit=crop",
    "geisha": "https://images.unsplash.com/photo-1528164344885-47b1492ee39a?w=400&h=300&fit=crop",
    "tokyo": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=400&h=300&fit=crop",
    "singapore": "https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=400&h=300&fit=crop",
    "okinawa": "https://images.unsplash.com/photo-1590559899731-a382839e5549?w=400&h=300&fit=crop",
    "jeju": "https://images.unsplash.com/photo-1578037571214-25e07ed1b244?w=400&h=300&fit=crop",
    "kyoto": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=400&h=300&fit=crop",
    "hokkaido": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?w=400&h=300&fit=crop",
}

destination_expenses = {
    1: {
        "total": 1000,
        "categories": [
            {"name": "Food", "amount": 500, "percentage": 52.6, "color": "#8CB4D5"},
            {"name": "Souvenir", "amount": 250, "percentage": 26.3, "color": "#D4C27A"},
            {"name": "Events", "amount": 150, "percentage": 13.2, "color": "#A889B5"},
            {"name": "Transport", "amount": 100, "percentage": 7.9, "color": "#C9A576"},
        ],
        "visited": [
            {"id": 1, "name": "Sumo Showdown", "date": "25 July 2030", "cost": 85.99, "rating": 5, "image": "sumo", "lat": 35.6997, "lng": 139.7935},
            {"id": 2, "name": "Nara Tour", "date": "25 July 2030", "cost": 10.0, "rating": 3, "image": "nara", "lat": 34.6851, "lng": 135.8048},
            {"id": 3, "name": "Tsukiji Fish Market", "date": "26 July 2030", "cost": 45.0, "rating": 5, "image": "tokyo", "lat": 35.6654, "lng": 139.7707},
            {"id": 4, "name": "Senso-ji Temple", "date": "27 July 2030", "cost": 0, "rating": 4, "image": "tokyo", "lat": 35.7148, "lng": 139.7967},
            {"id": 5, "name": "Akihabara Shopping", "date": "28 July 2030", "cost": 120.0, "rating": 4, "image": "tokyo", "lat": 35.7023, "lng": 139.7745},
            {"id": 6, "name": "Shibuya Crossing Walk", "date": "29 July 2030", "cost": 0, "rating": 5, "image": "tokyo", "lat": 35.6595, "lng": 139.7004},
        ],
    },
    2: {
        "total": 1500,
        "categories": [
            {"name": "Food", "amount": 700, "percentage": 46.7, "color": "#8CB4D5"},
            {"name": "Souvenir", "amount": 300, "percentage": 20.0, "color": "#D4C27A"},
            {"name": "Events", "amount": 200, "percentage": 13.3, "color": "#A889B5"},
            {"name": "Transport", "amount": 300, "percentage": 20.0, "color": "#C9A576"},
        ],
        "visited": [
            {"id": 1, "name": "Gardens by the Bay", "date": "10 Aug 2030", "cost": 28.0, "rating": 5, "image": "singapore", "lat": 1.2816, "lng": 103.8636},
            {"id": 2, "name": "Marina Bay Sands", "date": "11 Aug 2030", "cost": 55.0, "rating": 5, "image": "singapore", "lat": 1.2834, "lng": 103.8607},
            {"id": 3, "name": "Chinatown Food Tour", "date": "12 Aug 2030", "cost": 35.0, "rating": 4, "image": "singapore", "lat": 1.2833, "lng": 103.8443},
            {"id": 4, "name": "Sentosa Island", "date": "13 Aug 2030", "cost": 80.0, "rating": 4, "image": "singapore", "lat": 1.2494, "lng": 103.8303},
            {"id": 5, "name": "Merlion Park", "date": "14 Aug 2030", "cost": 0, "rating": 3, "image": "singapore", "lat": 1.2868, "lng": 103.8545},
        ],
    },
    3: {
        "total": 800,
        "categories": [
            {"name": "Food", "amount": 350, "percentage": 43.8, "color": "#8CB4D5"},
            {"name": "Souvenir", "amount": 100, "percentage": 12.5, "color": "#D4C27A"},
            {"name": "Events", "amount": 200, "percentage": 25.0, "color": "#A889B5"},
            {"name": "Transport", "amount": 150, "percentage": 18.7, "color": "#C9A576"},
        ],
        "visited": [
            {"id": 1, "name": "Beach Day", "date": "2 Sep 2030", "cost": 0, "rating": 5, "image": "okinawa", "lat": 26.3344, "lng": 127.8056},
            {"id": 2, "name": "Shuri Castle", "date": "3 Sep 2030", "cost": 30.0, "rating": 4, "image": "okinawa", "lat": 26.2171, "lng": 127.7195},
            {"id": 3, "name": "Churaumi Aquarium", "date": "4 Sep 2030", "cost": 25.0, "rating": 5, "image": "okinawa", "lat": 26.6944, "lng": 127.8778},
            {"id": 4, "name": "Kokusai Street Market", "date": "5 Sep 2030", "cost": 40.0, "rating": 4, "image": "okinawa", "lat": 26.3367, "lng": 127.6867},
        ],
    },
    4: {
        "total": 600,
        "categories": [
            {"name": "Food", "amount": 250, "percentage": 41.7, "color": "#8CB4D5"},
            {"name": "Souvenir", "amount": 100, "percentage": 16.7, "color": "#D4C27A"},
            {"name": "Events", "amount": 150, "percentage": 25.0, "color": "#A889B5"},
            {"name": "Transport", "amount": 100, "percentage": 16.6, "color": "#C9A576"},
        ],
        "visited": [
            {"id": 1, "name": "Dol Hareubang Tour", "date": "21 Sep 2030", "cost": 15.0, "rating": 4, "image": "jeju", "lat": 33.4536, "lng": 126.5706},
            {"id": 2, "name": "Hallasan Mountain Hike", "date": "22 Sep 2030", "cost": 0, "rating": 5, "image": "jeju", "lat": 33.3617, "lng": 126.5292},
            {"id": 3, "name": "Jeongbang Waterfall", "date": "23 Sep 2030", "cost": 5.0, "rating": 4, "image": "jeju", "lat": 33.2439, "lng": 126.5725},
            {"id": 4, "name": "Black Pork BBQ", "date": "24 Sep 2030", "cost": 35.0, "rating": 5, "image": "jeju", "lat": 33.5101, "lng": 126.5298},
        ],
    },
    5: {
        "total": 900,
        "categories": [
            {"name": "Food", "amount": 400, "percentage": 44.4, "color": "#8CB4D5"},
            {"name": "Souvenir", "amount": 200, "percentage": 22.2, "color": "#D4C27A"},
            {"name": "Events", "amount": 180, "percentage": 20.0, "color": "#A889B5"},
            {"name": "Transport", "amount": 120, "percentage": 13.4, "color": "#C9A576"},
        ],
        "visited": [
            {"id": 1, "name": "Bamboo Grove Walk", "date": "11 Oct 2030", "cost": 0, "rating": 5, "image": "kyoto", "lat": 35.0170, "lng": 135.6713},
            {"id": 2, "name": "Geisha Workshops", "date": "12 Oct 2030", "cost": 450.99, "rating": 4, "image": "geisha", "lat": 35.0037, "lng": 135.7787},
            {"id": 3, "name": "Fushimi Inari Shrine", "date": "13 Oct 2030", "cost": 0, "rating": 5, "image": "kyoto", "lat": 34.9671, "lng": 135.7727},
            {"id": 4, "name": "Kinkaku-ji Temple", "date": "13 Oct 2030", "cost": 10.0, "rating": 5, "image": "kyoto", "lat": 35.0394, "lng": 135.7292},
            {"id": 5, "name": "Nishiki Market", "date": "14 Oct 2030", "cost": 50.0, "rating": 4, "image": "kyoto", "lat": 35.0050, "lng": 135.7650},
        ],
    },
    6: {
        "total": 1200,
        "categories": [
            {"name": "Food", "amount": 500, "percentage": 41.7, "color": "#8CB4D5"},
            {"name": "Souvenir", "amount": 200, "percentage": 16.7, "color": "#D4C27A"},
            {"name": "Events", "amount": 250, "percentage": 20.8, "color": "#A889B5"},
            {"name": "Transport", "amount": 250, "percentage": 20.8, "color": "#C9A576"},
        ],
        "visited": [
            {"id": 1, "name": "Lavender Fields", "date": "2 Nov 2030", "cost": 25.0, "rating": 5, "image": "hokkaido", "lat": 43.3400, "lng": 142.3833},
            {"id": 2, "name": "Otaru Canal Walk", "date": "3 Nov 2030", "cost": 0, "rating": 4, "image": "hokkaido", "lat": 43.1975, "lng": 140.9944},
            {"id": 3, "name": "Sapporo Beer Museum", "date": "4 Nov 2030", "cost": 15.0, "rating": 4, "image": "hokkaido", "lat": 43.0714, "lng": 141.3564},
            {"id": 4, "name": "Snow Festival Grounds", "date": "5 Nov 2030", "cost": 0, "rating": 5, "image": "hokkaido", "lat": 43.0621, "lng": 141.3544},
            {"id": 5, "name": "Noboribetsu Onsen", "date": "6 Nov 2030", "cost": 40.0, "rating": 5, "image": "hokkaido", "lat": 42.4936, "lng": 141.1669},
        ],
    },
}

dashboard_countries = [
    {"name": "Singapore", "flag": "🇸🇬"},
    {"name": "Japan", "flag": "🇯🇵"},
    {"name": "United States", "flag": "🇺🇸"},
    {"name": "Switzerland", "flag": "🇨🇭"},
    {"name": "Canada", "flag": "🇨🇦"},
    {"name": "Christmas Island", "flag": "🇨🇽"},
]

all_chart_data = [
    {"year": "2022", "expenseCosts": 25, "travelFees": 10, "eventAttended": 5, "distanceTravelled": 1000},
    {"year": "2023", "expenseCosts": 40, "travelFees": 20, "eventAttended": 15, "distanceTravelled": 2900},
    {"year": "2024", "expenseCosts": 55, "travelFees": 30, "eventAttended": 25, "distanceTravelled": 5400},
    {"year": "2025", "expenseCosts": 80, "travelFees": 45, "eventAttended": 35, "distanceTravelled": 8100},
    {"year": "2026", "expenseCosts": 120, "travelFees": 70, "eventAttended": 50, "distanceTravelled": 11650},
]

dashboard_data_by_country = {
    "Singapore": {
        "stats": [
            {"label": "Total Costs", "value": "$12,000"},
            {"label": "Total Place Visited", "value": "8"},
            {"label": "Countries", "value": "1"},
            {"label": "Events Attended", "value": "15"},
        ],
        "chartData": [
            {"year": "2022", "expenseCosts": 10, "travelFees": 5, "eventAttended": 2, "distanceTravelled": 300},
            {"year": "2023", "expenseCosts": 20, "travelFees": 8, "eventAttended": 5, "distanceTravelled": 600},
            {"year": "2024", "expenseCosts": 30, "travelFees": 15, "eventAttended": 8, "distanceTravelled": 900},
            {"year": "2025", "expenseCosts": 45, "travelFees": 20, "eventAttended": 12, "distanceTravelled": 1200},
            {"year": "2026", "expenseCosts": 60, "travelFees": 30, "eventAttended": 18, "distanceTravelled": 1500},
        ],
    },
    "Japan": {
        "stats": [
            {"label": "Total Costs", "value": "$45,000"},
            {"label": "Total Place Visited", "value": "12"},
            {"label": "Countries", "value": "1"},
            {"label": "Events Attended", "value": "65"},
        ],
        "chartData": [
            {"year": "2022", "expenseCosts": 25, "travelFees": 10, "eventAttended": 5, "distanceTravelled": 500},
            {"year": "2023", "expenseCosts": 40, "travelFees": 20, "eventAttended": 15, "distanceTravelled": 1200},
            {"year": "2024", "expenseCosts": 55, "travelFees": 30, "eventAttended": 25, "distanceTravelled": 2000},
            {"year": "2025", "expenseCosts": 80, "travelFees": 45, "eventAttended": 35, "distanceTravelled": 3000},
            {"year": "2026", "expenseCosts": 120, "travelFees": 70, "eventAttended": 50, "distanceTravelled": 4500},
        ],
    },
}

all_stats = [
    {"label": "Total Costs", "value": "$78,000"},
    {"label": "Total Place Visited", "value": "25"},
    {"label": "Countries", "value": "6"},
    {"label": "Events Attended", "value": "123"},
]
