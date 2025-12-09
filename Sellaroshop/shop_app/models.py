# models.py - CORRECTED VERSION (no circular imports)
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal

# Get the User model
User = get_user_model()

# ==============================
# Category Model
# ==============================
class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    @property
    def product_count(self):
        return self.products.filter(available=True).count()


# ==============================
# Brand Model
# ==============================
class Brand(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    @property
    def product_count(self):
        return self.products.filter(available=True).count()


# ==============================
# Store Model
# ==============================
class Store(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=300)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    nearby = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


# ==============================
# Product Model
# ==============================
class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    discount_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        blank=True, 
        null=True,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    is_on_sale = models.BooleanField(default=False)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)
    sold_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Auto-set is_on_sale if discount_price exists
        if self.discount_price and self.discount_price < self.price:
            self.is_on_sale = True
        else:
            self.is_on_sale = False
            
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    @property
    def final_price(self):
        """Returns the discounted price if on sale, otherwise regular price"""
        if self.is_on_sale and self.discount_price:
            return self.discount_price
        return self.price
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if on sale"""
        if self.is_on_sale and self.discount_price and self.price > 0:
            discount = ((self.price - self.discount_price) / self.price) * 100
            return round(discount)
        return 0
    
    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        return self.stock > 0
    
    def reduce_stock(self, quantity):
        """Reduce stock quantity"""
        if self.stock >= quantity:
            self.stock -= quantity
            self.sold_count += quantity
            self.save()
            return True
        return False
    
    def increase_stock(self, quantity):
        """Increase stock quantity"""
        self.stock += quantity
        self.save()


# ==============================
# Product Image Model
# ==============================
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/images/')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'created_at']

    def __str__(self):
        return f"Image for {self.product.name}"


# ==============================
# Deal Model
# ==============================
class Deal(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='deals')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    discount_percentage = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.title} ({self.product.name})"
    
    @property
    def is_live(self):
        """Check if deal is currently active"""
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date


# ==============================
# Cart Model
# ==============================
class Cart(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='carts', 
        null=True, 
        blank=True
    )
    session_key = models.CharField(max_length=200, null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        if self.user:
            return f"{self.user.username}'s Cart"
        return f"Guest Cart {self.session_key}"
    
    def total_items(self):
        """Total number of items in cart"""
        return sum(item.quantity for item in self.items.all())
    
    def total_cost(self):
        """Total cost of all items in cart"""
        total = 0
        for item in self.items.all():
            total += item.item_total()
        return round(total, 2)
    
    def is_empty(self):
        """Check if cart is empty"""
        return self.items.count() == 0


# ==============================
# CartItem Model
# ==============================
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['cart', 'product']
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def item_total(self):
        """Total price for this cart item"""
        return self.product.final_price * self.quantity


# ==============================
# Wishlist Model
# ==============================
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


# ==============================
# Product Review Model
# ==============================
class ProductReview(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=5)
    comment = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating} Stars"