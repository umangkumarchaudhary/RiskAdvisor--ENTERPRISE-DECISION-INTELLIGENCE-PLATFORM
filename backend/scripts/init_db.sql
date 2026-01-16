"""
RiskAdvisor - Database Schema
=============================
PostgreSQL schema for decision intelligence platform.
Integrates with AeroRisk data.

Author: Umang Kumar
Date: January 2026
"""

-- ============================================
-- RISKADVISOR SCHEMA
-- ============================================

CREATE SCHEMA IF NOT EXISTS riskadvisor;

-- ============================================
-- STRATEGY LIBRARY
-- Mitigation strategies with costs/effectiveness
-- ============================================

CREATE TABLE riskadvisor.strategies (
    id SERIAL PRIMARY KEY,
    strategy_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,  -- maintenance, training, process, technology, policy
    
    -- Effectiveness
    risk_reduction_percent DECIMAL(5,2),
    confidence_level DECIMAL(3,2),
    
    -- Cost
    cost_min DECIMAL(12,2),
    cost_max DECIMAL(12,2),
    cost_estimate DECIMAL(12,2),
    cost_type VARCHAR(20) DEFAULT 'one-time',  -- one-time, recurring, per-unit
    
    -- Timeline
    implementation_days_min INT,
    implementation_days_max INT,
    implementation_days_estimate INT,
    
    -- Constraints
    requires_budget BOOLEAN DEFAULT TRUE,
    requires_approval_level VARCHAR(20),  -- team, manager, director, vp, ceo
    requires_regulatory_approval BOOLEAN DEFAULT FALSE,
    disruption_level VARCHAR(20),  -- none, low, medium, high
    
    -- Targeting
    applicable_risk_types TEXT[],  -- weather, maintenance, fatigue, etc
    applicable_severity_min INT,
    
    -- Metadata
    sms_pillar VARCHAR(50),
    regulatory_refs TEXT[],
    action_steps JSONB,
    kpis TEXT[],
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- CONSTRAINT DEFINITIONS
-- Budget, timeline, resource constraints
-- ============================================

CREATE TABLE riskadvisor.constraints (
    id SERIAL PRIMARY KEY,
    constraint_type VARCHAR(20) NOT NULL,  -- hard, soft, learned
    category VARCHAR(50) NOT NULL,  -- budget, timeline, resource, regulatory
    name VARCHAR(200) NOT NULL,
    
    -- Hard constraints
    min_value DECIMAL(15,2),
    max_value DECIMAL(15,2),
    
    -- Soft constraints
    target_value DECIMAL(15,2),
    penalty_per_unit DECIMAL(10,2),  -- cost of violating by 1 unit
    
    -- Context
    effective_from DATE,
    effective_to DATE,
    context_conditions JSONB,
    
    -- Learned (historical patterns)
    learned_adjustment DECIMAL(5,2),  -- e.g., +20% for Q4
    confidence DECIMAL(3,2),
    sample_size INT,
    
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- DECISION RECOMMENDATIONS
-- Generated decision packages
-- ============================================

CREATE TABLE riskadvisor.recommendations (
    id SERIAL PRIMARY KEY,
    recommendation_code VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Context
    risk_score DECIMAL(5,2),
    context_snapshot JSONB,
    
    -- Multi-horizon plans
    immediate_plan JSONB,  -- 0-30 days
    tactical_plan JSONB,   -- 30-180 days
    strategic_plan JSONB,  -- 180+ days
    
    -- Aggregates
    total_cost_estimate DECIMAL(15,2),
    total_risk_reduction DECIMAL(5,2),
    total_timeline_days INT,
    
    -- Alternatives (from negotiation engine)
    alternative_plans JSONB,
    
    -- Adversarial validation
    robustness_score DECIMAL(3,2),
    stress_test_results JSONB,
    backup_plan JSONB,
    
    -- Stakeholder versions
    stakeholder_briefs JSONB,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending',  -- pending, approved, rejected, implemented
    approved_by VARCHAR(100),
    approved_at TIMESTAMP
);

-- ============================================
-- IMPLEMENTATION TRACKING
-- Track actual vs predicted outcomes
-- ============================================

CREATE TABLE riskadvisor.implementations (
    id SERIAL PRIMARY KEY,
    recommendation_id INT REFERENCES riskadvisor.recommendations(id),
    strategy_id INT REFERENCES riskadvisor.strategies(id),
    
    -- Predicted
    predicted_cost DECIMAL(12,2),
    predicted_days INT,
    predicted_risk_reduction DECIMAL(5,2),
    
    -- Actual
    actual_cost DECIMAL(12,2),
    actual_days INT,
    actual_risk_reduction DECIMAL(5,2),
    
    -- Variance
    cost_variance_pct DECIMAL(5,2),
    time_variance_pct DECIMAL(5,2),
    effectiveness_variance_pct DECIMAL(5,2),
    
    -- Learnings
    challenges_encountered TEXT[],
    lessons_learned TEXT,
    
    -- Dates
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'planned'  -- planned, in_progress, completed, cancelled
);

-- ============================================
-- CONTEXT SNAPSHOTS
-- Organizational state tracking
-- ============================================

CREATE TABLE riskadvisor.context_snapshots (
    id SERIAL PRIMARY KEY,
    snapshot_date DATE NOT NULL,
    
    -- Organizational state
    org_state VARCHAR(50),  -- normal, post_incident, crisis, audit_prep
    leadership_focus TEXT[],
    active_initiatives TEXT[],
    
    -- Resources
    available_budget DECIMAL(15,2),
    available_fte DECIMAL(6,2),
    change_capacity_score DECIMAL(3,2),  -- 0-1, how much more change can org absorb
    
    -- External factors
    regulatory_pressure_level VARCHAR(20),  -- low, medium, high
    media_attention BOOLEAN DEFAULT FALSE,
    peak_season BOOLEAN DEFAULT FALSE,
    
    -- Constraints snapshot
    constraint_overrides JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- STAKEHOLDER PROFILES
-- Communication preferences
-- ============================================

CREATE TABLE riskadvisor.stakeholders (
    id SERIAL PRIMARY KEY,
    role VARCHAR(50) NOT NULL,
    name VARCHAR(100),
    
    -- Decision criteria
    primary_concerns TEXT[],
    decision_criteria TEXT[],
    
    -- Communication
    preferred_format VARCHAR(50),  -- executive_summary, detailed, visual
    communication_style VARCHAR(50),
    
    -- Framing
    recommendation_framing TEXT,
    metrics_preferred TEXT[],
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX idx_strategies_category ON riskadvisor.strategies(category);
CREATE INDEX idx_strategies_risk_types ON riskadvisor.strategies USING GIN(applicable_risk_types);
CREATE INDEX idx_recommendations_status ON riskadvisor.recommendations(status);
CREATE INDEX idx_implementations_status ON riskadvisor.implementations(status);

-- ============================================
-- SEED DATA - Stakeholder Profiles
-- ============================================

INSERT INTO riskadvisor.stakeholders (role, primary_concerns, decision_criteria, preferred_format, recommendation_framing) VALUES
('CEO', ARRAY['Financial impact', 'Reputation', 'Regulatory compliance'], ARRAY['ROI', 'Optics', 'Risk exposure'], 'executive_summary', 'Cost avoidance, risk transfer, reputation protection'),
('CFO', ARRAY['Budget impact', 'Cash flow', 'Audit trail'], ARRAY['NPV', 'Payback period', 'Budget fit'], 'detailed', 'Capital efficiency, risk-adjusted returns'),
('COO', ARRAY['Operational disruption', 'Schedule impact', 'Resource utilization'], ARRAY['Minimal downtime', 'Phased approach'], 'visual', 'Minimal disruption, flexible scheduling'),
('VP Safety', ARRAY['Risk reduction', 'Compliance', 'Safety culture'], ARRAY['Risk metrics', 'SMS alignment'], 'detailed', 'Safety first, measurable improvement'),
('Union Rep', ARRAY['Job security', 'Workload', 'Worker safety'], ARRAY['No layoffs', 'Fair workload'], 'visual', 'Worker safety first, collaborative approach');
