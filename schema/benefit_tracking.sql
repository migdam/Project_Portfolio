-- Benefit Intelligence Loop - Database Schema
-- Tracks planned vs realized benefits for portfolio projects

-- ============================================================================
-- BENEFIT PLANS
-- Stores planned/projected benefits from business cases
-- ============================================================================
CREATE TABLE IF NOT EXISTS benefit_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    benefit_category TEXT NOT NULL,  -- Revenue, CostSavings, Productivity, RiskReduction, Strategic
    benefit_subcategory TEXT,        -- e.g., "Automation", "Process Efficiency"
    planned_amount REAL NOT NULL,    -- Dollar value
    planned_timeline TEXT,            -- e.g., "Q2-2024", "Month 6-12"
    baseline_date DATE NOT NULL,      -- When benefit plan was created
    expected_start_date DATE,         -- When benefits should start
    expected_full_date DATE,          -- When benefits fully realized
    assumptions TEXT,                 -- Key assumptions for benefit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, benefit_category, benefit_subcategory)
);

CREATE INDEX IF NOT EXISTS idx_benefit_plans_project ON benefit_plans(project_id);
CREATE INDEX IF NOT EXISTS idx_benefit_plans_category ON benefit_plans(benefit_category);

-- ============================================================================
-- BENEFIT ACTUALS
-- Stores realized/actual benefits from post-implementation tracking
-- ============================================================================
CREATE TABLE IF NOT EXISTS benefit_actuals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    benefit_category TEXT NOT NULL,
    benefit_subcategory TEXT,
    actual_amount REAL NOT NULL,      -- Actual dollar value delivered
    realization_date DATE NOT NULL,   -- When benefit was realized
    evidence_source TEXT,             -- Finance extract, survey, audit, manual
    evidence_url TEXT,                -- Link to supporting documentation
    confidence_score REAL DEFAULT 0.8,-- 0-1 confidence in measurement
    measurement_method TEXT,          -- How benefit was measured
    notes TEXT,                       -- Additional context
    recorded_by TEXT,                 -- User who recorded
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES benefit_plans(project_id)
);

CREATE INDEX IF NOT EXISTS idx_benefit_actuals_project ON benefit_actuals(project_id);
CREATE INDEX IF NOT EXISTS idx_benefit_actuals_category ON benefit_actuals(benefit_category);
CREATE INDEX IF NOT EXISTS idx_benefit_actuals_date ON benefit_actuals(realization_date);

-- ============================================================================
-- BENEFIT VARIANCE HISTORY
-- Tracks variance snapshots over time for trend analysis
-- ============================================================================
CREATE TABLE IF NOT EXISTS benefit_variance_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    benefit_category TEXT NOT NULL,
    snapshot_date DATE NOT NULL,
    planned_amount REAL NOT NULL,
    actual_amount REAL NOT NULL,
    variance_amount REAL NOT NULL,    -- actual - planned
    variance_pct REAL NOT NULL,       -- (actual - planned) / planned * 100
    realization_rate REAL NOT NULL,   -- actual / planned * 100
    benefit_lag_months INTEGER,       -- Months delayed from plan
    status TEXT,                      -- OnTrack, AtRisk, Delayed, Exceeded
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_variance_history_project ON benefit_variance_history(project_id);
CREATE INDEX IF NOT EXISTS idx_variance_history_date ON benefit_variance_history(snapshot_date);

-- ============================================================================
-- SUCCESS FACTORS LIBRARY
-- Stores lessons learned and success patterns
-- ============================================================================
CREATE TABLE IF NOT EXISTS success_factors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_id TEXT UNIQUE NOT NULL,  -- e.g., "PAT-AI-001"
    pattern_name TEXT NOT NULL,
    pattern_type TEXT,                 -- Success, Failure, Risk, Opportunity
    applicable_categories TEXT,        -- JSON array of project categories
    success_rate REAL,                 -- 0-100 percentage
    avg_benefit_realization REAL,     -- Average % of planned benefits
    sample_size INTEGER,               -- Number of projects in pattern
    key_factors TEXT,                  -- JSON array of success factors
    evidence_projects TEXT,            -- JSON array of project IDs
    created_date DATE NOT NULL,
    last_updated DATE NOT NULL,
    confidence_level TEXT,             -- High, Medium, Low
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_success_factors_type ON success_factors(pattern_type);
CREATE INDEX IF NOT EXISTS idx_success_factors_rate ON success_factors(success_rate);

-- ============================================================================
-- PROJECT LESSONS LEARNED
-- Individual lessons from post-implementation reviews
-- ============================================================================
CREATE TABLE IF NOT EXISTS project_lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    lesson_type TEXT NOT NULL,         -- WhatWorked, WhatDidnt, Recommendation, RiskLearned
    lesson_category TEXT,              -- Planning, Execution, ChangeManagement, Technical, etc.
    lesson_text TEXT NOT NULL,
    impact_level TEXT,                 -- High, Medium, Low
    benefit_impact_pct REAL,           -- % impact on benefit realization
    captured_date DATE NOT NULL,
    captured_by TEXT,
    tags TEXT,                         -- JSON array of tags
    related_pattern_id TEXT,           -- Link to success_factors table
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(related_pattern_id) REFERENCES success_factors(pattern_id)
);

