# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_user, name='logout'),
    
    # Search
    path('search/', views.search_products, name='search'),
    path('api/search/', views.search_api, name='search_api'),
    
    # Cart
    path('cart/', views.cart_page, name='cart_page'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path('cart-data/', views.cart_data, name='cart_data'),
    path('update-cart-quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    path('get-cart-count/', views.get_cart_count, name='get_cart_count'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),
    
    # Product
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    
    # Category and Brand
    path('category/<slug:category_slug>/', views.category_products, name='category_products'),
    path('brand/<slug:brand_slug>/', views.brand_products, name='brand_products'),
    
    # Wishlist
    path('wishlist/', views.wishlist, name='wishlist'),
    path('toggle-wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
    
    # Reviews
    path('submit-review/', views.submit_review, name='submit_review'),
    
    # Static pages
    path('categories/', views.categories, name='categories'),
    path('brands/', views.brands, name='brands'),
    path('visual-search/', views.visual_search, name='visual_search'),
    path('api-visual-search/', views.api_visual_search, name='api_visual_search'),
    path('nearby-stores/', views.nearby_stores, name='nearby_stores'),
    path('deals/', views.deals, name='deals'),
    path('new-arrivals/', views.new_arrivals, name='new_arrivals'),
]