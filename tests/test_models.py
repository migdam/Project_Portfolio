"""Tests for ML models."""

import pytest
import pandas as pd
import numpy as np

from models import ProjectRiskModel, CostOverrunPredictor, SuccessLikelihoodModel, PortfolioOptimizer
from utils.config import load_config


@pytest.fixture
def config():
    """Load configuration."""
    return load_config()


@pytest.fixture
def sample_project_data():
    """Create sample project data for testing."""
    np.random.seed(42)
    n_samples = 100
    
    data = {
        'project_id': range(n_samples),
        'scope_change_frequency': np.random.uniform(0, 1, n_samples),
        'milestone_variance': np.random.uniform(0, 10, n_samples),
        'team_experience_score': np.random.uniform(1, 10, n_samples),
        'dependency_count': np.random.randint(0, 20, n_samples),
        'vendor_risk_score': np.random.uniform(0, 100, n_samples),
        'budget_utilization': np.random.uniform(0.5, 1.5, n_samples),
        'phase_duration': np.random.randint(30, 365, n_samples),
        'risk_level': np.random.choice(['low', 'medium', 'high', 'critical'], n_samples),
        'cost_overrun_pct': np.random.uniform(-0.2, 0.5, n_samples),
        'project_success': np.random.choice([0, 1], n_samples)
    }
    
    return pd.DataFrame(data)


def test_project_risk_model_initialization(config):
    """Test PRM initialization."""
    model = ProjectRiskModel(config)
    assert model.model_name == "prm"
    assert not model.is_trained
    assert len(model.feature_names) > 0


def test_project_risk_model_training(config, sample_project_data):
    """Test PRM training."""
    model = ProjectRiskModel(config)
    results = model.train(sample_project_data, target_column='risk_level')
    
    assert model.is_trained
    assert 'accuracy' in results
    assert 'f1_score' in results
    assert results['accuracy'] >= 0  # Should be non-negative


def test_cost_overrun_predictor_initialization(config):
    """Test COP initialization."""
    model = CostOverrunPredictor(config)
    assert model.model_name == "cop"
    assert not model.is_trained


def test_success_likelihood_model_initialization(config):
    """Test SLM initialization."""
    model = SuccessLikelihoodModel(config)
    assert model.model_name == "slm"
    assert not model.is_trained


def test_portfolio_optimizer_optimization(config, sample_project_data):
    """Test Portfolio Optimizer."""
    # Add required columns for optimizer
    sample_project_data['strategic_value_score'] = np.random.uniform(1, 100, len(sample_project_data))
    sample_project_data['project_npv'] = np.random.uniform(100000, 1000000, len(sample_project_data))
    sample_project_data['resource_requirements'] = np.random.uniform(1, 50, len(sample_project_data))
    sample_project_data['risk_score'] = np.random.uniform(0, 100, len(sample_project_data))
    
    model = PortfolioOptimizer(config)
    assert model.is_trained  # Optimizer doesn't require training
    
    results = model.optimize(
        sample_project_data,
        budget_constraint=5000000,
        resource_constraint=200
    )
    
    assert results['success']
    assert 'selected_projects' in results
    assert 'total_value' in results
    assert 'value_cost_ratio' in results


def test_model_save_load(config, sample_project_data, tmp_path):
    """Test model save and load."""
    model = ProjectRiskModel(config)
    model.train(sample_project_data, target_column='risk_level')
    
    # Save model
    model.save_model(str(tmp_path))
    assert (tmp_path / "prm" / "model.joblib").exists()
    
    # Load model
    new_model = ProjectRiskModel(config)
    new_model.load_model(str(tmp_path))
    assert new_model.is_trained
    
    # Test predictions
    test_data = sample_project_data.head(10)
    predictions = new_model.predict(test_data)
    assert len(predictions) == 10


def test_prediction_with_confidence(config, sample_project_data):
    """Test predictions with confidence scores."""
    model = ProjectRiskModel(config)
    model.train(sample_project_data, target_column='risk_level')
    
    test_data = sample_project_data.head(10)
    predictions, confidences = model.predict_with_confidence(test_data)
    
    assert len(predictions) == len(test_data)
    assert len(confidences) == len(test_data)
    assert all(0 <= c <= 1 for c in confidences)
