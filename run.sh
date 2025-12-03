#!/bin/bash
# Portfolio ML automation script

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if conda environment is active
check_environment() {
    if [[ -z "$CONDA_DEFAULT_ENV" ]]; then
        print_warning "No conda environment active"
        print_status "Activate environment with: conda activate project_portfolio"
        return 1
    fi
    print_status "Using conda environment: $CONDA_DEFAULT_ENV"
    return 0
}

# Setup command: Install dependencies
setup() {
    print_status "Setting up project..."
    
    # Create directories
    mkdir -p data/{raw,processed,validated}
    mkdir -p models/artifacts
    mkdir -p logs
    mkdir -p reports
    
    # Create placeholder files
    touch data/raw/.gitkeep
    touch data/processed/.gitkeep
    touch data/validated/.gitkeep
    
    # Install dependencies
    if check_environment; then
        print_status "Installing dependencies..."
        pip install -e .
        print_status "✓ Setup complete"
    else
        print_error "Please activate conda environment first"
        exit 1
    fi
}

# Test command: Run pytest
test() {
    print_status "Running tests..."
    check_environment || exit 1
    
    pytest tests/ -v --cov=. --cov-report=html
    print_status "✓ Tests complete. Coverage report: htmlcov/index.html"
}

# Lint command: Run code quality checks
lint() {
    print_status "Running linters..."
    check_environment || exit 1
    
    print_status "Running black..."
    black --check .
    
    print_status "Running flake8..."
    flake8 . --max-line-length=100 --exclude=venv,env,.venv,.git,__pycache__
    
    print_status "✓ Lint checks complete"
}

# Format command: Auto-format code
format() {
    print_status "Formatting code..."
    check_environment || exit 1
    
    black .
    print_status "✓ Code formatted"
}

# Train command: Train a model
train() {
    print_status "Training model..."
    check_environment || exit 1
    
    if [[ -z "$2" ]] || [[ -z "$3" ]]; then
        print_error "Usage: ./run.sh train <model> <data_file>"
        print_error "Models: prm, cop, slm, po"
        exit 1
    fi
    
    python -m models.train --model "$2" --data "$3"
    print_status "✓ Training complete"
}

# Monitor command: Check model health
monitor() {
    print_status "Checking model health..."
    check_environment || exit 1
    
    python -m monitoring.health_check
    print_status "✓ Health check complete"
}

# Deploy command: Deploy to environment
deploy() {
    ENV="${2:-staging}"
    print_status "Deploying to $ENV..."
    check_environment || exit 1
    
    if [[ "$ENV" == "production" ]]; then
        print_warning "Deploying to PRODUCTION"
        read -p "Are you sure? (yes/no): " confirm
        if [[ "$confirm" != "yes" ]]; then
            print_error "Deployment cancelled"
            exit 1
        fi
    fi
    
    print_status "Building Docker image..."
    docker build -t portfolio-ml:$ENV .
    
    print_status "✓ Deployment to $ENV complete"
}

# Help command
help() {
    cat << EOF
Portfolio ML - Automation Script

Usage: ./run.sh <command> [options]

Commands:
    setup               Install dependencies and create directories
    test                Run pytest test suite
    lint                Run code quality checks (black, flake8)
    format              Auto-format code with black
    train MODEL DATA    Train a model (prm/cop/slm/po) with data file
    monitor             Check model health and performance
    deploy [ENV]        Deploy to environment (staging/production)
    help                Show this help message

Examples:
    ./run.sh setup
    ./run.sh train prm data/processed/projects.csv
    ./run.sh test
    ./run.sh deploy staging

EOF
}

# Main command router
case "$1" in
    setup)
        setup
        ;;
    test)
        test
        ;;
    lint)
        lint
        ;;
    format)
        format
        ;;
    train)
        train "$@"
        ;;
    monitor)
        monitor
        ;;
    deploy)
        deploy "$@"
        ;;
    help|--help|-h|"")
        help
        ;;
    *)
        print_error "Unknown command: $1"
        help
        exit 1
        ;;
esac
