"""
RiskAdvisor - Layer 2: Constraint Negotiation Engine
=====================================================
Intelligent constraint handling that learns, negotiates, and proposes alternatives.

Key Features:
- Hard vs Soft constraint classification
- Learned constraints from historical data
- Alternative generation when constraints can't be satisfied
- Negotiation package generation

Author: Umang Kumar
Date: January 2026
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import numpy as np
from datetime import datetime
import logging

from src.core.optimizer import Strategy, Constraint, OptimizationResult, CoreOptimizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================
# DATA MODELS
# ============================================

class ConstraintType(Enum):
    HARD = "hard"      # Non-negotiable (regulatory, safety)
    SOFT = "soft"      # Negotiable with trade-offs
    LEARNED = "learned"  # Discovered from historical patterns


@dataclass
class NegotiableConstraint(Constraint):
    """Extended constraint with negotiation metadata."""
    constraint_type_enum: ConstraintType = ConstraintType.SOFT
    
    # Negotiation parameters
    relaxation_cost: float = 0  # Cost per unit of relaxation
    max_relaxation: float = 0   # Maximum amount it can be relaxed
    approval_required: str = "manager"  # Who can approve relaxation
    
    # Learned (from history)
    historical_average: float = 0
    historical_std: float = 0
    seasonal_adjustment: float = 0  # e.g., +20% in Q4
    
    def get_adjusted_value(self, context: Dict = None) -> float:
        """Get constraint value adjusted for context."""
        base = self.max_value
        
        # Apply seasonal adjustment
        if context and context.get("quarter") == "Q4":
            base *= (1 + self.seasonal_adjustment)
        
        return base


@dataclass
class NegotiationOption:
    """A single alternative when constraints can't be met."""
    option_id: str
    title: str
    description: str
    
    # What changes
    constraint_relaxations: Dict[str, float] = field(default_factory=dict)
    strategy_modifications: List[str] = field(default_factory=list)
    
    # Outcomes
    cost: float = 0
    risk_reduction: float = 0
    timeline_days: int = 0
    
    # Approval
    requires_approval: str = "manager"
    business_case: str = ""
    
    # Feasibility
    feasibility_score: float = 0.0  # 0-1


@dataclass
class NegotiationPackage:
    """Complete package of alternatives when optimal can't be achieved."""
    original_gap: Dict[str, float]  # What's missing
    
    options: List[NegotiationOption] = field(default_factory=list)
    
    recommended_option: Optional[str] = None
    recommendation_reason: str = ""
    
    created_at: datetime = field(default_factory=datetime.now)


# ============================================
# CONSTRAINT NEGOTIATION ENGINE
# ============================================

