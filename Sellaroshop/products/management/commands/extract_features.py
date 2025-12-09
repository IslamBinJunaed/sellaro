from django.core.management.base import BaseCommand
from products.models import Product
from products.visual_search import search_engine
import cv2

class Command(BaseCommand):
    help = 'Extract visual features for all products'
    
    def handle(self, *args, **options):
        products = Product.objects.filter(is_active=True)
        processed = 0
        errors = 0
        
        self.stdout.write(f"Starting feature extraction for {products.count()} products...")
        
        for product in products:
            if product.image and not product.feature_vector:
                try:
                    image_path = product.image.path
                    image = cv2.imread(image_path)
                    
                    if image is not None:
                        features = search_engine.extract_features(image)
                        
                        if features is not None:
                            product.feature_vector = features.tobytes()
                            product.save()
                            processed += 1
                            self.stdout.write(
                                self.style.SUCCESS(f'✓ Processed: {product.name}')
                            )
                        else:
                            errors += 1
                            self.stdout.write(
                                self.style.WARNING(f'✗ Feature extraction failed: {product.name}')
                            )
                    else:
                        errors += 1
                        self.stdout.write(
                            self.style.ERROR(f'✗ Cannot read image: {product.name}')
                        )
                
                except Exception as e:
                    errors += 1
                    self.stdout.write(
                        self.style.ERROR(f'✗ Error processing {product.name}: {str(e)}')
                    )
            else:
                if not product.image:
                    self.stdout.write(
                        self.style.WARNING(f'⚠ No image for: {product.name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠ Features already extracted for: {product.name}')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nFeature extraction completed!\nProcessed: {processed}, Errors: {errors}'
            )
        )
        