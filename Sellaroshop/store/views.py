from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import StoreLocation
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    R = 6371  # Earth radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

@csrf_exempt
@require_http_methods(["GET"])
def get_store_locations(request):
    """Get all store locations"""
    try:
        stores = StoreLocation.objects.filter(is_active=True)
        
        stores_data = []
        for store in stores:
            stores_data.append({
                'id': store.id,
                'name': store.name,
                'address': store.address,
                'city': store.city,
                'state': store.state,
                'zip_code': store.zip_code,
                'phone': store.phone,
                'email': store.email,
                'latitude': float(store.latitude),
                'longitude': float(store.longitude),
                'opening_hours': store.opening_hours,
            })
        
        return JsonResponse({
            'success': True,
            'stores': stores_data
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def find_nearby_stores(request):
    """Find stores near a given location"""
    try:
        data = json.loads(request.body)
        user_lat = float(data.get('latitude'))
        user_lon = float(data.get('longitude'))
        radius_km = float(data.get('radius', 10))  # Default 10km radius
        
        all_stores = StoreLocation.objects.filter(is_active=True)
        nearby_stores = []
        
        for store in all_stores:
            distance = haversine(user_lat, user_lon, store.latitude, store.longitude)
            if distance <= radius_km:
                nearby_stores.append({
                    'store': {
                        'id': store.id,
                        'name': store.name,
                        'address': store.address,
                        'city': store.city,
                        'state': store.state,
                        'phone': store.phone,
                        'opening_hours': store.opening_hours,
                        'latitude': float(store.latitude),
                        'longitude': float(store.longitude),
                    },
                    'distance_km': round(distance, 2)
                })
        
        # Sort by distance
        nearby_stores.sort(key=lambda x: x['distance_km'])
        
        return JsonResponse({
            'success': True,
            'user_location': {'latitude': user_lat, 'longitude': user_lon},
            'radius_km': radius_km,
            'nearby_stores': nearby_stores,
            'total_found': len(nearby_stores)
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_store_by_id(request, store_id):
    """Get specific store by ID"""
    try:
        store = StoreLocation.objects.get(id=store_id, is_active=True)
        
        store_data = {
            'id': store.id,
            'name': store.name,
            'address': store.address,
            'city': store.city,
            'state': store.state,
            'zip_code': store.zip_code,
            'phone': store.phone,
            'email': store.email,
            'latitude': float(store.latitude),
            'longitude': float(store.longitude),
            'opening_hours': store.opening_hours,
        }
        
        return JsonResponse({
            'success': True,
            'store': store_data
        })
    
    except StoreLocation.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Store not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    