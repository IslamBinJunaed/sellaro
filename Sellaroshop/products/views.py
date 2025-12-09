from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import base64
import cv2
import numpy as np
from .models import Product
from .visual_search import search_engine

@csrf_exempt
@require_http_methods(["POST"])
def visual_search(request):
    """Handle visual search requests"""
    try:
        # Get uploaded image
        if 'image' in request.FILES:
            image_file = request.FILES['image']
            image_array = np.frombuffer(image_file.read(), np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        elif 'image_data' in request.POST:
            # Handle base64 image data
            image_data = request.POST['image_data']
            if 'base64,' in image_data:
                image_data = image_data.split('base64,')[1]
            
            image_bytes = base64.b64decode(image_data)
            image_array = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        else:
            return JsonResponse({
                'success': False,
                'error': 'No image provided'
            }, status=400)
        
        if image is None:
            return JsonResponse({
                'success': False,
                'error': 'Invalid image format'
            }, status=400)
        
        # Extract features from query image
        query_features = search_engine.extract_features(image)
        
        if query_features is None:
            return JsonResponse({
                'success': False,
                'error': 'Could not process image'
            }, status=400)
        
        # Compare with all products
        products = Product.objects.filter(is_active=True)
        results = []
        
        for product in products:
            if product.feature_vector:
                try:
                    # Convert binary feature vector back to numpy array
                    product_features = np.frombuffer(product.feature_vector, dtype=np.float32)
                    
                    # Calculate similarity
                    similarity = search_engine.calculate_similarity(query_features, product_features)
                    
                    if similarity > 0.3:  # Threshold for matching
                        results.append({
                            'product': {
                                'id': product.id,
                                'name': product.name,
                                'description': product.description,
                                'price': str(product.price),
                                'category': product.category.name,
                                'brand': product.brand.name,
                                'image_url': product.image.url if product.image else None,
                                'stock': product.stock
                            },
                            'similarity_score': round(float(similarity), 4)
                        })
                except Exception as e:
                    print(f"Error comparing with product {product.id}: {e}")
                    continue
        
        # Sort by similarity score (descending)
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return JsonResponse({
            'success': True,
            'matches_found': len(results),
            'results': results[:10]  # Return top 10 matches
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def extract_product_features(request):
    """Extract and store features for all products (admin function)"""
    try:
        products = Product.objects.filter(is_active=True)
        processed = 0
        errors = 0
        
        for product in products:
            if product.image and not product.feature_vector:
                try:
                    # Read image
                    image_path = product.image.path
                    image = cv2.imread(image_path)
                    
                    if image is not None:
                        # Extract features
                        features = search_engine.extract_features(image)
                        
                        if features is not None:
                            # Convert to binary and save
                            product.feature_vector = features.tobytes()
                            product.save()
                            processed += 1
                        else:
                            errors += 1
                    else:
                        errors += 1
                
                except Exception as e:
                    print(f"Error processing product {product.id}: {str(e)}")
                    errors += 1
                    continue
        
        return JsonResponse({
            'success': True,
            'message': f'Processed {processed} products, {errors} errors',
            'processed_count': processed,
            'error_count': errors
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_products(request):
    """Get all products for testing"""
    try:
        products = Product.objects.filter(is_active=True)
        
        products_data = []
        for product in products:
            products_data.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': str(product.price),
                'category': product.category.name,
                'brand': product.brand.name,
                'image_url': product.image.url if product.image else None,
                'stock': product.stock,
                'has_features': product.feature_vector is not None
            })
        
        return JsonResponse({
            'success': True,
            'products': products_data
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    