#!/usr/bin/env python3
"""
Data Analysis Template
A basic template for data analysis projects
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Set up plotting style
plt.style.use('default')
sns.set_palette("husl")

class DataAnalyzer:
    """A class to handle common data analysis tasks"""
    
    def __init__(self, data_path: str = None):
        """Initialize with optional data path"""
        self.data = None
        self.data_path = data_path
        
        if data_path:
            self.load_data(data_path)
    
    def load_data(self, file_path: str):
        """Load data from various file formats"""
        file_path = Path(file_path)
        
        if file_path.suffix.lower() == '.csv':
            self.data = pd.read_csv(file_path)
        elif file_path.suffix.lower() in ['.xlsx', '.xls']:
            self.data = pd.read_excel(file_path)
        elif file_path.suffix.lower() == '.json':
            self.data = pd.read_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        print(f"✓ Loaded data from {file_path}")
        print(f"  Shape: {self.data.shape}")
    
    def basic_info(self):
        """Display basic information about the dataset"""
        if self.data is None:
            print("No data loaded yet!")
            return
        
        print("=== BASIC DATASET INFORMATION ===")
        print(f"Shape: {self.data.shape}")
        print(f"Memory usage: {self.data.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        print("\n=== DATA TYPES ===")
        print(self.data.dtypes)
        
        print("\n=== MISSING VALUES ===")
        missing = self.data.isnull().sum()
        missing_percent = (missing / len(self.data)) * 100
        missing_df = pd.DataFrame({
            'Missing Count': missing,
            'Percentage': missing_percent
        }).sort_values('Missing Count', ascending=False)
        print(missing_df[missing_df['Missing Count'] > 0])
    
    def explore_numerical(self):
        """Explore numerical columns"""
        if self.data is None:
            print("No data loaded yet!")
            return
        
        numerical_cols = self.data.select_dtypes(include=[np.number]).columns
        
        if len(numerical_cols) == 0:
            print("No numerical columns found!")
            return
        
        print("=== NUMERICAL COLUMNS SUMMARY ===")
        print(self.data[numerical_cols].describe())
        
        # Create histograms
        n_cols = min(4, len(numerical_cols))
        n_rows = (len(numerical_cols) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4*n_rows))
        axes = axes.flatten() if n_rows * n_cols > 1 else [axes]
        
        for i, col in enumerate(numerical_cols):
            if i < len(axes):
                axes[i].hist(self.data[col].dropna(), bins=30, alpha=0.7)
                axes[i].set_title(f'Distribution of {col}')
                axes[i].set_xlabel(col)
                axes[i].set_ylabel('Frequency')
        
        # Hide empty subplots
        for i in range(len(numerical_cols), len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        plt.show()
    
    def explore_categorical(self):
        """Explore categorical columns"""
        if self.data is None:
            print("No data loaded yet!")
            return
        
        categorical_cols = self.data.select_dtypes(include=['object', 'category']).columns
        
        if len(categorical_cols) == 0:
            print("No categorical columns found!")
            return
        
        print("=== CATEGORICAL COLUMNS SUMMARY ===")
        for col in categorical_cols:
            print(f"\n{col}:")
            print(f"  Unique values: {self.data[col].nunique()}")
            print(f"  Top 5 values:")
            print(self.data[col].value_counts().head())
    
    def correlation_matrix(self):
        """Display correlation matrix for numerical columns"""
        if self.data is None:
            print("No data loaded yet!")
            return
        
        numerical_cols = self.data.select_dtypes(include=[np.number]).columns
        
        if len(numerical_cols) < 2:
            print("Need at least 2 numerical columns for correlation matrix!")
            return
        
        plt.figure(figsize=(10, 8))
        correlation_matrix = self.data[numerical_cols].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
        plt.title('Correlation Matrix')
        plt.tight_layout()
        plt.show()
    
    def quick_analysis(self):
        """Run a quick comprehensive analysis"""
        print("=== QUICK DATA ANALYSIS ===")
        self.basic_info()
        print("\n")
        self.explore_numerical()
        self.explore_categorical()
        self.correlation_matrix()

def main():
    """Main function for standalone execution"""
    # Example usage
    analyzer = DataAnalyzer()
    
    # If you have a data file, uncomment and modify this line:
    # analyzer.load_data("path/to/your/data.csv")
    
    # Create sample data for demonstration
    np.random.seed(42)
    sample_data = pd.DataFrame({
        'age': np.random.randint(18, 80, 1000),
        'income': np.random.normal(50000, 15000, 1000),
        'category': np.random.choice(['A', 'B', 'C'], 1000),
        'score': np.random.normal(75, 10, 1000)
    })
    
    analyzer.data = sample_data
    print("✓ Created sample dataset for demonstration")
    
    # Run analysis
    analyzer.quick_analysis()

if __name__ == "__main__":
    main()
