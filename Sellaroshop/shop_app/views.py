# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.db import transaction, models
from decimal import Decimal, InvalidOperation
import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Avg
from django.contrib import messages
from .models import (
    Product, Category, Brand, Cart, CartItem, 
    Store, Deal, ProductReview, Wishlist, ProductImage
)

# Helper function to get or create cart
def get_or_create_cart(request):
    """Get or create cart for user or session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        # For anonymous users, use session
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        cart, created = Cart.objects.get_or_create(
            session_key=session_key,
            user=None
        )
    return cart

# Home page
def home(request):
    featured_products = Product.objects.filter(is_featured=True, available=True)[:8]
    new_products = Product.objects.filter(is_new=True, available=True)[:8]
    on_sale_products = Product.objects.filter(is_on_sale=True, available=True)[:8]
    
    return render(request, 'index.html', {
        'featured_products': featured_products,
        'new_products': new_products,
        'on_sale_products': on_sale_products,
    })

# Authentication views
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Merge cart if user had a guest cart
            session_key = request.session.session_key
            if session_key:
                try:
                    guest_cart = Cart.objects.filter(session_key=session_key, user=None).first()
                    if guest_cart:
                        user_cart = get_or_create_cart(request)
                        # Transfer items from guest cart to user cart
                        for item in guest_cart.items.all():
                            user_item, created = CartItem.objects.get_or_create(
                                cart=user_cart,
                                product=item.product,
                                defaults={'quantity': item.quantity}
                            )
                            if not created:
                                user_item.quantity += item.quantity
                                user_item.save()
                        # Delete guest cart
                        guest_cart.delete()
                except Exception as e:
                    print(f"Error merging cart: {e}")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Login successful'})
            return redirect('home')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Invalid credentials'})
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'login.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Log the user in
            login(request, user)
            
            # Merge cart if user had a guest cart
            session_key = request.session.session_key
            if session_key:
                try:
                    guest_cart = Cart.objects.filter(session_key=session_key, user=None).first()
                    if guest_cart:
                        user_cart = get_or_create_cart(request)
                        # Transfer items from guest cart to user cart
                        for item in guest_cart.items.all():
                            user_item, created = CartItem.objects.get_or_create(
                                cart=user_cart,
                                product=item.product,
                                defaults={'quantity': item.quantity}
                            )
                            if not created:
                                user_item.quantity += item.quantity
                                user_item.save()
                        # Delete guest cart
                        guest_cart.delete()
                except Exception as e:
                    print(f"Error merging cart: {e}")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Signup successful'})
            return redirect('home')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = form.errors.as_json()
                return JsonResponse({'success': False, 'error': errors})
            return render(request, 'signup.html', {'form': form})
    
    form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def logout_user(request):
    if request.method == 'POST':
        logout(request)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Logged out'})
        return redirect('home')
    return redirect('home')

# Cart views
def cart_page(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.all().select_related('product')
    total_cost = cart.total_cost()
    
    return render(request, 'cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'total_cost': total_cost
    })

@require_POST
@csrf_exempt
def add_to_cart(request):
    try:
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        print(f"DEBUG: Adding product {product_id} to cart")
        
        product = get_object_or_404(Product, id=product_id, available=True)
        
        # Check stock
        if product.stock < quantity:
            return JsonResponse({
                'success': False,
                'error': f'Only {product.stock} items available in stock'
            })
        
        cart = get_or_create_cart(request)
        
        # Get or create cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock:
                return JsonResponse({
                    'success': False,
                    'error': f'Cannot add {quantity} more items. Total would exceed available stock.'
                })
            cart_item.quantity = new_quantity
            cart_item.save()
        
        # Get updated cart data
        cart_count = cart.total_items()
        cart_total = cart.total_cost()
        
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart',
            'cart_count': cart_count,
            'cart_total': float(cart_total),
            'item_total': float(cart_item.item_total())
        })
    except Exception as e:
        print(f"ERROR in add_to_cart: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@require_POST
@csrf_exempt
def remove_from_cart(request):
    try:
        item_id = request.POST.get('item_id')
        cart = get_or_create_cart(request)
        
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        product_name = cart_item.product.name
        cart_item.delete()
        
        # Get updated cart data
        cart_count = cart.total_items()
        cart_total = cart.total_cost()
        
        return JsonResponse({
            'success': True,
            'message': f'{product_name} removed from cart',
            'cart_count': cart_count,
            'cart_total': float(cart_total)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

def cart_data(request):
    """Get cart data for AJAX requests"""
    try:
        cart = get_or_create_cart(request)
        cart_items = cart.items.all().select_related('product')
        
        items_data = []
        for item in cart_items:
            product = item.product
            items_data.append({
                'id': item.id,
                'product_id': product.id,
                'name': product.name,
                'price': float(product.final_price),
                'original_price': float(product.price),
                'quantity': item.quantity,
                'image': product.image.url if product.image else '/static/img/default-product.jpg',
                'total': float(item.item_total()),
                'stock': product.stock,
                'in_stock': product.is_in_stock
            })
        
        total = cart.total_cost()
        cart_count = cart.total_items()
        
        return JsonResponse({
            'success': True,
            'count': cart_count,
            'items': items_data,
            'total': float(total),
            'cart_id': cart.id
        })
    except Exception as e:
        print(f"Error in cart_data: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'count': 0,
            'items': [],
            'total': 0
        }, status=500)

@require_POST
@csrf_exempt
def update_cart_quantity(request):
    try:
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity < 1:
            return JsonResponse({
                'success': False,
                'error': 'Quantity must be at least 1'
            })
        
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        # Check stock
        if quantity > cart_item.product.stock:
            return JsonResponse({
                'success': False,
                'error': f'Only {cart_item.product.stock} items available in stock'
            })
        
        cart_item.quantity = quantity
        cart_item.save()
        
        # Recalculate totals
        total_cost = cart.total_cost()
        cart_count = cart.total_items()
        item_total = cart_item.item_total()
        
        return JsonResponse({
            'success': True,
            'message': 'Cart updated',
            'cart_count': cart_count,
            'total': float(total_cost),
            'item_total': float(item_total),
            'quantity': quantity
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

def get_cart_count(request):
    """Get only cart count (lighter than full cart_data)"""
    try:
        cart = get_or_create_cart(request)
        count = cart.total_items()
        return JsonResponse({'success': True, 'count': count})
    except Exception as e:
        return JsonResponse({'success': False, 'count': 0, 'error': str(e)})

@require_POST
@csrf_exempt
def clear_cart(request):
    try:
        cart = get_or_create_cart(request)
        cart.items.all().delete()
        return JsonResponse({'success': True, 'message': 'Cart cleared'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def checkout(request):
    cart = get_or_create_cart(request)
    
    if cart.is_empty():
        return redirect('cart_page')
    
    cart_items = cart.items.all().select_related('product')
    total_cost = cart.total_cost()
    
    # Check stock for all items before checkout
    out_of_stock_items = []
    for item in cart_items:
        if item.quantity > item.product.stock:
            out_of_stock_items.append(item.product.name)
    
    if out_of_stock_items:
        return render(request, 'checkout.html', {
            'cart': cart,
            'cart_items': cart_items,
            'total_cost': total_cost,
            'out_of_stock_items': out_of_stock_items,
            'error': 'Some items are out of stock'
        })
    
    if request.method == 'POST':
        # Process payment here (simplified)
        # In a real app, you would integrate with a payment gateway
        
        # Update stock and clear cart
        with transaction.atomic():
            for item in cart_items:
                item.product.reduce_stock(item.quantity)
            cart.items.all().delete()
        
        return render(request, 'checkout_success.html', {
            'order_total': total_cost,
            'items_count': cart_items.count()
        })
    
    return render(request, 'checkout.html', {
        'cart': cart,
        'cart_items': cart_items,
        'total_cost': total_cost
    })

# Product views
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    images = product.images.all()
    related_products = Product.objects.filter(
        category=product.category, 
        available=True
    ).exclude(id=product_id)[:4]
    
    # Get reviews
    reviews = product.reviews.filter(is_approved=True)
    
    # Check if user has this in wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(
            user=request.user, 
            product=product
        ).exists()
    
    return render(request, 'product_detail.html', {
        'product': product,
        'images': images,
        'related_products': related_products,
        'reviews': reviews,
        'in_wishlist': in_wishlist
    })

# Search views
def search_products(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    products = Product.objects.filter(available=True)
    
    if query:
        products = products.filter(name__icontains=query)
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if min_price:
        try:
            products = products.filter(final_price__gte=Decimal(min_price))
        except:
            pass
    
    if max_price:
        try:
            products = products.filter(final_price__lte=Decimal(max_price))
        except:
            pass
    
    categories = Category.objects.filter(is_active=True)
    
    return render(request, 'search_results.html', {
        'query': query,
        'products': products[:50],
        'categories': categories,
        'selected_category': category_id,
        'min_price': min_price,
        'max_price': max_price
    })

@require_GET
def search_api(request):
    """API endpoint for live search"""
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    products = Product.objects.filter(
        name__icontains=query, 
        available=True
    )[:10]
    
    results = []
    for product in products:
        results.append({
            'id': product.id,
            'name': product.name,
            'price': float(product.final_price),
            'original_price': float(product.price),
            'image': product.image.url if product.image else '',
            'url': f'/product/{product.id}/',
            'in_stock': product.is_in_stock,
            'discount_percentage': product.discount_percentage
        })
    
    return JsonResponse({'results': results})

# API endpoints
@require_GET
def api_products(request):
    """API endpoint to get products for homepage"""
    try:
        products = Product.objects.filter(available=True)[:8]
        
        product_list = []
        for product in products:
            product_list.append({
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'final_price': float(product.final_price) if product.final_price else float(product.price),
                'description': product.description,
                'image': product.image.url if product.image else '/static/img/default-product.jpg',
                'stock': product.stock,
                'is_featured': product.is_featured,
                'is_new': product.is_new,
                'rating': float(product.rating) if product.rating else 0,
                'review_count': product.review_count or 0,
                'discount_percentage': product.discount_percentage
            })
        
        return JsonResponse(product_list, safe=False)
        
    except Exception as e:
        print(f"ERROR in api_products: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

# Static page views
def categories(request):
    categories = Category.objects.filter(is_active=True).prefetch_related('products')
    return render(request, 'categories.html', {'categories': categories})

def brands(request):
    brands = Brand.objects.filter(is_active=True).prefetch_related('products')
    return render(request, 'brands.html', {'brands': brands})

def visual_search(request):
    return render(request, 'visual_search.html')

def api_visual_search(request):
    # This would handle image upload and search
    # For now, return dummy data
    if request.method == 'POST' and request.FILES.get('image'):
        # Process image here
        # For demo, return some products
        products = Product.objects.filter(available=True)[:8]
        results = []
        for product in products:
            results.append({
                'id': product.id,
                'name': product.name,
                'price': float(product.final_price),
                'image': product.image.url if product.image else '',
                'url': f'/product/{product.id}/'
            })
        return JsonResponse({'success': True, 'results': results})
    
    return JsonResponse({'success': False, 'error': 'No image provided'})

def nearby_stores(request):
    stores = Store.objects.filter(is_active=True)
    
    # For demo, show some stores as "nearby"
    nearby_stores = stores.filter(nearby=True)
    other_stores = stores.filter(nearby=False)
    
    return render(request, 'nearby_stores.html', {
        'nearby_stores': nearby_stores,
        'other_stores': other_stores
    })

def deals(request):
    # Get active deals
    active_deals = Deal.objects.filter(is_active=True)
    
    # Get products that are on sale
    sale_products = Product.objects.filter(
        is_on_sale=True, 
        available=True
    )[:12]
    
    return render(request, 'deals.html', {
        'deals': active_deals,
        'sale_products': sale_products
    })

def new_arrivals(request):
    # Get new products
    new_products = Product.objects.filter(
        is_new=True, 
        available=True
    ).order_by('-created_at')[:16]
    
    return render(request, 'new_arrivals.html', {
        'products': new_products
    })

# Wishlist views
@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})

@require_POST
@login_required
@csrf_exempt
def toggle_wishlist(request):
    try:
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        
        # Check if already in wishlist
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if not created:
            # Remove from wishlist
            wishlist_item.delete()
            return JsonResponse({
                'success': True,
                'message': 'Removed from wishlist',
                'in_wishlist': False
            })
        
        return JsonResponse({
            'success': True,
            'message': 'Added to wishlist',
            'in_wishlist': True
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

# Review views
@require_POST
@login_required
@csrf_exempt
def submit_review(request):
    try:
        product_id = request.POST.get('product_id')
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '').strip()
        
        product = get_object_or_404(Product, id=product_id)
        
        # Check if user already reviewed this product
        existing_review = ProductReview.objects.filter(
            user=request.user,
            product=product
        ).first()
        
        if existing_review:
            # Update existing review
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.save()
        else:
            # Create new review
            ProductReview.objects.create(
                user=request.user,
                product=product,
                rating=rating,
                comment=comment,
                is_approved=True  # Auto-approve for demo
            )
        
        # Update product rating
        reviews = product.reviews.filter(is_approved=True)
        if reviews.exists():
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            product.rating = round(avg_rating, 2)
            product.review_count = reviews.count()
            product.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Review submitted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

# Category products view
def category_products(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    products = Product.objects.filter(category=category, available=True)
    
    # Apply filters
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort_by = request.GET.get('sort', '')
    
    if min_price:
        try:
            products = products.filter(final_price__gte=Decimal(min_price))
        except:
            pass
    
    if max_price:
        try:
            products = products.filter(final_price__lte=Decimal(max_price))
        except:
            pass
    
    if sort_by == 'price_asc':
        products = products.order_by('final_price')
    elif sort_by == 'price_desc':
        products = products.order_by('-final_price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'popular':
        products = products.order_by('-sold_count')
    
    return render(request, 'category_products.html', {
        'category': category,
        'products': products,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by
    })

# Brand products view
def brand_products(request, brand_slug):
    brand = get_object_or_404(Brand, slug=brand_slug, is_active=True)
    products = Product.objects.filter(brand=brand, available=True)
    
    return render(request, 'brand_products.html', {
        'brand': brand,
        'products': products
    })

# Debug view
@require_GET
def debug_products(request):
    """Debug endpoint to check products"""
    products = Product.objects.all()
    data = {
        'count': products.count(),
        'products': list(products.values('id', 'name', 'price', 'stock'))
    }
    return JsonResponse(data)