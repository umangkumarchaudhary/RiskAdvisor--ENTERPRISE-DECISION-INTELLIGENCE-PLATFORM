"""
RiskAdvisor - Layer 5: Multi-Horizon Optimization
===================================================
Optimizes across three time horizons simultaneously.

Horizons:
- IMMEDIATE (0-30 days): Emergency interventions, quick wins
- TACTICAL (30-180 days): Systematic improvements, training
- STRATEGIC (180+ days): Transformational investments

Key Features:
- Inter-temporal trade-off analysis
- Horizon-specific constraints
- Phase sequencing optimization
- Value chain across horizons

Author: Umang Kumar
Date: January 2026
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import numpy as np
import logging
from copy import deepcopy

from src.core.optimizer import Strategy, OptimizationResult, CoreOptimizer, StrategyCategory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================
# DATA MODELS
# ============================================

class Horizon(Enum):
    IMMEDIATE = "immediate"    # 0-30 days
    TACTICAL = "tactical"      # 30-180 days
    STRATEGIC = "strategic"    # 180+ days


@dataclass
class HorizonConfig:
    """Configuration for a time horizon."""
    horizon: Horizon
    label: str
    min_days: int
    max_days: int
    
    # Budget allocation (as fraction of total)
    budget_fraction_min: float = 0
    budget_fraction_max: float = 1
    budget_fraction_recommended: float = 0.33
    
    # Strategy preferences
    preferred_categories: List[StrategyCategory] = field(default_factory=list)
    max_complexity: str = "high"  # low, medium, high
    
    # Objectives
    primary_objective: str = "risk_reduction"  # or "quick_wins" or "transformation"


@dataclass
class HorizonPlan:
    """Optimized plan for a single horizon."""
    horizon: Horizon
    strategies: List[Strategy]
    
    # Outcomes
    total_cost: float
    risk_reduction: float
    timeline_days: int
    
    # Metadata
    action_items: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    decision_deadline: str = ""


@dataclass
class MultiHorizonPlan:
    """Complete multi-horizon optimization result."""
    # Individual horizon plans
    immediate_plan: HorizonPlan
    tactical_plan: HorizonPlan
    strategic_plan: HorizonPlan
    
    # Aggregates
    total_cost: float
    total_risk_reduction: float
    
    # Trade-off analysis
    immediate_vs_sustainable_tradeoff: Dict = field(default_factory=dict)
    
    # Phase sequencing
    phase_sequence: List[Dict] = field(default_factory=list)
    
    # Interdependencies
    cross_horizon_dependencies: List[Dict] = field(default_factory=list)


# ============================================
# MULTI-HORIZON OPTIMIZER
# ============================================

class MultiHorizonOptimizer:
    """
    Optimizes strategy portfolios across three time horizons.
    
    This is THE key differentiator - solving:
    1. "What do I do THIS WEEK?" (Immediate)
    2. "What do I implement THIS QUARTER?" (Tactical)
    3. "What do I invest in THIS YEAR?" (Strategic)
    
    And showing trade-offs between short-term patches vs long-term solutions.
    """
    
    def __init__(
        self,
        strategies: List[Strategy],
        total_budget: float,
        risk_score: float = 50.0
    ):
        self.strategies = strategies
        self.total_budget = total_budget
        self.risk_score = risk_score
        
        # Configure horizons
        self.horizons = self._configure_horizons()
        
        # Classify strategies by horizon suitability
        self.strategy_horizons = self._classify_strategies()
    
    def _configure_horizons(self) -> Dict[Horizon, HorizonConfig]:
        """Configure each time horizon."""
        return {
            Horizon.IMMEDIATE: HorizonConfig(
                horizon=Horizon.IMMEDIATE,
                label="Immediate Actions (0-30 days)",
                min_days=0,
                max_days=30,
                budget_fraction_min=0.1,
                budget_fraction_max=0.4,
                budget_fraction_recommended=0.25,
                preferred_categories=[StrategyCategory.PROCESS, StrategyCategory.POLICY],
                max_complexity="low",
                primary_objective="quick_wins"
            ),
            Horizon.TACTICAL: HorizonConfig(
                horizon=Horizon.TACTICAL,
                label="Tactical Improvements (30-180 days)",
                min_days=30,
                max_days=180,
                budget_fraction_min=0.3,
                budget_fraction_max=0.5,
                budget_fraction_recommended=0.45,
                preferred_categories=[StrategyCategory.TRAINING, StrategyCategory.MAINTENANCE],
                max_complexity="medium",
                primary_objective="risk_reduction"
            ),
            Horizon.STRATEGIC: HorizonConfig(
                horizon=Horizon.STRATEGIC,
                label="Strategic Investments (180+ days)",
                min_days=180,
                max_days=730,  # Up to 2 years
                budget_fraction_min=0.2,
                budget_fraction_max=0.5,
                budget_fraction_recommended=0.30,
                preferred_categories=[StrategyCategory.TECHNOLOGY],
                max_complexity="high",
                primary_objective="transformation"
            ),
        }
    
    def _classify_strategies(self) -> Dict[str, List[Horizon]]:
        """Classify each strategy by suitable horizons."""
        classification = {}
        
        for strategy in self.strategies:
            suitable_horizons = []
            
            # Immediate: Low cost, fast implementation
            if strategy.time_estimate <= 30 and strategy.cost_estimate < 50000:
                suitable_horizons.append(Horizon.IMMEDIATE)
            
            # Tactical: Medium complexity
            if 14 <= strategy.time_estimate <= 180:
                suitable_horizons.append(Horizon.TACTICAL)
            
            # Strategic: High investment, long-term
            if strategy.time_estimate >= 60 or strategy.cost_estimate >= 200000:
                suitable_horizons.append(Horizon.STRATEGIC)
            
            # Technology is usually strategic
            if strategy.category == StrategyCategory.TECHNOLOGY:
                if Horizon.STRATEGIC not in suitable_horizons:
                    suitable_horizons.append(Horizon.STRATEGIC)
            
            classification[strategy.id] = suitable_horizons if suitable_horizons else [Horizon.TACTICAL]
        
        return classification
    
    def optimize_horizon(
        self,
        horizon: Horizon,
        budget: float,
        excluded_strategies: List[str] = None
    ) -> HorizonPlan:
        """Optimize for a single horizon."""
        config = self.horizons[horizon]
        excluded = excluded_strategies or []
        
        # Filter strategies suitable for this horizon
        suitable_strategies = [
            s for s in self.strategies
            if s.id not in excluded
            and horizon in self.strategy_horizons.get(s.id, [])
            and s.time_estimate <= config.max_days
        ]
        
        # Prioritize by category preference
        def priority_score(s: Strategy) -> float:
            category_bonus = 1.5 if s.category in config.preferred_categories else 1.0
            efficiency = s.risk_reduction_pct / s.cost_estimate if s.cost_estimate > 0 else 0
            return efficiency * category_bonus
        
        suitable_strategies.sort(key=priority_score, reverse=True)
        
        # Greedy selection within budget
        selected = []
        total_cost = 0
        
        for strategy in suitable_strategies:
            if total_cost + strategy.cost_estimate <= budget:
                selected.append(strategy)
                total_cost += strategy.cost_estimate
        
        # Calculate outcomes
        risk_reduction = sum(s.risk_reduction_pct for s in selected)
        timeline = max((s.time_estimate for s in selected), default=0)
        
        # Generate action items
        action_items = []
        for s in selected:
            if horizon == Horizon.IMMEDIATE:
                action_items.append(f"⚡ START NOW: {s.name}")
            elif horizon == Horizon.TACTICAL:
                action_items.append(f"📋 PLAN Q1/Q2: {s.name}")
            else:
                action_items.append(f"🎯 BUDGET FY: {s.name}")
        
        return HorizonPlan(
            horizon=horizon,
            strategies=selected,
            total_cost=total_cost,
            risk_reduction=min(risk_reduction, 50),  # Cap per horizon
            timeline_days=timeline,
            action_items=action_items,
            decision_deadline=self._get_decision_deadline(horizon)
        )
    
    def _get_decision_deadline(self, horizon: Horizon) -> str:
        """Get decision deadline based on horizon."""
        if horizon == Horizon.IMMEDIATE:
            return "Decision required: TODAY"
        elif horizon == Horizon.TACTICAL:
            return "Decision required: This week"
        else:
            return "Decision required: This quarter"
    
    def optimize_all_horizons(
        self,
        budget_allocation: Dict[Horizon, float] = None
    ) -> MultiHorizonPlan:
        """
        Optimize across all three horizons.
        
        Args:
            budget_allocation: Optional custom budget per horizon.
                             If None, uses recommended fractions.
        """
        if budget_allocation is None:
            budget_allocation = {
                Horizon.IMMEDIATE: self.total_budget * 0.25,
                Horizon.TACTICAL: self.total_budget * 0.45,
                Horizon.STRATEGIC: self.total_budget * 0.30,
            }
        
        used_strategies = []
        
        # Optimize immediate first (highest urgency)
        immediate = self.optimize_horizon(
            Horizon.IMMEDIATE,
            budget_allocation[Horizon.IMMEDIATE],
            excluded_strategies=used_strategies
        )
        used_strategies.extend([s.id for s in immediate.strategies])
        
        # Optimize tactical
        tactical = self.optimize_horizon(
            Horizon.TACTICAL,
            budget_allocation[Horizon.TACTICAL],
            excluded_strategies=used_strategies
        )
        used_strategies.extend([s.id for s in tactical.strategies])
        
        # Optimize strategic
        strategic = self.optimize_horizon(
            Horizon.STRATEGIC,
            budget_allocation[Horizon.STRATEGIC],
            excluded_strategies=used_strategies
        )
        
        # Calculate totals
        total_cost = immediate.total_cost + tactical.total_cost + strategic.total_cost
        total_risk_reduction = min(
            immediate.risk_reduction + tactical.risk_reduction + strategic.risk_reduction,
            95  # Cap at 95%
        )
        
        # Analyze trade-offs
        tradeoff = self._analyze_tradeoffs(immediate, tactical, strategic)
        
        # Generate phase sequence
        phases = self._generate_phase_sequence(immediate, tactical, strategic)
        
        # Identify cross-horizon dependencies
        dependencies = self._identify_dependencies(immediate, tactical, strategic)
        
        return MultiHorizonPlan(
            immediate_plan=immediate,
            tactical_plan=tactical,
            strategic_plan=strategic,
            total_cost=total_cost,
            total_risk_reduction=total_risk_reduction,
            immediate_vs_sustainable_tradeoff=tradeoff,
            phase_sequence=phases,
            cross_horizon_dependencies=dependencies
        )
    
    def _analyze_tradeoffs(
        self,
        immediate: HorizonPlan,
        tactical: HorizonPlan,
        strategic: HorizonPlan
    ) -> Dict:
        """Analyze trade-offs between horizons."""
        return {
            "quick_fix_value": immediate.risk_reduction,
            "quick_fix_cost": immediate.total_cost,
            "sustainable_value": tactical.risk_reduction + strategic.risk_reduction,
            "sustainable_cost": tactical.total_cost + strategic.total_cost,
            "quick_fix_cost_effectiveness": (
                immediate.risk_reduction / immediate.total_cost * 1000 
                if immediate.total_cost > 0 else 0
            ),
            "sustainable_cost_effectiveness": (
                (tactical.risk_reduction + strategic.risk_reduction) / 
                (tactical.total_cost + strategic.total_cost) * 1000
                if (tactical.total_cost + strategic.total_cost) > 0 else 0
            ),
            "recommendation": self._tradeoff_recommendation(immediate, tactical, strategic)
        }
    
    def _tradeoff_recommendation(
        self,
        immediate: HorizonPlan,
        tactical: HorizonPlan,
        strategic: HorizonPlan
    ) -> str:
        """Generate trade-off recommendation."""
        if self.risk_score >= 75:
            return "URGENT: Prioritize immediate actions, then tactical. Risk is critical."
        elif self.risk_score >= 50:
            return "BALANCED: Execute immediate actions for quick wins, invest heavily in tactical for sustainability."
        else:
            return "STRATEGIC: Focus on long-term improvements. Immediate risk is manageable."
    
    def _generate_phase_sequence(
        self,
        immediate: HorizonPlan,
        tactical: HorizonPlan,
        strategic: HorizonPlan
    ) -> List[Dict]:
        """Generate implementation phase sequence."""
        phases = []
        
        # Phase 1: Immediate
        if immediate.strategies:
            phases.append({
                "phase": 1,
                "name": "Crisis Response / Quick Wins",
                "horizon": "immediate",
                "start_day": 0,
                "end_day": 30,
                "strategies": [s.name for s in immediate.strategies],
                "cost": immediate.total_cost,
                "expected_risk_reduction": immediate.risk_reduction,
                "milestone": f"Achieve {immediate.risk_reduction:.0f}% risk reduction"
            })
        
        # Phase 2: Tactical
        if tactical.strategies:
            phases.append({
                "phase": 2,
                "name": "Systematic Improvement",
                "horizon": "tactical",
                "start_day": 30,
                "end_day": 180,
                "strategies": [s.name for s in tactical.strategies],
                "cost": tactical.total_cost,
                "expected_risk_reduction": tactical.risk_reduction,
                "milestone": f"Cumulative {immediate.risk_reduction + tactical.risk_reduction:.0f}% reduction"
            })
        
        # Phase 3: Strategic
        if strategic.strategies:
            phases.append({
                "phase": 3,
                "name": "Transformational Investment",
                "horizon": "strategic",
                "start_day": 180,
                "end_day": 365,
                "strategies": [s.name for s in strategic.strategies],
                "cost": strategic.total_cost,
                "expected_risk_reduction": strategic.risk_reduction,
                "milestone": f"Target {immediate.risk_reduction + tactical.risk_reduction + strategic.risk_reduction:.0f}% total reduction"
            })
        
        return phases
    
    def _identify_dependencies(
        self,
        immediate: HorizonPlan,
        tactical: HorizonPlan,
        strategic: HorizonPlan
    ) -> List[Dict]:
        """Identify dependencies across horizons."""
        dependencies = []
        
        # Technology strategies often depend on process changes
        for s_strat in strategic.strategies:
            if s_strat.category == StrategyCategory.TECHNOLOGY:
                for t_strat in tactical.strategies:
                    if t_strat.category == StrategyCategory.TRAINING:
                        dependencies.append({
                            "from": s_strat.name,
                            "to": t_strat.name,
                            "type": "requires_training",
                            "description": f"{s_strat.name} requires {t_strat.name} to be completed first"
                        })
        
        return dependencies
    
    def generate_decision_brief(self) -> str:
        """Generate executive decision brief."""
        plan = self.optimize_all_horizons()
        
        lines = [
            "=" * 70,
            "📅 MULTI-HORIZON DECISION BRIEF",
            "=" * 70,
            "",
            f"Risk Score: {self.risk_score}/100 | Budget: ${self.total_budget:,.0f}",
            "",
            "─" * 70,
            f"⚡ IMMEDIATE ACTIONS (0-30 days) - {plan.immediate_plan.decision_deadline}",
            "─" * 70,
        ]
        
        for item in plan.immediate_plan.action_items:
            lines.append(f"   {item}")
        lines.append(f"   Cost: ${plan.immediate_plan.total_cost:,.0f} | "
                    f"Risk↓: {plan.immediate_plan.risk_reduction:.0f}%")
        
        lines.extend([
            "",
            "─" * 70,
            f"📋 TACTICAL PLAN (30-180 days) - {plan.tactical_plan.decision_deadline}",
            "─" * 70,
        ])
        
        for item in plan.tactical_plan.action_items:
            lines.append(f"   {item}")
        lines.append(f"   Cost: ${plan.tactical_plan.total_cost:,.0f} | "
                    f"Risk↓: {plan.tactical_plan.risk_reduction:.0f}%")
        
        lines.extend([
            "",
            "─" * 70,
            f"🎯 STRATEGIC INVESTMENT (180+ days) - {plan.strategic_plan.decision_deadline}",
            "─" * 70,
        ])
        
        for item in plan.strategic_plan.action_items:
            lines.append(f"   {item}")
        lines.append(f"   Cost: ${plan.strategic_plan.total_cost:,.0f} | "
                    f"Risk↓: {plan.strategic_plan.risk_reduction:.0f}%")
        
        lines.extend([
            "",
            "=" * 70,
            f"📊 TOTAL: ${plan.total_cost:,.0f} → {plan.total_risk_reduction:.0f}% risk reduction",
            "",
            f"💡 {plan.immediate_vs_sustainable_tradeoff.get('recommendation', '')}",
            "=" * 70,
        ])
        
        return "\n".join(lines)


# ============================================
# EXAMPLE USAGE
# ============================================

if __name__ == "__main__":
    # Sample strategies across horizons
    strategies = [
        # Immediate (quick wins)
        Strategy(
            id="PROC_001", name="Emergency Inspection Protocol",
            category=StrategyCategory.PROCESS,
            risk_reduction_pct=8.0, cost_estimate=15000, time_estimate=7
        ),
        Strategy(
            id="POLICY_001", name="Updated Weather Minimums",
            category=StrategyCategory.POLICY,
            risk_reduction_pct=5.0, cost_estimate=5000, time_estimate=3
        ),
        # Tactical
        Strategy(
            id="TRAIN_001", name="Crew Fatigue Training",
            category=StrategyCategory.TRAINING,
            risk_reduction_pct=12.0, cost_estimate=45000, time_estimate=45
        ),
        Strategy(
            id="MAINT_001", name="Enhanced Maintenance Protocol",
            category=StrategyCategory.MAINTENANCE,
            risk_reduction_pct=18.0, cost_estimate=120000, time_estimate=60
        ),
        # Strategic
        Strategy(
            id="TECH_001", name="Predictive Maintenance AI System",
            category=StrategyCategory.TECHNOLOGY,
            risk_reduction_pct=25.0, cost_estimate=350000, time_estimate=180
        ),
        Strategy(
            id="TECH_002", name="Safety Management Platform",
            category=StrategyCategory.TECHNOLOGY,
            risk_reduction_pct=15.0, cost_estimate=200000, time_estimate=120
        ),
    ]
    
    # Initialize optimizer
    optimizer = MultiHorizonOptimizer(
        strategies=strategies,
        total_budget=500000,
        risk_score=72
    )
    
    # Generate decision brief
    print(optimizer.generate_decision_brief())