class ConstraintNegotiationEngine:
    """
    Intelligent constraint handling engine.
    
    When constraints can't be satisfied:
    1. Identifies the gap
    2. Classifies which constraints are negotiable
    3. Generates alternative approaches
    4. Creates a negotiation package
    """
    
    def __init__(
        self,
        strategies: List[Strategy],
        constraints: List[NegotiableConstraint],
        historical_implementations: List[Dict] = None
    ):
        self.strategies = strategies
        self.constraints = constraints
        self.historical = historical_implementations or []
        
    def check_feasibility(
        self,
        required_budget: float,
        required_timeline: int,
        available_budget: float,
        available_timeline: int
    ) -> Tuple[bool, Dict[str, float]]:
        """
        Check if solution is feasible given constraints.
        Returns (feasible, gaps).
        """
        gaps = {}
        
        if required_budget > available_budget:
            gaps["budget"] = required_budget - available_budget
        
        if required_timeline > available_timeline:
            gaps["timeline"] = required_timeline - available_timeline
        
        return len(gaps) == 0, gaps
    
    def learn_from_history(self) -> Dict[str, float]:
        """
        Learn constraint adjustments from historical implementations.
        """
        learnings = {}
        
        if not self.historical:
            return learnings
        
        # Analyze cost overruns
        cost_ratios = []
        for impl in self.historical:
            if impl.get("predicted_cost") and impl.get("actual_cost"):
                ratio = impl["actual_cost"] / impl["predicted_cost"]
                cost_ratios.append(ratio)
        
        if cost_ratios:
            learnings["cost_adjustment"] = np.mean(cost_ratios)
            learnings["cost_std"] = np.std(cost_ratios)
            logger.info(f"Learned: Costs typically {learnings['cost_adjustment']:.0%} of estimates")
        
        # Analyze timeline overruns
        time_ratios = []
        for impl in self.historical:
            if impl.get("predicted_days") and impl.get("actual_days"):
                ratio = impl["actual_days"] / impl["predicted_days"]
                time_ratios.append(ratio)
        
        if time_ratios:
            learnings["timeline_adjustment"] = np.mean(time_ratios)
            learnings["timeline_std"] = np.std(time_ratios)
            logger.info(f"Learned: Timelines typically {learnings['timeline_adjustment']:.0%} of estimates")
        
        return learnings
    
    def generate_negotiation_package(
        self,
        optimal_result: OptimizationResult,
        available_budget: float,
        available_timeline: int,
        context: Dict = None
    ) -> NegotiationPackage:
        """
        Generate alternatives when optimal solution can't be achieved.
        
        Returns multiple options:
        1. Phased implementation
        2. Risk-adjusted (lower) portfolio
        3. Cross-functional funding
        4. ROI-based emergency request
        5. Alternative resourcing
        """
        feasible, gaps = self.check_feasibility(
            optimal_result.total_cost,
            optimal_result.total_timeline_days,
            available_budget,
            available_timeline
        )
        
        if feasible:
            return NegotiationPackage(
                original_gap={},
                options=[],
                recommended_option="optimal",
                recommendation_reason="Original plan is feasible"
            )
        
        options = []
        
        # OPTION 1: Phased Implementation
        if gaps.get("budget", 0) > 0:
            phase1_strategies = self._select_quick_wins(
                optimal_result.selected_strategies,
                available_budget * 0.8
            )
            
            phase2_strategies = [
                s for s in optimal_result.selected_strategies 
                if s not in phase1_strategies
            ]
            
            phase1_cost = sum(s.cost_estimate for s in phase1_strategies)
            phase1_reduction = sum(s.risk_reduction_pct for s in phase1_strategies)
            
            options.append(NegotiationOption(
                option_id="PHASED_001",
                title="Phased Implementation",
                description=f"Phase 1 now (${phase1_cost:,.0f}), Phase 2 next quarter",
                constraint_relaxations={"budget": available_budget - phase1_cost},
                cost=phase1_cost,
                risk_reduction=phase1_reduction,
                timeline_days=60,
                requires_approval="manager",
                business_case="Deliver value NOW, secure Phase 2 funding based on results",
                feasibility_score=0.9
            ))
        
        # OPTION 2: Risk-Adjusted Portfolio
        core_optimizer = CoreOptimizer(self.strategies, [])
        conservative_result = core_optimizer.get_optimal_portfolio(
            budget_limit=available_budget,
            timeline_limit=available_timeline,
            risk_tolerance="conservative"
        )
        
        options.append(NegotiationOption(
            option_id="RISKADJUST_001",
            title="Risk-Adjusted Portfolio",
            description=f"Reduced scope, {conservative_result.total_risk_reduction:.0f}% risk reduction",
            cost=conservative_result.total_cost,
            risk_reduction=conservative_result.total_risk_reduction,
            timeline_days=conservative_result.total_timeline_days,
            requires_approval="team",
            business_case="Stay within budget, accept lower risk reduction",
            feasibility_score=0.95
        ))
        
        # OPTION 3: Cross-Functional Funding
        if gaps.get("budget", 0) > 0:
            budget_gap = gaps["budget"]
            
            options.append(NegotiationOption(
                option_id="CROSSFUND_001",
                title="Cross-Functional Funding",
                description="Split costs across Safety, Operations, and Maintenance",
                constraint_relaxations={"budget": 0},  # No relaxation needed
                cost=optimal_result.total_cost,
                risk_reduction=optimal_result.total_risk_reduction,
                timeline_days=optimal_result.total_timeline_days,
                requires_approval="director",
                business_case=f"Safety: ${available_budget:,.0f}, Ops contribution: ${budget_gap * 0.6:,.0f}, Maint: ${budget_gap * 0.4:,.0f}",
                feasibility_score=0.7
            ))
        
        # OPTION 4: ROI-Based Emergency Request
        if gaps.get("budget", 0) > 0:
            budget_gap = gaps["budget"]
            avoided_incident_cost = optimal_result.total_risk_reduction * 100000  # $100K per 1%
            roi = avoided_incident_cost / optimal_result.total_cost
            payback_months = (optimal_result.total_cost / (avoided_incident_cost / 12))
            
            options.append(NegotiationOption(
                option_id="EMERGENCY_001",
                title="ROI-Based Emergency Funding Request",
                description=f"Request ${budget_gap:,.0f} additional with {roi:.1f}x ROI",
                constraint_relaxations={"budget": -budget_gap},  # Increase budget
                cost=optimal_result.total_cost,
                risk_reduction=optimal_result.total_risk_reduction,
                timeline_days=optimal_result.total_timeline_days,
                requires_approval="vp",
                business_case=f"ROI: {roi:.1f}x, Payback: {payback_months:.1f} months, Avoids ${avoided_incident_cost:,.0f} in incident costs",
                feasibility_score=0.6
            ))
        
        # OPTION 5: Alternative Resourcing
        options.append(NegotiationOption(
            option_id="ALTRESOURCE_001",
            title="Alternative Resourcing Strategy",
            description="Internal resources + timeline extension + bulk purchasing",
            constraint_relaxations={"timeline": 60},  # Extend by 60 days
            cost=optimal_result.total_cost * 0.75,  # 25% savings
            risk_reduction=optimal_result.total_risk_reduction * 0.95,  # Slight reduction
            timeline_days=optimal_result.total_timeline_days + 60,
            requires_approval="manager",
            business_case="Use internal resources, extend timeline, bulk purchase for savings",
            feasibility_score=0.85
        ))
        
        # Select recommended option
        # Prefer high feasibility + high risk reduction
        best_option = max(
            options,
            key=lambda x: x.feasibility_score * (x.risk_reduction / 100)
        )
        
        return NegotiationPackage(
            original_gap=gaps,
            options=options,
            recommended_option=best_option.option_id,
            recommendation_reason=f"Best balance of feasibility ({best_option.feasibility_score:.0%}) and effectiveness ({best_option.risk_reduction:.0f}%)"
        )
    
    def _select_quick_wins(
        self,
        strategies: List[Strategy],
        max_budget: float
    ) -> List[Strategy]:
        """Select high-value strategies that fit in budget."""
        # Sort by cost-effectiveness (risk reduction per dollar)
        sorted_strats = sorted(
            strategies,
            key=lambda s: s.risk_reduction_pct / s.cost_estimate if s.cost_estimate > 0 else 0,
            reverse=True
        )
        
        selected = []
        total_cost = 0
        
        for s in sorted_strats:
            if total_cost + s.cost_estimate <= max_budget:
                selected.append(s)
                total_cost += s.cost_estimate
        
        return selected
    
    def challenge_constraint(
        self,
        constraint_name: str,
        proposed_value: float
    ) -> Dict:
        """
        Challenge a constraint with business justification.
        
        Returns analysis of what's gained by relaxing the constraint.
        """
        constraint = next(
            (c for c in self.constraints if c.name == constraint_name),
            None
        )
        
        if not constraint:
            return {"error": f"Constraint '{constraint_name}' not found"}
        
        if constraint.constraint_type_enum == ConstraintType.HARD:
            return {
                "constraint": constraint_name,
                "challengeable": False,
                "reason": "This is a hard constraint (regulatory/safety) and cannot be relaxed"
            }
        
        # Calculate benefit of relaxation
        relaxation_amount = proposed_value - constraint.max_value
        
        # Estimate additional risk reduction possible
        optimizer = CoreOptimizer(self.strategies, [])
        
        original_result = optimizer.get_optimal_portfolio(
            budget_limit=constraint.max_value if constraint.category == "budget" else float('inf'),
            risk_tolerance="balanced"
        )
        
        relaxed_result = optimizer.get_optimal_portfolio(
            budget_limit=proposed_value if constraint.category == "budget" else float('inf'),
            risk_tolerance="balanced"
        )
        
        additional_reduction = relaxed_result.total_risk_reduction - original_result.total_risk_reduction
        
        return {
            "constraint": constraint_name,
            "challengeable": True,
            "current_value": constraint.max_value,
            "proposed_value": proposed_value,
            "relaxation_amount": relaxation_amount,
            "additional_risk_reduction": additional_reduction,
            "risk_reduction_per_unit": additional_reduction / relaxation_amount if relaxation_amount > 0 else 0,
            "approval_required": constraint.approval_required,
            "recommendation": f"Every ${relaxation_amount/1000:.0f}K additional budget = {additional_reduction:.1f}% more risk reduction"
        }