CREATE INDEX IF NOT EXISTS idx_lessons_project ON project_lessons(project_id);
CREATE INDEX IF NOT EXISTS idx_lessons_type ON project_lessons(lesson_type);
CREATE INDEX IF NOT EXISTS idx_lessons_category ON project_lessons(lesson_category);

-- ============================================================================
-- BENEFIT ALERTS
-- Tracks alerts generated for benefit shortfalls
-- ============================================================================
CREATE TABLE IF NOT EXISTS benefit_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id TEXT UNIQUE NOT NULL,
    project_id TEXT NOT NULL,
    benefit_category TEXT,
    alert_type TEXT NOT NULL,          -- BenefitShortfall, BenefitLag, AnomalyDetected
    severity TEXT NOT NULL,            -- Critical, High, Medium, Low
    predicted_shortfall_pct REAL,      -- % below plan
    predicted_shortfall_amount REAL,   -- Dollar amount
    confidence REAL,                   -- 0-1 confidence in prediction
    alert_date DATE NOT NULL,
    expected_impact_date DATE,         -- When shortfall expected
    status TEXT DEFAULT 'OPEN',        -- OPEN, ACKNOWLEDGED, RESOLVED, FALSE_POSITIVE
    assigned_to TEXT,
    resolution_notes TEXT,
    resolved_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_alerts_project ON benefit_alerts(project_id);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON benefit_alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_date ON benefit_alerts(alert_date);

-- ============================================================================
-- PORTFOLIO BENEFIT SUMMARY
-- Pre-computed aggregations for dashboard performance
-- ============================================================================
CREATE TABLE IF NOT EXISTS portfolio_benefit_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_date DATE NOT NULL,
    total_planned_benefits REAL,
    total_realized_benefits REAL,
    overall_realization_rate REAL,
    category_breakdown TEXT,           -- JSON object with per-category metrics
    high_performers TEXT,              -- JSON array of top projects
    underperformers TEXT,              -- JSON array of struggling projects
    trend_direction TEXT,              -- Improving, Declining, Stable
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(snapshot_date)
);

CREATE INDEX IF NOT EXISTS idx_portfolio_summary_date ON portfolio_benefit_summary(snapshot_date);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Variance view with calculated metrics
CREATE VIEW IF NOT EXISTS v_benefit_variance AS
SELECT 
    bp.project_id,
    bp.benefit_category,
    bp.benefit_subcategory,
    bp.planned_amount,
    COALESCE(SUM(ba.actual_amount), 0) as actual_amount,
    COALESCE(SUM(ba.actual_amount), 0) - bp.planned_amount as variance_amount,
    CASE 
        WHEN bp.planned_amount > 0 THEN 
            ((COALESCE(SUM(ba.actual_amount), 0) - bp.planned_amount) / bp.planned_amount * 100)
        ELSE 0 
    END as variance_pct,
    CASE 
        WHEN bp.planned_amount > 0 THEN 
            (COALESCE(SUM(ba.actual_amount), 0) / bp.planned_amount * 100)
        ELSE 0 
    END as realization_rate,
    bp.baseline_date,
    bp.expected_full_date,
    MAX(ba.realization_date) as latest_actual_date
FROM benefit_plans bp
LEFT JOIN benefit_actuals ba ON bp.project_id = ba.project_id 
    AND bp.benefit_category = ba.benefit_category
    AND (bp.benefit_subcategory = ba.benefit_subcategory OR 
         (bp.benefit_subcategory IS NULL AND ba.benefit_subcategory IS NULL))
GROUP BY bp.project_id, bp.benefit_category, bp.benefit_subcategory;

-- Project summary view
CREATE VIEW IF NOT EXISTS v_project_benefit_summary AS
SELECT 
    project_id,
    COUNT(DISTINCT benefit_category) as benefit_categories_count,
    SUM(planned_amount) as total_planned,
    SUM(actual_amount) as total_realized,
    AVG(realization_rate) as avg_realization_rate,
    MIN(realization_rate) as min_realization_rate,
    MAX(realization_rate) as max_realization_rate
FROM v_benefit_variance
GROUP BY project_id;

-- Category performance view
CREATE VIEW IF NOT EXISTS v_category_performance AS
SELECT 
    benefit_category,
    COUNT(DISTINCT project_id) as project_count,
    SUM(planned_amount) as total_planned,
    SUM(actual_amount) as total_realized,
    AVG(realization_rate) as avg_realization_rate,
    SUM(variance_amount) as total_variance,
    COUNT(CASE WHEN realization_rate >= 90 THEN 1 END) as high_performers,
    COUNT(CASE WHEN realization_rate < 70 THEN 1 END) as underperformers
FROM v_benefit_variance
GROUP BY benefit_category;
