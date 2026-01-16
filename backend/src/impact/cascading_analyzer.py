"""
RiskAdvisor - Layer 3: Cascading Impact Analyzer
=================================================
Models first, second, and third-order effects of strategies.

Key Features:
- Direct impact calculation
- Ripple effects (resource, schedule, financial)
- Total cost of ownership calculation
- Dependency graph analysis

Author: Umang Kumar
Date: January 2026
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import numpy as np
import logging

from src.core.optimizer import Strategy, OptimizationResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================
# DATA MODELS
# ============================================

class ImpactOrder(Enum):
    FIRST = 1   # Direct effects
    SECOND = 2  # Ripple effects
    THIRD = 3   # Systemic effects


class ImpactCategory(Enum):
    RESOURCE = "resource"       # Staff, equipment, space
    FINANCIAL = "financial"     # Budget, revenue, costs
    OPERATIONAL = "operational" # Schedule, availability
    ORGANIZATIONAL = "organizational"  # Culture, morale
    COMPLIANCE = "compliance"   # Regulatory, audit


@dataclass
class ImpactEffect:
    """A single impact effect."""
    effect_id: str
    description: str
    order: ImpactOrder
    category: ImpactCategory
    
    # Quantification
    metric: str  # e.g., "cost", "fte", "days"
    value: float
    unit: str  # e.g., "$", "FTE", "days"
    
    # Likelihood
    probability: float = 1.0  # Probability this effect occurs
    
    # Dependencies
    triggers: List[str] = field(default_factory=list)  # What triggers this
    triggered_by: Optional[str] = None  # Parent effect
    
    # Business context
    mitigation: Optional[str] = None  # How to mitigate
    mitigation_cost: float = 0


@dataclass
class CascadeChain:
    """A chain of cascading effects."""
    root_strategy_id: str
    chain: List[ImpactEffect] = field(default_factory=list)
    
    @property
    def total_financial_impact(self) -> float:
        """Sum of all financial impacts."""
        return sum(
            e.value for e in self.chain 
            if e.category == ImpactCategory.FINANCIAL
        )
    
    @property
    def max_order(self) -> int:
        """Maximum order of effects in chain."""
        return max((e.order.value for e in self.chain), default=0)


@dataclass
class TotalCostAnalysis:
    """Complete cost analysis including all orders of effects."""
    strategy_id: str
    strategy_name: str
    
    # Direct costs
    direct_cost: float
    
    # Cascading costs
    second_order_cost: float
    third_order_cost: float
    
    # Total
    total_cost_of_ownership: float
    
    # Breakdown
    resource_impact: float
    operational_impact: float
    hidden_costs: float
    
    # Comparison
    cost_multiplier: float  # total / direct
    
    # Effects detail
    effects: List[ImpactEffect] = field(default_factory=list)
    
    # Justification
    still_recommended: bool = True
    justification: str = ""


# ============================================
# CASCADING IMPACT ANALYZER
# ============================================

class CascadingImpactAnalyzer:
    """
    Analyzes first, second, and third-order effects of strategies.
    
    Example cascade:
    Strategy: Increase maintenance by 25%
    
    FIRST ORDER:
    - Risk reduction: -18%
    - Direct cost: $120K
    
    SECOND ORDER:
    - Bay utilization: 75% → 94% (triggers hiring)
    - Hiring 2 technicians: +$150K
    - Hiring takes 60 days (extends timeline)
    
    THIRD ORDER:
    - Overtime increases 15% (fatigue risk)
    - Quality defects may increase 3%
    - Requires quality control enhancement: +$30K
    """
    
    def __init__(
        self,
        organizational_params: Dict = None
    ):
        self.params = organizational_params or self._default_params()
        
        # Impact rules library
        self.impact_rules = self._build_impact_rules()
    
    def _default_params(self) -> Dict:
        """Default organizational parameters."""
        return {
            # Resource utilization
            "maintenance_bay_utilization": 0.75,
            "maintenance_bay_capacity_threshold": 0.90,
            "technician_hourly_cost": 75,
            "technician_annual_cost": 150000,
            "hiring_time_days": 60,
            
            # Operations
            "fleet_size": 50,
            "daily_flights_per_aircraft": 4,
            "revenue_per_flight": 15000,
            "aog_cost_per_day": 50000,  # Aircraft on ground
            
            # Training
            "training_hours_per_person": 8,
            "training_cost_per_hour": 100,
            "productivity_loss_during_training": 0.3,
            
            # Supply chain
            "parts_inventory_buffer_weeks": 4,
            "parts_cost_per_maintenance": 5000,
            "bulk_discount_threshold": 1.25,  # 25% volume increase
            "bulk_discount_rate": 0.15,
            
            # Human factors
            "overtime_fatigue_threshold": 0.15,  # 15% overtime = fatigue concern
            "fatigue_quality_impact": 0.03,  # 3% quality degradation
        }
    
    def _build_impact_rules(self) -> List[Dict]:
        """Build library of impact rules."""
        return [
            # Maintenance strategy impacts
            {
                "strategy_category": "maintenance",
                "trigger_condition": lambda s, p: s.risk_reduction_pct > 15,
                "effects": [
                    {
                        "order": ImpactOrder.SECOND,
                        "category": ImpactCategory.RESOURCE,
                        "description": "Maintenance bay capacity impact",
                        "calculate": lambda s, p: {
                            "new_utilization": min(1.0, p["maintenance_bay_utilization"] + 0.19),
                            "needs_expansion": p["maintenance_bay_utilization"] + 0.19 > p["maintenance_bay_capacity_threshold"]
                        }
                    },
                    {
                        "order": ImpactOrder.SECOND,
                        "category": ImpactCategory.FINANCIAL,
                        "description": "Additional technician hiring",
                        "condition": lambda calc: calc.get("needs_expansion", False),
                        "calculate": lambda s, p: {
                            "fte_needed": 2,
                            "cost": 2 * p["technician_annual_cost"],
                            "timeline_extension": p["hiring_time_days"]
                        }
                    },
                ]
            },
            # Training strategy impacts
            {
                "strategy_category": "training",
                "trigger_condition": lambda s, p: s.risk_reduction_pct > 10,
                "effects": [
                    {
                        "order": ImpactOrder.SECOND,
                        "category": ImpactCategory.OPERATIONAL,
                        "description": "Training schedule productivity loss",
                        "calculate": lambda s, p: {
                            "productivity_loss_pct": p["productivity_loss_during_training"],
                            "cost": p["training_hours_per_person"] * p["training_cost_per_hour"] * 50  # 50 staff
                        }
                    }
                ]
            },
            # Technology strategy impacts
            {
                "strategy_category": "technology",
                "trigger_condition": lambda s, p: s.cost_estimate > 200000,
                "effects": [
                    {
                        "order": ImpactOrder.SECOND,
                        "category": ImpactCategory.ORGANIZATIONAL,
                        "description": "Change management and user training",
                        "calculate": lambda s, p: {
                            "cost": s.cost_estimate * 0.20,  # 20% of tech cost
                            "timeline_extension": 30
                        }
                    },
                    {
                        "order": ImpactOrder.THIRD,
                        "category": ImpactCategory.OPERATIONAL,
                        "description": "Initial productivity dip during transition",
                        "calculate": lambda s, p: {
                            "productivity_dip_weeks": 4,
                            "cost": 4 * 5 * p["revenue_per_flight"] * 0.05  # 5% revenue impact for 4 weeks
                        }
                    }
                ]
            },
        ]
    
    def analyze_strategy(
        self,
        strategy: Strategy,
        include_third_order: bool = True
    ) -> TotalCostAnalysis:
        """
        Analyze complete cost including cascading effects.
        """
        effects = []
        second_order_cost = 0
        third_order_cost = 0
        resource_impact = 0
        operational_impact = 0
        
        # First order effects (direct)
        effects.append(ImpactEffect(
            effect_id=f"{strategy.id}_DIRECT",
            description=f"Direct implementation cost",
            order=ImpactOrder.FIRST,
            category=ImpactCategory.FINANCIAL,
            metric="cost",
            value=strategy.cost_estimate,
            unit="$"
        ))
        
        # Check each impact rule
        for rule in self.impact_rules:
            if strategy.category.value != rule["strategy_category"]:
                continue
            
            if not rule["trigger_condition"](strategy, self.params):
                continue
            
            previous_calc = {}
            
            for effect_def in rule["effects"]:
                # Check condition if exists
                if "condition" in effect_def:
                    if not effect_def["condition"](previous_calc):
                        continue
                
                # Calculate effect
                calc_result = effect_def["calculate"](strategy, self.params)
                previous_calc.update(calc_result)
                
                cost_value = calc_result.get("cost", 0)
                
                effect = ImpactEffect(
                    effect_id=f"{strategy.id}_{effect_def['order'].name}_{len(effects)}",
                    description=effect_def["description"],
                    order=effect_def["order"],
                    category=effect_def["category"],
                    metric="cost",
                    value=cost_value,
                    unit="$"
                )
                effects.append(effect)
                
                # Accumulate by order
                if effect_def["order"] == ImpactOrder.SECOND:
                    second_order_cost += cost_value
                elif effect_def["order"] == ImpactOrder.THIRD:
                    third_order_cost += cost_value
                
                # Accumulate by category
                if effect_def["category"] == ImpactCategory.RESOURCE:
                    resource_impact += cost_value
                elif effect_def["category"] == ImpactCategory.OPERATIONAL:
                    operational_impact += cost_value
        
        total_cost = strategy.cost_estimate + second_order_cost + third_order_cost
        hidden_costs = second_order_cost + third_order_cost
        
        # Calculate if still recommended
        # Assume avoided incident cost is $100K per 1% risk reduction
        avoided_cost = strategy.risk_reduction_pct * 100000
        still_recommended = avoided_cost > total_cost
        
        justification = (
            f"Strategy costs ${total_cost:,.0f} (direct: ${strategy.cost_estimate:,.0f} + "
            f"hidden: ${hidden_costs:,.0f}), but prevents ${avoided_cost:,.0f} in incident costs. "
            f"Net benefit: ${avoided_cost - total_cost:,.0f}."
            if still_recommended else
            f"Total cost ${total_cost:,.0f} exceeds avoided incident cost ${avoided_cost:,.0f}. "
            f"Consider alternatives."
        )
        
        return TotalCostAnalysis(
            strategy_id=strategy.id,
            strategy_name=strategy.name,
            direct_cost=strategy.cost_estimate,
            second_order_cost=second_order_cost,
            third_order_cost=third_order_cost,
            total_cost_of_ownership=total_cost,
            resource_impact=resource_impact,
            operational_impact=operational_impact,
            hidden_costs=hidden_costs,
            cost_multiplier=total_cost / strategy.cost_estimate if strategy.cost_estimate > 0 else 1,
            effects=effects,
            still_recommended=still_recommended,
            justification=justification
        )
    
    def analyze_portfolio(
        self,
        result: OptimizationResult
    ) -> Dict:
        """Analyze cascading impacts for entire portfolio."""
        analyses = []
        total_direct = 0
        total_hidden = 0
        total_tco = 0
        
        for strategy in result.selected_strategies:
            analysis = self.analyze_strategy(strategy)
            analyses.append(analysis)
            total_direct += analysis.direct_cost
            total_hidden += analysis.hidden_costs
            total_tco += analysis.total_cost_of_ownership
        
        return {
            "portfolio_size": len(result.selected_strategies),
            "original_reported_cost": result.total_cost,
            "total_direct_cost": total_direct,
            "total_hidden_costs": total_hidden,
            "total_cost_of_ownership": total_tco,
            "cost_multiplier": total_tco / total_direct if total_direct > 0 else 1,
            "risk_reduction": result.total_risk_reduction,
            "strategy_analyses": analyses,
            "summary": f"Portfolio costs ${total_direct:,.0f} on paper but TRUE total cost is ${total_tco:,.0f} when including ripple effects (${total_hidden:,.0f} hidden costs)."
        }
    
    def generate_impact_tree(
        self,
        strategy: Strategy
    ) -> str:
        """Generate ASCII tree visualization of impacts."""
        analysis = self.analyze_strategy(strategy)
        
        lines = [
            f"STRATEGY: {strategy.name}",
            "",
            "FIRST-ORDER EFFECTS (Direct):",
            f"├─ Risk reduction: -{strategy.risk_reduction_pct}%",
            f"├─ Direct cost: ${strategy.cost_estimate:,.0f}",
            f"└─ Timeline: {strategy.time_estimate} days",
        ]
        
        second_order = [e for e in analysis.effects if e.order == ImpactOrder.SECOND]
        if second_order:
            lines.append("")
            lines.append("SECOND-ORDER EFFECTS (Ripple):")
            for i, effect in enumerate(second_order):
                prefix = "└─" if i == len(second_order) - 1 else "├─"
                lines.append(f"{prefix} {effect.description}")
                lines.append(f"   └─ Impact: ${effect.value:,.0f}")
        
        third_order = [e for e in analysis.effects if e.order == ImpactOrder.THIRD]
        if third_order:
            lines.append("")
            lines.append("THIRD-ORDER EFFECTS (Systemic):")
            for i, effect in enumerate(third_order):
                prefix = "└─" if i == len(third_order) - 1 else "├─"
                lines.append(f"{prefix} {effect.description}")
                lines.append(f"   └─ Impact: ${effect.value:,.0f}")
        
        lines.append("")
        lines.append(f"TOTAL COST OF OWNERSHIP: ${analysis.total_cost_of_ownership:,.0f}")
        lines.append(f"({analysis.cost_multiplier:.1f}x the direct cost)")
        lines.append("")
        lines.append(f"VERDICT: {'✅ STILL RECOMMENDED' if analysis.still_recommended else '❌ RECONSIDER'}")
        lines.append(analysis.justification)
        
        return "\n".join(lines)


# ============================================
# EXAMPLE USAGE
# ============================================

if __name__ == "__main__":
    from src.core.optimizer import Strategy, StrategyCategory
    
    # Sample strategy
    strategy = Strategy(
        id="MAINT_001",
        name="Increase maintenance frequency by 25%",
        category=StrategyCategory.MAINTENANCE,
        risk_reduction_pct=18.0,
        cost_min=80000, cost_max=150000, cost_estimate=120000,
        time_min=30, time_max=60, time_estimate=45
    )
    
    # Analyzer
    analyzer = CascadingImpactAnalyzer()
    
    print("=" * 70)
    print("📊 RiskAdvisor - Cascading Impact Analysis")
    print("=" * 70)
    print()
    print(analyzer.generate_impact_tree(strategy))
    print("=" * 70)
