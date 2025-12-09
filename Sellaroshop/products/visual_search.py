import cv2
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image
import io

class VisualSearchEngine:
    def __init__(self):
        self.feature_size = 512  # Reduced feature size
    
    def extract_features(self, image_array):
        """Extract simplified features from image"""
        if image_array is None:
            return None
            
        try:
            # Convert to grayscale for simplicity
            if len(image_array.shape) == 3:
                gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
            else:
                gray = image_array
            
            # Resize image
            resized = cv2.resize(gray, (64, 64))
            
            # Simple feature extraction using histogram and resized pixels
            hist_features = cv2.calcHist([resized], [0], None, [32], [0, 256]).flatten()
            pixel_features = resized.flatten() / 255.0  # Normalize
            
            # Combine features
            features = np.concatenate([hist_features, pixel_features])
            
            # Ensure consistent feature size
            if len(features) > self.feature_size:
                features = features[:self.feature_size]
            else:
                features = np.pad(features, (0, self.feature_size - len(features)))
            
            return features
            
        except Exception as e:
            print(f"Feature extraction error: {e}")
            return None
    
    def calculate_similarity(self, features1, features2):
        """Calculate cosine similarity between two feature vectors"""
        if features1 is None or features2 is None:
            return 0
        
        try:
            # Ensure both feature vectors have the same length
            min_len = min(len(features1), len(features2))
            features1 = features1[:min_len]
            features2 = features2[:min_len]
            
            return cosine_similarity([features1], [features2])[0][0]
        except Exception as e:
            print(f"Similarity calculation error: {e}")
            return 0

# Global instance
search_engine = VisualSearchEngine()
