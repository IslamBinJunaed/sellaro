# admin.py - FIXED VERSION
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Brand, Store, Product, 
    ProductImage, Deal, Cart, CartItem,
    Wishlist, ProductReview
)


# ==============================
# SIMPLE ADMIN (NO INLINES THAT CAUSE CIRCULAR IMPORTS)
# ==============================

# Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')


# Brand Admin
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')


# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price', 'stock', 'available', 'image_tag')
    list_filter = ('available', 'category', 'brand', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'image_tag')
    prepopulated_fields = {'slug': ('name',)}
    
    def image_tag(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No image"
    image_tag.short_description = 'Image'


# Deal Admin
@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ('title', 'product', 'start_date', 'end_date', 'is_active', 'created_at')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('title', 'description', 'product__name')
    readonly_fields = ('created_at', 'updated_at')


# Store Admin
@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'nearby', 'is_active', 'created_at')
    search_fields = ('name', 'location', 'phone', 'email')
    list_filter = ('nearby', 'is_active', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


# Cart Admin
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user', 'created_at')
    list_filter = ('created_at',)
    
    def get_user(self, obj):
        if obj.user:
            return obj.user.username
        return f"Guest ({obj.session_key})"
    get_user.short_description = 'User'


# CartItem Admin
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'added_at')
    list_filter = ('added_at',)


# ProductImage Admin
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_primary', 'created_at')
    list_filter = ('is_primary', 'created_at')


# Wishlist Admin
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    list_filter = ('added_at',)


# ProductReview Admin
@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at')
    readonly_fields = ('created_at', 'updated_at')