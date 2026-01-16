"""
RiskAdvisor - Strategy Service
===============================
CRUD operations for strategies.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

from src.db.models import StrategyModel
from src.core.optimizer import Strategy, StrategyCategory


def category_str_to_enum(category: str) -> StrategyCategory:
    """Convert string category to enum."""
    mapping = {
        "maintenance": StrategyCategory.MAINTENANCE,
        "training": StrategyCategory.TRAINING,
        "process": StrategyCategory.PROCESS,
        "technology": StrategyCategory.TECHNOLOGY,
        "policy": StrategyCategory.POLICY,
    }
    return mapping.get(category.lower(), StrategyCategory.PROCESS)


def db_to_strategy(db_strategy: StrategyModel) -> Strategy:
    """Convert SQLAlchemy model to Strategy dataclass."""
    return Strategy(
        id=db_strategy.id,
        name=db_strategy.name,
        category=category_str_to_enum(db_strategy.category),
        risk_reduction_pct=db_strategy.risk_reduction_pct,
        cost_estimate=db_strategy.cost_estimate,
        cost_min=db_strategy.cost_min or db_strategy.cost_estimate * 0.8,
        cost_max=db_strategy.cost_max or db_strategy.cost_estimate * 1.2,
        time_estimate=db_strategy.time_estimate,
        time_min=db_strategy.time_min or max(1, db_strategy.time_estimate - 14),
        time_max=db_strategy.time_max or db_strategy.time_estimate + 30,
    )


class StrategyService:
    """Service for managing strategies."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, active_only: bool = True) -> List[Strategy]:
        """Get all strategies."""
        query = self.db.query(StrategyModel)
        if active_only:
            query = query.filter(StrategyModel.is_active == True)
        
        db_strategies = query.all()
        return [db_to_strategy(s) for s in db_strategies]
    
    def get_by_id(self, strategy_id: str) -> Optional[Strategy]:
        """Get strategy by ID."""
        db_strategy = self.db.query(StrategyModel).filter(
            StrategyModel.id == strategy_id
        ).first()
        
        if db_strategy:
            return db_to_strategy(db_strategy)
        return None
    
    def get_by_category(self, category: str) -> List[Strategy]:
        """Get strategies by category."""
        db_strategies = self.db.query(StrategyModel).filter(
            StrategyModel.category == category,
            StrategyModel.is_active == True
        ).all()
        
        return [db_to_strategy(s) for s in db_strategies]
    
    def create(
        self,
        name: str,
        category: str,
        risk_reduction_pct: float,
        cost_estimate: float,
        time_estimate: int,
        description: str = "",
        **kwargs
    ) -> Strategy:
        """Create a new strategy."""
        strategy_id = f"{category.upper()[:4]}_{uuid.uuid4().hex[:6].upper()}"
        
        db_strategy = StrategyModel(
            id=strategy_id,
            name=name,
            category=category,
            description=description,
            risk_reduction_pct=risk_reduction_pct,
            cost_estimate=cost_estimate,
            cost_min=kwargs.get("cost_min", cost_estimate * 0.8),
            cost_max=kwargs.get("cost_max", cost_estimate * 1.2),
            time_estimate=time_estimate,
            time_min=kwargs.get("time_min", max(1, time_estimate - 14)),
            time_max=kwargs.get("time_max", time_estimate + 30),
            required_skills=kwargs.get("required_skills", []),
            required_resources=kwargs.get("required_resources", []),
            dependencies=kwargs.get("dependencies", []),
            source=kwargs.get("source", "manual"),
        )
        
        self.db.add(db_strategy)
        self.db.commit()
        self.db.refresh(db_strategy)
        
        return db_to_strategy(db_strategy)
    
    def update(self, strategy_id: str, **updates) -> Optional[Strategy]:
        """Update a strategy."""
        db_strategy = self.db.query(StrategyModel).filter(
            StrategyModel.id == strategy_id
        ).first()
        
        if not db_strategy:
            return None
        
        for key, value in updates.items():
            if hasattr(db_strategy, key):
                setattr(db_strategy, key, value)
        
        db_strategy.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_strategy)
        
        return db_to_strategy(db_strategy)
    
    def delete(self, strategy_id: str) -> bool:
        """Soft delete a strategy (mark as inactive)."""
        db_strategy = self.db.query(StrategyModel).filter(
            StrategyModel.id == strategy_id
        ).first()
        
        if not db_strategy:
            return False
        
        db_strategy.is_active = False
        db_strategy.updated_at = datetime.utcnow()
        self.db.commit()
        
        return True
    
    def seed_default_strategies(self):
        """Seed the database with default strategies."""
        default_strategies = [
            {
                "name": "Emergency Inspection Protocol",
                "category": "process",
                "description": "Enhanced inspection procedures for critical components",
                "risk_reduction_pct": 8.0,
                "cost_estimate": 15000,
                "time_estimate": 7,
            },
            {
                "name": "Weather Minimums Update",
                "category": "policy",
                "description": "Revised weather decision-making criteria",
                "risk_reduction_pct": 5.0,
                "cost_estimate": 5000,
                "time_estimate": 3,
            },
            {
                "name": "Crew Fatigue Training",
                "category": "training",
                "description": "Comprehensive fatigue awareness and management program",
                "risk_reduction_pct": 12.0,
                "cost_estimate": 45000,
                "time_estimate": 45,
            },
            {
                "name": "Enhanced Maintenance Protocol",
                "category": "maintenance",
                "description": "Increased inspection frequency and enhanced procedures",
                "risk_reduction_pct": 18.0,
                "cost_estimate": 120000,
                "time_estimate": 60,
            },
            {
                "name": "Predictive Maintenance AI",
                "category": "technology",
                "description": "AI-powered predictive maintenance system",
                "risk_reduction_pct": 25.0,
                "cost_estimate": 350000,
                "time_estimate": 180,
            },
            {
                "name": "Safety Culture Assessment",
                "category": "process",
                "description": "Organization-wide safety culture evaluation and action plan",
                "risk_reduction_pct": 10.0,
                "cost_estimate": 35000,
                "time_estimate": 30,
            },
            {
                "name": "Threat and Error Management",
                "category": "training",
                "description": "TEM training for all flight crews",
                "risk_reduction_pct": 15.0,
                "cost_estimate": 60000,
                "time_estimate": 60,
            },
            {
                "name": "Digital Safety Reporting",
                "category": "technology",
                "description": "Modern digital safety reporting and analytics platform",
                "risk_reduction_pct": 8.0,
                "cost_estimate": 85000,
                "time_estimate": 90,
            },
        ]
        
        for strat_data in default_strategies:
            # Check if exists
            existing = self.db.query(StrategyModel).filter(
                StrategyModel.name == strat_data["name"]
            ).first()
            
            if not existing:
                self.create(**strat_data)
        
        self.db.commit()
