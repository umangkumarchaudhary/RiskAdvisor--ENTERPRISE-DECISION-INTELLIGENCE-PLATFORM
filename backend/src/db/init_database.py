"""
RiskAdvisor - Database Initialization Script
=============================================
Run this to create tables and seed initial data.

Usage:
    python -m src.db.init_database
"""

import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv()

from src.db.database import engine, Base, SessionLocal
from src.db.models import StrategyModel, ConstraintModel, StakeholderModel
from src.services.strategy_service import StrategyService


def init_database():
    """Initialize the database with tables and seed data."""
    print("=" * 60)
    print("[DB] RiskAdvisor Database Initialization")
    print("=" * 60)
    
    # 1. Create all tables
    print("\n[1] Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("    [OK] Tables created successfully")
    except Exception as e:
        print(f"    [ERROR] Error creating tables: {e}")
        return False
    
    # 2. Seed strategies
    print("\n[2] Seeding strategy library...")
    try:
        db = SessionLocal()
        service = StrategyService(db)
        service.seed_default_strategies()
        
        # Count strategies
        count = db.query(StrategyModel).count()
        print(f"    [OK] {count} strategies in database")
        db.close()
    except Exception as e:
        print(f"    [ERROR] Error seeding strategies: {e}")
        return False
    
    # 3. Seed stakeholders
    print("\n[3] Seeding stakeholder profiles...")
    try:
        db = SessionLocal()
        
        stakeholders = [
            {
                "id": "SH_CEO",
                "role": "CEO",
                "primary_concerns": ["Financial impact", "Reputation", "Regulatory compliance"],
                "decision_criteria": ["ROI", "Optics", "Risk exposure"],
                "preferred_format": "executive_summary",
                "framing": "Cost avoidance, risk transfer, reputation protection",
            },
            {
                "id": "SH_CFO",
                "role": "CFO",
                "primary_concerns": ["Budget impact", "Cash flow", "Audit trail"],
                "decision_criteria": ["NPV", "Payback period", "Budget fit"],
                "preferred_format": "detailed_financials",
                "framing": "Capital efficiency, risk-adjusted returns",
            },
            {
                "id": "SH_COO",
                "role": "COO",
                "primary_concerns": ["Operational disruption", "Schedule impact"],
                "decision_criteria": ["Minimal downtime", "Phased approach"],
                "preferred_format": "operational_plan",
                "framing": "Minimal disruption, flexible scheduling",
            },
            {
                "id": "SH_SAFETY",
                "role": "VP_SAFETY",
                "primary_concerns": ["Risk reduction", "Compliance", "Safety culture"],
                "decision_criteria": ["Risk metrics", "SMS alignment"],
                "preferred_format": "detailed",
                "framing": "Safety first, measurable improvement",
            },
        ]
        
        for sh_data in stakeholders:
            existing = db.query(StakeholderModel).filter(
                StakeholderModel.id == sh_data["id"]
            ).first()
            
            if not existing:
                sh = StakeholderModel(**sh_data)
                db.add(sh)
        
        db.commit()
        count = db.query(StakeholderModel).count()
        print(f"    [OK] {count} stakeholder profiles in database")
        db.close()
    except Exception as e:
        print(f"    [ERROR] Error seeding stakeholders: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("[DONE] Database initialization complete!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
