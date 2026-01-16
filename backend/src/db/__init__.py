"""RiskAdvisor Database Module"""
from src.db.database import Base, engine, SessionLocal, get_db
from src.db.models import (
    StrategyModel,
    ConstraintModel,
    RecommendationModel,
    ImplementationModel,
    StakeholderModel
)

# Create all tables
def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
