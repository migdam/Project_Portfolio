# 🏗️ Architecture Documentation

## System Architecture

```mermaid
graph TB
    subgraph "Data Layer"
        A[PPM System]
        B[Finance System]
        C[HR System]
        D[Risk Logs]
    end
    
    subgraph "Ingestion"
        E[Data Ingestion]
        A --> E
        B --> E
        C --> E
        D --> E
    end
    
    subgraph "Pipeline"
        F[Preprocessing]
        G[Feature Engineering]
        H[Validation]
        E --> F
        F --> G
        G --> H
    end
    
    subgraph "ML Models"
        I[PRM]
        J[COP]
        K[SLM]
        L[PO]
        H --> I
        H --> J
        H --> K
        H --> L
    end
    
    subgraph "API Layer"
        M[FastAPI]
        I --> M
        J --> M
        K --> M
        L --> M
    end
    
    subgraph "Monitoring"
        N[Drift Detection]
        O[Health Checks]
        P[Retraining]
        I --> N
        J --> N
        K --> N
        N --> P
        O --> P
        P --> I
        P --> J
        P --> K
    end
    
    subgraph "Applications"
        Q[Dashboard]
        R[Batch Jobs]
        S[Notebooks]
        M --> Q
        M --> R
        M --> S
    end
```

## ML Pipeline Flow

```mermaid
sequenceDiagram
    participant D as Data Sources
    participant P as Pipeline
    participant M as ML Models
    participant API as API
    participant U as Users
    
    D->>P: Raw Data
    P->>P: Clean & Transform
    P->>P: Feature Engineering
    P->>P: Validate Quality
    P->>M: Training Data
    M->>M: Train Models
    M->>M: Cross-Validate
    M->>API: Deploy Models
    U->>API: Request Prediction
    API->>M: Get Prediction
    M->>API: Return Result
    API->>U: Prediction + Explanation
```

## Model Training Workflow

```mermaid
flowchart LR
    A[Data Collection] --> B{Quality Check}
    B -->|Pass| C[Feature Engineering]
    B -->|Fail| A
    C --> D[Model Training]
    D --> E{Performance Check}
    E -->|Good| F[Save Model]
    E -->|Poor| G[Hyperparameter Tuning]
    G --> D
    F --> H[Deploy to Production]
    H --> I[Monitor Performance]
    I --> J{Drift Detected?}
    J -->|Yes| A
    J -->|No| I
```

## Component Interaction

```
┌─────────────────────────────────────────────────────────┐
│                    Portfolio ML System                   │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │   PRM    │  │   COP    │  │   SLM    │  │   PO    │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬────┘ │
│       │             │              │             │      │
│       └─────────────┴──────────────┴─────────────┘      │
│                           │                              │
│                      ┌────▼────┐                         │
│                      │ FastAPI │                         │
│                      └────┬────┘                         │
│                           │                              │
│       ┌───────────────────┼───────────────────┐          │
│       │                   │                   │          │
│  ┌────▼─────┐      ┌──────▼──────┐    ┌──────▼──────┐  │
│  │Dashboard │      │Batch Predict│    │Explainability│  │
│  └──────────┘      └─────────────┘    └─────────────┘  │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

## Data Flow

```
Raw Data → Ingestion → Cleaning → Feature Engineering → Validation
    ↓
Training Data → Model Training → Cross-Validation → Model Saving
    ↓
Production Model → Predictions → Explanations → Audit Logs
    ↓
Monitoring → Drift Detection → Alerts → Retraining (if needed)
```

## Deployment Architecture

```
┌─────────────────┐
│   GitHub Repo   │
└────────┬────────┘
         │
    ┌────▼────┐
    │GitHub   │
    │Actions  │
    └────┬────┘
         │
    ┌────▼────────┐
    │Build & Test │
    └────┬────────┘
         │
    ┌────▼─────┐
    │  Docker  │
    │  Image   │
    └────┬─────┘
         │
    ┌────▼──────────┐
    │  Kubernetes   │
    │  Deployment   │
    └───────────────┘
```
