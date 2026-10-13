import json
from app import create_app
from app.services.analytics_service import (
    get_dashboard_stats, get_production_trends, 
    get_saree_distribution, get_worker_rankings
)

app = create_app()
with app.app_context():
    try:
        print("1. Testing get_dashboard_stats...")
        stats = get_dashboard_stats()
        print("Stats:", stats)
        
        print("\n2. Testing get_production_trends...")
        trends = get_production_trends(days=15)
        print("Trends labels:", trends["labels"])
        print("Trends quantities:", trends["quantities"])
        print("Trends profits:", trends["profits"])
        json.dumps(trends)
        
        print("\n3. Testing get_saree_distribution...")
        sarees_dist = get_saree_distribution()
        print("Sarees distribution labels:", sarees_dist["labels"])
        print("Sarees distribution values:", sarees_dist["values"])
        json.dumps(sarees_dist)
        
        print("\n4. Testing get_worker_rankings...")
        rankings = get_worker_rankings()
        print("Rankings labels:", rankings["labels"])
        print("Rankings quantities:", rankings["quantities"])
        print("Rankings earnings:", rankings["earnings"])
        json.dumps(rankings)
        
        print("\nAll JSON serializations successful!")
    except Exception as e:
        import traceback
        traceback.print_exc()
