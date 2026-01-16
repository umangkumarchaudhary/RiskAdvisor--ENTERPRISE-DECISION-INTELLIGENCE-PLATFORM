"""
RiskAdvisor - FastAPI Backend
==============================
Enterprise Decision Intelligence API.

Author: Umang Kumar
Date: January 2026
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import all layers
from src.core.optimizer import Strategy, StrategyCategory, CoreOptimizer
from src.negotiation.constraint_engine import ConstraintNegotiationEngine, NegotiableConstraint
from src.impact.cascading_analyzer import CascadingImpactAnalyzer
from src.adversarial.war_gaming import PurpleTeam
from src.horizons.multi_horizon import MultiHorizonOptimizer
from src.context.intelligence_engine import ContextIntelligenceEngine
from src.interface.executive_interface import ExecutiveDecisionInterface

# Import database
from src.db.database import get_db, engine, Base
from src.db.models import StrategyModel
from src.services.strategy_service import StrategyService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================
# Lifespan - Initialize DB on startup
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables on startup."""
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database ready!")
    yield
    logger.info("Shutting down...")


# ============================================
# FastAPI App
# ============================================

app = FastAPI(
    title="RiskAdvisor v4.0",
    description="Enterprise Decision Intelligence Platform for Aviation Safety",
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Pydantic Models
# ============================================

class StrategyInput(BaseModel):
    id: str
    name: str
    category: str  # maintenance, training, process, technology, policy
    risk_reduction_pct: float = Field(ge=0, le=100)
    cost_estimate: float = Field(ge=0)
    cost_min: float = Field(ge=0, default=0)
    cost_max: float = Field(ge=0, default=0)
    time_estimate: int = Field(ge=0, default=30)
    time_min: int = Field(ge=0, default=0)
    time_max: int = Field(ge=0, default=0)


class OptimizationRequest(BaseModel):
    strategies: List[StrategyInput]
    budget_limit: float = Field(ge=0)
    timeline_limit: int = Field(ge=0, default=365)
    risk_tolerance: str = "balanced"  # aggressive, balanced, conservative


class ContextInput(BaseModel):
    recent_incident_days: int = 365
    budget_frozen: bool = False
    peak_season: bool = False
    audit_days: int = 365
    available_budget: float = 0
    active_initiatives: int = 0
    leadership_support_score: float = 50


class DecisionPackageRequest(BaseModel):
    strategies: List[StrategyInput]
    budget: float
    risk_score: float = Field(ge=0, le=100)
    context: Optional[ContextInput] = None


# ============================================
# Helper Functions
# ============================================

def convert_to_strategy(s: StrategyInput) -> Strategy:
    """Convert Pydantic model to Strategy dataclass."""
    category_map = {
        "maintenance": StrategyCategory.MAINTENANCE,
        "training": StrategyCategory.TRAINING,
        "process": StrategyCategory.PROCESS,
        "technology": StrategyCategory.TECHNOLOGY,
        "policy": StrategyCategory.POLICY,
    }
    return Strategy(
        id=s.id,
        name=s.name,
        category=category_map.get(s.category, StrategyCategory.PROCESS),
        risk_reduction_pct=s.risk_reduction_pct,
        cost_estimate=s.cost_estimate,
        cost_min=s.cost_min or s.cost_estimate * 0.8,
        cost_max=s.cost_max or s.cost_estimate * 1.2,
        time_estimate=s.time_estimate,
        time_min=s.time_min or max(1, s.time_estimate - 14),
        time_max=s.time_max or s.time_estimate + 30,
    )


# ============================================
# API Endpoints
# ============================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint."""
    return {
        "name": "RiskAdvisor v4.0",
        "description": "Enterprise Decision Intelligence Platform",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "layers": [
            "Layer 1: Core Optimizer ✓",
            "Layer 2: Constraint Negotiation ✓",
            "Layer 3: Cascading Impact ✓",
            "Layer 4: Adversarial Validation ✓",
            "Layer 5: Multi-Horizon ✓",
            "Layer 6: Context Intelligence ✓",
            "Layer 7: Executive Interface ✓"
        ]
    }


# ============================================
# Layer 1: Core Optimization
# ============================================

@app.post("/api/v1/optimize", tags=["Layer 1: Optimization"])
async def optimize_portfolio(request: OptimizationRequest):
    """
    Optimize safety strategy portfolio.
    
    Returns optimal portfolio with Monte Carlo uncertainty analysis.
    """
    try:
        strategies = [convert_to_strategy(s) for s in request.strategies]
        
        optimizer = CoreOptimizer(strategies, [])
        result = optimizer.get_optimal_portfolio(
            budget_limit=request.budget_limit,
            timeline_limit=request.timeline_limit,
            risk_tolerance=request.risk_tolerance
        )
        
        return {
            "success": True,
            "selected_strategies": [
                {
                    "id": s.id,
                    "name": s.name,
                    "category": s.category.value,
                    "risk_reduction_pct": s.risk_reduction_pct,
                    "cost_estimate": s.cost_estimate
                }
                for s in result.selected_strategies
            ],
            "total_cost": result.total_cost,
            "total_risk_reduction": result.total_risk_reduction,
            "total_timeline_days": result.total_timeline_days,
            "cost_range": {
                "p5": result.cost_p5,
                "p95": result.cost_p95
            },
            "risk_range": {
                "p5": result.risk_reduction_p5,
                "p95": result.risk_reduction_p95
            }
        }
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/optimize/pareto", tags=["Layer 1: Optimization"])
async def pareto_frontier(request: OptimizationRequest):
    """
    Generate Pareto frontier of optimal solutions.
    """
    try:
        strategies = [convert_to_strategy(s) for s in request.strategies]
        
        optimizer = CoreOptimizer(strategies, [])
        pareto = optimizer.optimize_pareto(
            budget_limit=request.budget_limit,
            timeline_limit=request.timeline_limit,
            n_solutions=10
        )
        
        return {
            "success": True,
            "pareto_solutions": [
                {
                    "rank": i + 1,
                    "cost": sol.total_cost,
                    "risk_reduction": sol.total_risk_reduction,
                    "timeline": sol.total_timeline_days,
                    "strategy_count": len(sol.selected_strategies)
                }
                for i, sol in enumerate(pareto)
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Layer 3: Cascading Impact
# ============================================

@app.post("/api/v1/impact/analyze", tags=["Layer 3: Impact"])
async def analyze_impact(strategy: StrategyInput):
    """
    Analyze cascading impacts of a strategy.
    
    Returns first, second, and third-order effects.
    """
    try:
        s = convert_to_strategy(strategy)
        analyzer = CascadingImpactAnalyzer()
        analysis = analyzer.analyze_strategy(s)
        
        return {
            "success": True,
            "strategy": strategy.name,
            "direct_cost": analysis.direct_cost,
            "second_order_cost": analysis.second_order_cost,
            "third_order_cost": analysis.third_order_cost,
            "total_cost_of_ownership": analysis.total_cost_of_ownership,
            "cost_multiplier": analysis.cost_multiplier,
            "still_recommended": analysis.still_recommended,
            "justification": analysis.justification,
            "effects": [
                {
                    "description": e.description,
                    "order": e.order.value,
                    "category": e.category.value,
                    "value": e.value
                }
                for e in analysis.effects
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Layer 4: War Gaming
# ============================================

@app.post("/api/v1/wargame", tags=["Layer 4: War Gaming"])
async def war_gaming(request: OptimizationRequest):
    """
    Stress test recommendations via adversarial validation.
    
    Returns robustness score and backup plans.
    """
    try:
        strategies = [convert_to_strategy(s) for s in request.strategies]
        
        # Get optimal first
        optimizer = CoreOptimizer(strategies, [])
        optimal = optimizer.get_optimal_portfolio(
            budget_limit=request.budget_limit,
            risk_tolerance=request.risk_tolerance
        )
        
        # War game it
        purple_team = PurpleTeam(strategies)
        assessment = purple_team.assess_robustness(optimal, request.budget_limit)
        
        return {
            "success": True,
            "robustness_score": assessment.robustness_score,
            "resilience_rating": assessment.resilience_rating,
            "attack_results": [
                {
                    "attack": r.attack.description,
                    "severity": r.attack.severity,
                    "degradation_pct": r.outcome_degradation_pct,
                    "still_viable": r.still_viable,
                    "recovery_options": r.recovery_options
                }
                for r in assessment.attack_results
            ],
            "worst_case": assessment.worst_case_description,
            "recommendations": assessment.recommendations,
            "backup_plan": {
                "cost": assessment.backup_plan.total_cost if assessment.backup_plan else 0,
                "risk_reduction": assessment.backup_plan.total_risk_reduction if assessment.backup_plan else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Layer 5: Multi-Horizon
# ============================================

@app.post("/api/v1/horizon/plan", tags=["Layer 5: Multi-Horizon"])
async def multi_horizon_plan(request: DecisionPackageRequest):
    """
    Generate multi-horizon decision plan.
    
    Returns Immediate, Tactical, and Strategic plans.
    """
    try:
        strategies = [convert_to_strategy(s) for s in request.strategies]
        
        optimizer = MultiHorizonOptimizer(
            strategies=strategies,
            total_budget=request.budget,
            risk_score=request.risk_score
        )
        
        plan = optimizer.optimize_all_horizons()
        
        return {
            "success": True,
            "total_cost": plan.total_cost,
            "total_risk_reduction": plan.total_risk_reduction,
            "immediate": {
                "label": "0-30 days",
                "strategies": [s.name for s in plan.immediate_plan.strategies],
                "cost": plan.immediate_plan.total_cost,
                "risk_reduction": plan.immediate_plan.risk_reduction,
                "action_items": plan.immediate_plan.action_items,
                "decision_deadline": plan.immediate_plan.decision_deadline
            },
            "tactical": {
                "label": "30-180 days",
                "strategies": [s.name for s in plan.tactical_plan.strategies],
                "cost": plan.tactical_plan.total_cost,
                "risk_reduction": plan.tactical_plan.risk_reduction,
                "action_items": plan.tactical_plan.action_items
            },
            "strategic": {
                "label": "180+ days",
                "strategies": [s.name for s in plan.strategic_plan.strategies],
                "cost": plan.strategic_plan.total_cost,
                "risk_reduction": plan.strategic_plan.risk_reduction,
                "action_items": plan.strategic_plan.action_items
            },
            "phase_sequence": plan.phase_sequence,
            "tradeoff": plan.immediate_vs_sustainable_tradeoff
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Layer 6: Context Intelligence
# ============================================

@app.post("/api/v1/context/detect", tags=["Layer 6: Context"])
async def detect_context(context: ContextInput):
    """
    Detect organizational context and recommended approach.
    """
    try:
        engine = ContextIntelligenceEngine()
        org_context = engine.detect_context({
            "recent_incident_days": context.recent_incident_days,
            "budget_frozen": context.budget_frozen,
            "peak_season": context.peak_season,
            "audit_days": context.audit_days,
            "available_budget": context.available_budget,
            "active_initiatives": context.active_initiatives,
            "leadership_support_score": context.leadership_support_score
        })
        
        adaptation = engine.adaptation_rules.get(org_context.org_state)
        
        return {
            "success": True,
            "detected_state": org_context.org_state.value,
            "change_capacity_pct": org_context.change_capacity_pct,
            "leadership_support": org_context.leadership_support.value,
            "adaptation": {
                "approach_name": adaptation.approach_name,
                "approach_description": adaptation.approach_description,
                "budget_multiplier": adaptation.budget_multiplier,
                "timeline_multiplier": adaptation.timeline_multiplier,
                "scope_adjustment": adaptation.scope_adjustment,
                "framing": adaptation.framing,
                "key_messages": adaptation.key_messages
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Layer 7: Executive Interface
# ============================================

@app.post("/api/v1/decision/package", tags=["Layer 7: Executive"])
async def generate_decision_package(request: DecisionPackageRequest):
    """
    Generate complete executive decision package.
    
    Combines all 7 layers into executive-ready outputs.
    """
    try:
        strategies = [convert_to_strategy(s) for s in request.strategies]
        
        interface = ExecutiveDecisionInterface(
            strategies=strategies,
            budget=request.budget,
            risk_score=request.risk_score
        )
        
        context_dict = {}
        if request.context:
            context_dict = {
                "recent_incident_days": request.context.recent_incident_days,
                "budget_frozen": request.context.budget_frozen,
                "peak_season": request.context.peak_season,
                "available_budget": request.context.available_budget,
                "active_initiatives": request.context.active_initiatives,
                "leadership_support_score": request.context.leadership_support_score
            }
        
        package = interface.generate_decision_package(context_dict)
        
        return {
            "success": True,
            "title": package.title,
            "situation_summary": package.situation_summary,
            "risk_score": package.risk_score,
            "decision_deadline": package.decision_deadline,
            "scenarios": [
                {
                    "id": s.scenario_id,
                    "name": s.name,
                    "description": s.description,
                    "cost": s.cost,
                    "risk_reduction": s.risk_reduction,
                    "timeline_days": s.timeline_days,
                    "disruption_level": s.disruption_level,
                    "confidence": s.confidence,
                    "recommended": s.recommended,
                    "rationale": s.rationale
                }
                for s in package.scenarios
            ],
            "stakeholder_briefs": {
                role: {
                    "subject_line": brief.subject_line,
                    "key_points": brief.key_points,
                    "recommended_action": brief.recommended_action,
                    "metrics": brief.metrics_highlighted
                }
                for role, brief in package.stakeholder_briefs.items()
            },
            "robustness": {
                "score": package.robustness.robustness_score if package.robustness else 0,
                "rating": package.robustness.resilience_rating if package.robustness else "N/A"
            }
        }
    except Exception as e:
        logger.error(f"Decision package generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Strategy Endpoints (Database)
# ============================================

@app.get("/api/v1/strategies", tags=["Strategies"])
async def list_strategies(db: Session = Depends(get_db)):
    """Get all strategies from database."""
    try:
        service = StrategyService(db)
        strategies = service.get_all()
        
        return {
            "success": True,
            "count": len(strategies),
            "strategies": [
                {
                    "id": s.id,
                    "name": s.name,
                    "category": s.category.value,
                    "risk_reduction_pct": s.risk_reduction_pct,
                    "cost_estimate": s.cost_estimate,
                    "time_estimate": s.time_estimate
                }
                for s in strategies
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching strategies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/strategies/sample", tags=["Strategies"])
async def get_sample_strategies(db: Session = Depends(get_db)):
    """Get strategies from database (alias for /strategies)."""
    try:
        service = StrategyService(db)
        strategies = service.get_all()
        
        return {
            "strategies": [
                {
                    "id": s.id,
                    "name": s.name,
                    "category": s.category.value,
                    "risk_reduction_pct": s.risk_reduction_pct,
                    "cost_estimate": s.cost_estimate,
                    "time_estimate": s.time_estimate
                }
                for s in strategies
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching strategies: {e}")
        # Fallback to hardcoded if DB fails
        return {
            "strategies": [
                {"id": "PROC_001", "name": "Emergency Protocol Update", "category": "process", "risk_reduction_pct": 8.0, "cost_estimate": 15000, "time_estimate": 7},
                {"id": "TRAIN_001", "name": "Crew Fatigue Training", "category": "training", "risk_reduction_pct": 12.0, "cost_estimate": 45000, "time_estimate": 45},
                {"id": "MAINT_001", "name": "Enhanced Maintenance", "category": "maintenance", "risk_reduction_pct": 18.0, "cost_estimate": 120000, "time_estimate": 60},
                {"id": "TECH_001", "name": "Predictive Maintenance AI", "category": "technology", "risk_reduction_pct": 25.0, "cost_estimate": 350000, "time_estimate": 180},
            ]
        }


@app.post("/api/v1/strategies", tags=["Strategies"])
async def create_strategy(
    name: str,
    category: str,
    risk_reduction_pct: float,
    cost_estimate: float,
    time_estimate: int,
    description: str = "",
    db: Session = Depends(get_db)
):
    """Create a new strategy."""
    try:
        service = StrategyService(db)
        strategy = service.create(
            name=name,
            category=category,
            risk_reduction_pct=risk_reduction_pct,
            cost_estimate=cost_estimate,
            time_estimate=time_estimate,
            description=description
        )
        
        return {
            "success": True,
            "message": "Strategy created",
            "strategy": {
                "id": strategy.id,
                "name": strategy.name,
                "category": strategy.category.value
            }
        }
    except Exception as e:
        logger.error(f"Error creating strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

