"""Script to train the threat detection ML model."""
import sys
sys.path.append('.')

from app.services.threat_detector import ThreatDetector

if __name__ == "__main__":
    print("=" * 60)
    print("Threat Detection Model Training")
    print("=" * 60)
    
    detector = ThreatDetector()
    
    # Train with 10,000 synthetic samples
    results = detector.train_model(num_samples=10000)
    
    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
    print(f"Total samples: {results['samples']}")
    print(f"Model saved and ready for use")