# ============================================
# EXAMPLE USAGE
# ============================================

if __name__ == "__main__":
    from src.core.optimizer import Strategy, StrategyCategory
    
    # Sample strategies
    strategies = [
        Strategy(
            id="MAINT_001", name="Enhanced Maintenance",
            category=StrategyCategory.MAINTENANCE,
            risk_reduction_pct=18.0,
            cost_estimate=120000, cost_min=80000, cost_max=150000,
            time_estimate=45
        ),
        Strategy(
            id="TRAIN_001", name="Fatigue Training",
            category=StrategyCategory.TRAINING,
            risk_reduction_pct=12.0,
            cost_estimate=45000, cost_min=30000, cost_max=60000,
            time_estimate=21
        ),
        Strategy(
            id="TECH_001", name="Predictive Maintenance",
            category=StrategyCategory.TECHNOLOGY,
            risk_reduction_pct=25.0,
            cost_estimate=280000, cost_min=200000, cost_max=350000,
            time_estimate=120
        ),
    ]
    
    # Constraints
    constraints = [
        NegotiableConstraint(
            name="Q1 Budget",
            constraint_type="soft",
            category="budget",
            max_value=200000,
            constraint_type_enum=ConstraintType.SOFT,
            max_relaxation=100000,
            approval_required="director"
        ),
    ]
    
    # Engine
    engine = ConstraintNegotiationEngine(strategies, constraints)
    
    # Get optimal (which requires more budget)
    optimizer = CoreOptimizer(strategies, [])
    optimal = optimizer.get_optimal_portfolio(
        budget_limit=500000,  # If we had unlimited budget
        risk_tolerance="balanced"
    )
    
    print("=" * 60)
    print("🤝 RiskAdvisor - Constraint Negotiation Engine")
    print("=" * 60)
    
    print(f"\n💰 OPTIMAL SOLUTION:")
    print(f"   Cost: ${optimal.total_cost:,.0f}")
    print(f"   Risk Reduction: {optimal.total_risk_reduction:.1f}%")
    
    print(f"\n⚠️  AVAILABLE BUDGET: $200,000")
    print(f"   GAP: ${optimal.total_cost - 200000:,.0f}")
    
    # Generate negotiation package
    package = engine.generate_negotiation_package(
        optimal_result=optimal,
        available_budget=200000,
        available_timeline=90
    )
    
    print(f"\n📋 NEGOTIATION OPTIONS:")
    for opt in package.options:
        print(f"\n   {opt.option_id}: {opt.title}")
        print(f"   └─ Cost: ${opt.cost:,.0f}")
        print(f"   └─ Risk Reduction: {opt.risk_reduction:.1f}%")
        print(f"   └─ Feasibility: {opt.feasibility_score:.0%}")
        print(f"   └─ Business Case: {opt.business_case[:60]}...")
    
    print(f"\n✅ RECOMMENDED: {package.recommended_option}")
    print(f"   Reason: {package.recommendation_reason}")
    
    print("\n" + "=" * 60)
