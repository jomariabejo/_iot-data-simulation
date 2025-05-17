import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
from datetime import datetime
import json
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

class LogisticsAnalyzer:
    def __init__(self, json_file: str = "logistics_data.json", csv_file: str = "logistics_data.csv"):
        """Initialize the analyzer with data files."""
        self.data_dir = "data"
        self.json_file = os.path.join(self.data_dir, json_file)
        self.csv_file = os.path.join(self.data_dir, csv_file)
        self.df = None
        self.json_data = None
        self.load_data()
        
    def load_data(self):
        """Load data from both JSON and CSV files."""
        try:
            # Load JSON data
            with open(self.json_file, 'r') as f:
                self.json_data = json.load(f)
            
            # Load CSV data
            self.df = pd.read_csv(self.csv_file)
            print("Data loaded successfully!")
        except FileNotFoundError:
            print("Please run generate_logistics_data.py first to create the dataset.")
            raise

    def get_basic_stats(self) -> Dict:
        """Get basic statistics about the dataset."""
        stats = {
            "total_packages": len(self.df),
            "delivery_status_counts": self.df['status'].value_counts().to_dict(),
            "package_type_distribution": self.df['package_type'].value_counts().to_dict(),
            "avg_weight": self.df['weight_kg'].mean(),
            "avg_dimensions": {
                "length": self.df['length_cm'].mean(),
                "width": self.df['width_cm'].mean(),
                "height": self.df['height_cm'].mean()
            }
        }
        return stats

    def sample_data(self, n_samples: int = 5, random_state: int = 42) -> pd.DataFrame:
        """Sample n records from the dataset."""
        return self.df.sample(n=n_samples, random_state=random_state)

    def analyze_delivery_times(self) -> Dict:
        """Analyze delivery times and delays."""
        # Convert string timestamps to datetime
        self.df['estimated_delivery'] = pd.to_datetime(self.df['estimated_delivery'])
        self.df['actual_delivery'] = pd.to_datetime(self.df['actual_delivery'])
        
        # Calculate delivery delays
        delivered_packages = self.df[self.df['status'] == 'Delivered']
        delays = (delivered_packages['actual_delivery'] - delivered_packages['estimated_delivery']).dt.total_seconds() / 3600  # in hours
        
        return {
            "avg_delay_hours": delays.mean(),
            "max_delay_hours": delays.max(),
            "min_delay_hours": delays.min(),
            "on_time_delivery_percentage": (delays <= 0).mean() * 100
        }

    def plot_delivery_status_distribution(self):
        """Plot the distribution of delivery statuses."""
        plt.figure(figsize=(10, 6))
        sns.countplot(data=self.df, x='status')
        plt.title('Distribution of Package Statuses')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(self.data_dir, 'delivery_status_distribution.png'))
        plt.close()

    def plot_package_type_distribution(self):
        """Plot the distribution of package types."""
        plt.figure(figsize=(10, 6))
        sns.countplot(data=self.df, x='package_type')
        plt.title('Distribution of Package Types')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(self.data_dir, 'package_type_distribution.png'))
        plt.close()

    def plot_weight_distribution(self):
        """Plot the distribution of package weights."""
        plt.figure(figsize=(10, 6))
        sns.histplot(data=self.df, x='weight_kg', bins=20)
        plt.title('Distribution of Package Weights')
        plt.xlabel('Weight (kg)')
        plt.tight_layout()
        plt.savefig(os.path.join(self.data_dir, 'weight_distribution.png'))
        plt.close()

    def train_delivery_prediction_model(self) -> Tuple[RandomForestClassifier, float]:
        """Train a model to predict delivery status."""
        # Prepare features
        features = ['weight_kg', 'length_cm', 'width_cm', 'height_cm']
        X = self.df[features]
        
        # Encode target variable
        le = LabelEncoder()
        y = le.fit_transform(self.df['status'])
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Calculate accuracy
        accuracy = model.score(X_test, y_test)
        
        return model, accuracy

    def generate_report(self):
        """Generate a comprehensive analysis report."""
        print("\n=== Logistics Data Analysis Report ===")
        
        # Basic Statistics
        stats = self.get_basic_stats()
        print("\nBasic Statistics:")
        print(f"Total Packages: {stats['total_packages']}")
        print("\nDelivery Status Distribution:")
        for status, count in stats['delivery_status_counts'].items():
            print(f"{status}: {count}")
        
        # Delivery Time Analysis
        delivery_times = self.analyze_delivery_times()
        print("\nDelivery Time Analysis:")
        print(f"Average Delay: {delivery_times['avg_delay_hours']:.2f} hours")
        print(f"On-time Delivery Rate: {delivery_times['on_time_delivery_percentage']:.2f}%")
        
        # Generate plots
        self.plot_delivery_status_distribution()
        self.plot_package_type_distribution()
        self.plot_weight_distribution()
        
        # Train and evaluate prediction model
        model, accuracy = self.train_delivery_prediction_model()
        print(f"\nDelivery Status Prediction Model Accuracy: {accuracy:.2f}")
        
        print("\nAnalysis complete! Check the generated plots in the data folder.")

def main():
    try:
        analyzer = LogisticsAnalyzer()
        
        # Generate sample data
        print("\nSample Data:")
        print(analyzer.sample_data(n_samples=3))
        
        # Generate full report
        analyzer.generate_report()
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 