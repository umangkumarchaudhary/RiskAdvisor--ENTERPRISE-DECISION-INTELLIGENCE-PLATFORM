"""
RiskAdvisor - SQLAlchemy Models
================================
Database models for strategies, constraints, recommendations, etc.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from src.db.database import Base


class StrategyModel(Base):
    """Database model for mitigation strategies."""
    __tablename__ = "strategies"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False)  # maintenance, training, process, technology, policy
    
    # Effectiveness
    risk_reduction_pct = Column(Float, nullable=False)  # Expected risk reduction
    effectiveness_confidence = Column(Float, default=0.8)  # How confident in this estimate
    
    # Cost
    cost_estimate = Column(Float, nullable=False)
    cost_min = Column(Float)
    cost_max = Column(Float)
    
    # Timeline
    time_estimate = Column(Integer, nullable=False)  # Days
    time_min = Column(Integer)
    time_max = Column(Integer)
    
    # Constraints
    required_skills = Column(JSON, default=list)  # Skills needed
    required_resources = Column(JSON, default=list)  # Equipment, space, etc.
    dependencies = Column(JSON, default=list)  # Other strategy IDs this depends on
    
    # Metadata
    source = Column(String(100))  # Where this strategy came from
    last_used = Column(DateTime)
    success_rate = Column(Float)  # Historical success rate
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConstraintModel(Base):
    """Database model for constraints."""
    __tablename__ = "constraints"
    
    id = Column(String(50), primary_key=True)
    type = Column(String(20), nullable=False)  # hard, soft, learned
    category = Column(String(50), nullable=False)  # budget, timeline, resource, regulatory
    description = Column(Text, nullable=False)
    
    # Constraint value
    metric = Column(String(50))  # What we're constraining
    limit_value = Column(Float)  # The limit
    current_value = Column(Float)  # Current state
    
    # Flexibility
    negotiable = Column(Boolean, default=False)
    flexibility_pct = Column(Float, default=0)  # How much can we flex
    
    # Learning
    times_challenged = Column(Integer, default=0)
    times_relaxed = Column(Integer, default=0)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class RecommendationModel(Base):
    """Database model for generated recommendations."""
    __tablename__ = "recommendations"
    
    id = Column(String(50), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    risk_score = Column(Float, nullable=False)
    
    # The recommendation
    selected_strategies = Column(JSON)  # List of strategy IDs
    total_cost = Column(Float)
    total_risk_reduction = Column(Float)
    total_timeline = Column(Integer)
    
    # Multi-horizon breakdown
    immediate_strategies = Column(JSON)
    tactical_strategies = Column(JSON)
    strategic_strategies = Column(JSON)
    
    # Analysis results
    robustness_score = Column(Float)
    resilience_rating = Column(String(1))  # A, B, C, D, F
    cascading_costs = Column(Float)
    
    # Stakeholder briefs
    ceo_brief = Column(JSON)
    cfo_brief = Column(JSON)
    coo_brief = Column(JSON)
    
    # Context
    org_state = Column(String(50))
    context_snapshot = Column(JSON)
    
    # Status
    status = Column(String(20), default="generated")  # generated, approved, implemented, completed


class ImplementationModel(Base):
    """Database model for tracking implementations."""
    __tablename__ = "implementations"
    
    id = Column(String(50), primary_key=True)
    recommendation_id = Column(String(50), ForeignKey("recommendations.id"))
    strategy_id = Column(String(50), ForeignKey("strategies.id"))
    
    # Predicted
    predicted_cost = Column(Float)
    predicted_risk_reduction = Column(Float)
    predicted_timeline = Column(Integer)
    
    # Actual
    actual_cost = Column(Float)
    actual_risk_reduction = Column(Float)
    actual_timeline = Column(Integer)
    
    # Tracking
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String(20), default="pending")  # pending, in_progress, completed, failed
    
    # Learning
    success = Column(Boolean)
    lessons_learned = Column(Text)
    variance_explained = Column(Text)  # Why actual differed from predicted


class StakeholderModel(Base):
    """Database model for stakeholder profiles."""
    __tablename__ = "stakeholders"
    
    id = Column(String(50), primary_key=True)
    role = Column(String(50), nullable=False)
    name = Column(String(100))
    
    # Preferences
    primary_concerns = Column(JSON)  # What they care about
    decision_criteria = Column(JSON)  # How they decide
    preferred_format = Column(String(50))  # How to communicate
    
    # Communication style
    framing = Column(Text)  # How to frame recommendations
    key_metrics = Column(JSON)  # Which metrics to highlight
    
    is_active = Column(Boolean, default=True)
