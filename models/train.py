"""Model training CLI."""

import click
import pandas as pd
from pathlib import Path

from utils.config import load_config
from utils.logger import setup_logger
from models import ProjectRiskModel, CostOverrunPredictor, SuccessLikelihoodModel, PortfolioOptimizer

logger = setup_logger(__name__)


@click.command()
@click.option('--model', required=True, type=click.Choice(['prm', 'cop', 'slm', 'po']), help='Model to train')
@click.option('--data', required=True, help='Path to training data CSV')
@click.option('--target', help='Target column name (optional, uses default)')
@click.option('--output-dir', default='models/artifacts', help='Output directory for trained model')
def train(model: str, data: str, target: str, output_dir: str):
    """Train a portfolio ML model."""
    
    logger.info(f"Starting training for {model}...")
    
    # Load config
    config = load_config()
    
    # Load data
    data_path = Path(data)
    if not data_path.exists():
        logger.error(f"Data file not found: {data}")
        return
    
    df = pd.read_csv(data_path)
    logger.info(f"Loaded {len(df)} rows from {data}")
    
    # Initialize model
    model_classes = {
        'prm': ProjectRiskModel,
        'cop': CostOverrunPredictor,
        'slm': SuccessLikelihoodModel,
        'po': PortfolioOptimizer
    }
    
    model_instance = model_classes[model](config)
    
    # Set default target columns
    default_targets = {
        'prm': 'risk_level',
        'cop': 'cost_overrun_pct',
        'slm': 'project_success',
        'po': None  # Optimizer doesn't train on data
    }
    
    target_col = target or default_targets[model]
    
    # Train model
    if model == 'po':
        logger.info("Portfolio Optimizer does not require training")
        results = {"message": "No training required for optimizer"}
    else:
        if target_col not in df.columns:
            logger.error(f"Target column '{target_col}' not found in data")
            return
        
        results = model_instance.train(df, target_column=target_col)
        
        # Save model
        model_instance.save_model(output_dir)
        logger.info(f"Model saved to {output_dir}/{model}/")
    
    # Print results
    logger.info("Training completed!")
    logger.info(f"Results: {results}")


def main():
    """Entry point for training."""
    train()


if __name__ == "__main__":
    main()
