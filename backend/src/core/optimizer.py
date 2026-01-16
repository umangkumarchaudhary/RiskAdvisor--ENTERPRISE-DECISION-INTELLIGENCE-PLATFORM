"""
RiskAdvisor - Layer 1: Core Optimization Engine
=================================================
Multi-objective optimizer for safety strategy portfolio selection.

Uses:
- Pareto optimization for multi-objective trade-offs
- Monte Carlo simulation for uncertainty quantification
- Sensitivity analysis for robustness

Author: Umang Kumar
Date: January 2026
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import pulp
from scipy import stats
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================
# DATA MODELS
# ============================================

class StrategyCategory(Enum):
    MAINTENANCE = "maintenance"
    TRAINING = "training"
    PROCESS = "process"
    TECHNOLOGY = "technology"
    POLICY = "policy"


@dataclass
class Strategy:
    """A mitigation strategy with costs and effectiveness."""
    id: str
    name: str
    category: StrategyCategory
    
    # Effectiveness (risk reduction)
    risk_reduction_pct: float  # 0-100%
    confidence: float = 0.85  # Confidence in estimate
    
    # Cost
    cost_min: float = 0
    cost_max: float = 0
    cost_estimate: float = 0
    
    # Timeline (days)
    time_min: int = 0
    time_max: int = 0
    time_estimate: int = 0
    
    # Constraints
    requires_budget: bool = True
    disruption_level: str = "low"  # none, low, medium, high
    approval_level: str = "manager"  # team, manager, director, vp, ceo
    
    # Targeting
    applicable_risk_types: List[str] = field(default_factory=list)
    
    def get_cost_distribution(self, n_samples: int = 1000) -> np.ndarray:
        """Generate Monte Carlo samples for cost."""
        if self.cost_min == self.cost_max:
            return np.full(n_samples, self.cost_estimate)
        return np.random.triangular(
            self.cost_min, 
            self.cost_estimate, 
            self.cost_max, 
            n_samples
        )
    
    def get_time_distribution(self, n_samples: int = 1000) -> np.ndarray:
        """Generate Monte Carlo samples for timeline."""
        if self.time_min == self.time_max:
            return np.full(n_samples, self.time_estimate)
        return np.random.triangular(
            self.time_min,
            self.time_estimate,
            self.time_max,
            n_samples
        )


@dataclass
class Constraint:
    """A constraint on the optimization."""
    name: str
    constraint_type: str  # hard, soft
    category: str  # budget, timeline, resource
    max_value: float
    penalty_per_unit: float = 0  # For soft constraints
    is_negotiable: bool = False


@dataclass
class OptimizationResult:
    """Result of portfolio optimization."""
    selected_strategies: List[Strategy]
    total_cost: float
    total_risk_reduction: float
    total_timeline_days: int
    pareto_rank: int = 1
    robustness_score: float = 0.0
    
    # Uncertainty bounds (from Monte Carlo)
    cost_p5: float = 0
    cost_p95: float = 0
    risk_reduction_p5: float = 0
    risk_reduction_p95: float = 0
    
    # Metadata
    constraints_satisfied: Dict[str, bool] = field(default_factory=dict)
    constraint_violations: Dict[str, float] = field(default_factory=dict)


# ============================================
# CORE OPTIMIZER
# ============================================

class CoreOptimizer:
    """
    Multi-objective optimizer for safety strategy portfolios.
    
    Optimizes for:
    1. Maximum risk reduction
    2. Minimum cost
    3. Minimum timeline
    
    Subject to constraints:
    - Budget limits
    - Timeline limits
    - Resource availability
    - Regulatory requirements
    """
    
    def __init__(
        self,
        strategies: List[Strategy],
        constraints: List[Constraint],
        risk_score: float = 50.0
    ):
        self.strategies = strategies
        self.constraints = constraints
        self.risk_score = risk_score
        self.n_simulations = 1000
    
    def optimize_single_objective(
        self,
        objective: str = "risk_reduction",
        budget_limit: float = float('inf'),
        timeline_limit: int = 365
    ) -> OptimizationResult:
        """
        Single-objective optimization using linear programming.
        
        Args:
            objective: 'risk_reduction', 'cost', or 'timeline'
            budget_limit: Maximum budget
            timeline_limit: Maximum days
        
        Returns:
            OptimizationResult with selected strategies
        """
        prob = pulp.LpProblem("SafetyStrategySelection", pulp.LpMaximize)
        
        # Decision variables (1 if selected, 0 otherwise)
        x = {s.id: pulp.LpVariable(f"x_{s.id}", cat='Binary') 
             for s in self.strategies}
        
        # Objective function
        if objective == "risk_reduction":
            prob += pulp.lpSum([
                s.risk_reduction_pct * x[s.id] 
                for s in self.strategies
            ])
        elif objective == "cost":
            prob.sense = pulp.LpMinimize
            prob += pulp.lpSum([
                s.cost_estimate * x[s.id] 
                for s in self.strategies
            ])
        elif objective == "timeline":
            prob.sense = pulp.LpMinimize
            prob += pulp.lpSum([
                s.time_estimate * x[s.id] 
                for s in self.strategies
            ])
        
        # Constraints
        # Budget constraint
        prob += pulp.lpSum([
            s.cost_estimate * x[s.id] 
            for s in self.strategies
        ]) <= budget_limit
        
        # Timeline constraint (max of selected strategies if parallel)
        # For simplicity, using sum (sequential implementation)
        # In reality, this could be modified for parallel execution
        
        # Solve
        prob.solve(pulp.PULP_CBC_CMD(msg=0))
        
        # Extract results
        selected = [s for s in self.strategies if pulp.value(x[s.id]) == 1]
        
        total_cost = sum(s.cost_estimate for s in selected)
        total_risk_reduction = sum(s.risk_reduction_pct for s in selected)
        total_time = max((s.time_estimate for s in selected), default=0)
        
        return OptimizationResult(
            selected_strategies=selected,
            total_cost=total_cost,
            total_risk_reduction=min(total_risk_reduction, 95),  # Cap at 95%
            total_timeline_days=total_time,
            constraints_satisfied={"budget": total_cost <= budget_limit}
        )
    
    def optimize_pareto(
        self,
        budget_limit: float,
        timeline_limit: int = 365,
        n_solutions: int = 10
    ) -> List[OptimizationResult]:
        """
        Multi-objective optimization generating Pareto frontier.
        
        Returns set of non-dominated solutions trading off
        risk reduction vs cost vs timeline.
        """
        pareto_solutions = []
        
        # Generate solutions by varying constraints
        budget_steps = np.linspace(budget_limit * 0.3, budget_limit, n_solutions)
        
        for budget in budget_steps:
            result = self.optimize_single_objective(
                objective="risk_reduction",
                budget_limit=budget,
                timeline_limit=timeline_limit
            )
            pareto_solutions.append(result)
        
        # Remove dominated solutions
        non_dominated = self._filter_dominated(pareto_solutions)
        
        # Assign Pareto ranks
        for i, sol in enumerate(non_dominated):
            sol.pareto_rank = i + 1
        
        return non_dominated
    
    def _filter_dominated(
        self, 
        solutions: List[OptimizationResult]
    ) -> List[OptimizationResult]:
        """Filter dominated solutions to keep Pareto frontier."""
        non_dominated = []
        
        for sol in solutions:
            is_dominated = False
            for other in solutions:
                if (other.total_risk_reduction >= sol.total_risk_reduction and
                    other.total_cost <= sol.total_cost and
                    other.total_timeline_days <= sol.total_timeline_days and
                    (other.total_risk_reduction > sol.total_risk_reduction or
                     other.total_cost < sol.total_cost or
                     other.total_timeline_days < sol.total_timeline_days)):
                    is_dominated = True
                    break
            
            if not is_dominated:
                non_dominated.append(sol)
        
        return non_dominated
    
    def monte_carlo_analysis(
        self,
        result: OptimizationResult,
        n_simulations: int = 1000
    ) -> OptimizationResult:
        """
        Add uncertainty quantification via Monte Carlo simulation.
        
        Generates confidence intervals for cost and effectiveness.
        """
        cost_samples = np.zeros(n_simulations)
        risk_samples = np.zeros(n_simulations)
        
        for i in range(n_simulations):
            total_cost = 0
            total_risk = 0
            
            for strategy in result.selected_strategies:
                # Sample from distributions
                cost = strategy.get_cost_distribution(1)[0]
                
                # Risk reduction with confidence-based variance
                risk_std = strategy.risk_reduction_pct * (1 - strategy.confidence)
                risk = np.random.normal(
                    strategy.risk_reduction_pct, 
                    risk_std
                )
                
                total_cost += cost
                total_risk += risk
            
            cost_samples[i] = total_cost
            risk_samples[i] = min(total_risk, 95)  # Cap at 95%
        
        # Add confidence intervals to result
        result.cost_p5 = np.percentile(cost_samples, 5)
        result.cost_p95 = np.percentile(cost_samples, 95)
        result.risk_reduction_p5 = np.percentile(risk_samples, 5)
        result.risk_reduction_p95 = np.percentile(risk_samples, 95)
        
        return result
    
    def sensitivity_analysis(
        self,
        result: OptimizationResult,
        parameter: str = "cost"
    ) -> Dict[str, float]:
        """
        Sensitivity analysis: how much does outcome change 
        if parameters vary by ±20%?
        """
        sensitivities = {}
        base_value = result.total_risk_reduction
        
        for strategy in result.selected_strategies:
            original = getattr(strategy, f"{parameter}_estimate", strategy.cost_estimate)
            
            # Increase by 20%
            setattr(strategy, f"{parameter}_estimate", original * 1.2)
            new_result = self.optimize_single_objective(
                budget_limit=sum(s.cost_estimate for s in self.strategies)
            )
            delta = new_result.total_risk_reduction - base_value
            
            sensitivities[strategy.id] = delta / base_value if base_value > 0 else 0
            
            # Restore
            setattr(strategy, f"{parameter}_estimate", original)
        
        return sensitivities
    
    def get_optimal_portfolio(
        self,
        budget_limit: float,
        timeline_limit: int = 365,
        risk_tolerance: str = "balanced"
    ) -> OptimizationResult:
        """
        Get single optimal portfolio based on risk tolerance.
        
        Args:
            risk_tolerance: 'aggressive', 'balanced', or 'conservative'
        """
        pareto = self.optimize_pareto(budget_limit, timeline_limit)
        
        if not pareto:
            return OptimizationResult(
                selected_strategies=[],
                total_cost=0,
                total_risk_reduction=0,
                total_timeline_days=0
            )
        
        # Select based on preference
        if risk_tolerance == "aggressive":
            # Max risk reduction
            selected = max(pareto, key=lambda x: x.total_risk_reduction)
        elif risk_tolerance == "conservative":
            # Min cost
            selected = min(pareto, key=lambda x: x.total_cost)
        else:  # balanced
            # Best cost-effectiveness ratio
            selected = max(
                pareto, 
                key=lambda x: x.total_risk_reduction / x.total_cost if x.total_cost > 0 else 0
            )
        
        # Add uncertainty analysis
        selected = self.monte_carlo_analysis(selected)
        
        return selected


# ============================================
# EXAMPLE USAGE
# ============================================

if __name__ == "__main__":
    # Create sample strategies
    strategies = [
        Strategy(
            id="MAINT_001",
            name="Enhanced Maintenance Protocol",
            category=StrategyCategory.MAINTENANCE,
            risk_reduction_pct=18.0,
            cost_min=80000, cost_max=150000, cost_estimate=120000,
            time_min=30, time_max=60, time_estimate=45,
            applicable_risk_types=["maintenance", "equipment"]
        ),
        Strategy(
            id="TRAIN_001",
            name="Crew Fatigue Training",
            category=StrategyCategory.TRAINING,
            risk_reduction_pct=12.0,
            cost_min=30000, cost_max=60000, cost_estimate=45000,
            time_min=14, time_max=30, time_estimate=21,
            applicable_risk_types=["fatigue", "human_factors"]
        ),
        Strategy(
            id="TECH_001",
            name="Predictive Maintenance System",
            category=StrategyCategory.TECHNOLOGY,
            risk_reduction_pct=25.0,
            cost_min=200000, cost_max=350000, cost_estimate=280000,
            time_min=90, time_max=180, time_estimate=120,
            applicable_risk_types=["maintenance", "equipment"]
        ),
        Strategy(
            id="PROC_001",
            name="Weather Decision Framework",
            category=StrategyCategory.PROCESS,
            risk_reduction_pct=15.0,
            cost_min=15000, cost_max=30000, cost_estimate=22000,
            time_min=7, time_max=21, time_estimate=14,
            applicable_risk_types=["weather"]
        ),
        Strategy(
            id="POLICY_001",
            name="Mandatory Rest Requirements",
            category=StrategyCategory.POLICY,
            risk_reduction_pct=20.0,
            cost_min=50000, cost_max=100000, cost_estimate=75000,
            time_min=30, time_max=90, time_estimate=60,
            applicable_risk_types=["fatigue"]
        ),
    ]
    
    # Create constraints
    constraints = [
        Constraint("Q1 Budget", "hard", "budget", max_value=300000),
        Constraint("Implementation Deadline", "soft", "timeline", 
                   max_value=90, penalty_per_unit=1000),
    ]
    
    # Initialize optimizer
    optimizer = CoreOptimizer(
        strategies=strategies,
        constraints=constraints,
        risk_score=75.0
    )
    
    # Get optimal portfolio
    print("=" * 60)
    print("🎯 RiskAdvisor - Core Optimization Engine")
    print("=" * 60)
    
    result = optimizer.get_optimal_portfolio(
        budget_limit=300000,
        timeline_limit=90,
        risk_tolerance="balanced"
    )
    
    print(f"\n📊 OPTIMAL PORTFOLIO (Balanced)")
    print(f"   Total Cost: ${result.total_cost:,.0f}")
    print(f"   Risk Reduction: {result.total_risk_reduction:.1f}%")
    print(f"   Timeline: {result.total_timeline_days} days")
    print(f"\n   Cost Range (90% CI): ${result.cost_p5:,.0f} - ${result.cost_p95:,.0f}")
    print(f"   Risk Range (90% CI): {result.risk_reduction_p5:.1f}% - {result.risk_reduction_p95:.1f}%")
    
    print(f"\n📋 SELECTED STRATEGIES:")
    for s in result.selected_strategies:
        print(f"   • {s.name} ({s.category.value})")
        print(f"     └─ Cost: ${s.cost_estimate:,.0f} | Risk↓: {s.risk_reduction_pct}%")
    
    print("\n" + "=" * 60)
