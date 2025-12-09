from django.contrib import admin
from .models import Product, Category, Brand

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'brand', 'price', 'stock', 'is_active', 'has_features']
    list_filter = ['category', 'brand', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['price', 'stock', 'is_active']
    
    def has_features(self, obj):
        return obj.feature_vector is not None
    has_features.boolean = True
    has_features.short_description = 'Features Extracted'
    