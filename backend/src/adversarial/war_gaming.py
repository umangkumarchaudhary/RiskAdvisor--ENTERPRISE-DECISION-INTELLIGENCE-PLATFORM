"""
RiskAdvisor - Layer 4: Adversarial Validation (War Gaming)
==========================================================
Stress tests recommendations against worst-case scenarios.

Key Features:
- Red Team: Attacks recommendations to find weaknesses
- Blue Team: Defends with optimal strategy
- Purple Team: Synthesizes robust recommendations
- Robustness scoring

Author: Umang Kumar
Date: January 2026
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import numpy as np
import logging
from copy import deepcopy

from src.core.optimizer import Strategy, OptimizationResult, CoreOptimizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================
# DATA MODELS
# ============================================

class AttackType(Enum):
    COST_OVERRUN = "cost_overrun"
    TIMELINE_DELAY = "timeline_delay"
    STRATEGY_FAILURE = "strategy_failure"
    BUDGET_CUT = "budget_cut"
    KEY_PERSON_LEAVES = "key_person_leaves"
    NEW_RISK_EMERGES = "new_risk_emerges"
    VENDOR_DELAY = "vendor_delay"
    REGULATORY_CHANGE = "regulatory_change"


@dataclass
class Attack:
    """A red team attack scenario."""
    attack_type: AttackType
    description: str
    severity: str  # low, medium, high
    probability: float  # Likelihood of occurring (0-1)
    
    # Attack parameters
    affected_strategies: List[str] = field(default_factory=list)
    impact_multiplier: float = 1.0  # e.g., 1.5 = 50% worse
    impact_absolute: float = 0  # Fixed impact amount


@dataclass
class AttackResult:
    """Result of applying an attack."""
    attack: Attack
    original_outcome: Dict
    degraded_outcome: Dict
    damage: Dict  # What was lost
    
    # Resilience metrics
    outcome_degradation_pct: float  # How much worse
    still_viable: bool  # Can we still achieve objectives?
    recovery_options: List[str] = field(default_factory=list)


@dataclass
class RobustnessAssessment:
    """Overall robustness of a portfolio."""
    portfolio: OptimizationResult
    
    # Scores
    robustness_score: float  # 0-100
    resilience_rating: str  # A, B, C, D, F
    
    # Attack results
    attack_results: List[AttackResult] = field(default_factory=list)
    
    # Worst case
    worst_case_outcome: Dict = field(default_factory=dict)
    worst_case_description: str = ""
    
    # Best actions
    backup_plan: Optional[OptimizationResult] = None
    recommendations: List[str] = field(default_factory=list)


# ============================================
# RED TEAM (Attacker)
# ============================================

class RedTeam:
    """
    Generates attack scenarios to stress test recommendations.
    """
    
    def __init__(self):
        self.attack_library = self._build_attack_library()
    
    def _build_attack_library(self) -> List[Attack]:
        """Standard attack scenarios."""
        return [
            Attack(
                attack_type=AttackType.COST_OVERRUN,
                description="Costs are 50% higher than estimated",
                severity="high",
                probability=0.25,
                impact_multiplier=1.5
            ),
            Attack(
                attack_type=AttackType.TIMELINE_DELAY,
                description="Implementation takes 2x longer",
                severity="medium",
                probability=0.35,
                impact_multiplier=2.0
            ),
            Attack(
                attack_type=AttackType.STRATEGY_FAILURE,
                description="Top strategy fails completely",
                severity="high",
                probability=0.15,
                impact_multiplier=0  # Zero effectiveness
            ),
            Attack(
                attack_type=AttackType.BUDGET_CUT,
                description="Budget reduced by 40% mid-implementation",
                severity="high",
                probability=0.20,
                impact_absolute=-0.40  # 40% budget cut
            ),
            Attack(
                attack_type=AttackType.KEY_PERSON_LEAVES,
                description="Project lead leaves mid-implementation",
                severity="medium",
                probability=0.15,
                impact_multiplier=1.3  # 30% cost increase, delays
            ),
            Attack(
                attack_type=AttackType.NEW_RISK_EMERGES,
                description="New critical risk discovered during implementation",
                severity="medium",
                probability=0.20,
                impact_absolute=0.15  # 15% additional risk to address
            ),
            Attack(
                attack_type=AttackType.VENDOR_DELAY,
                description="Key vendor delays equipment by 60 days",
                severity="medium",
                probability=0.30,
                impact_absolute=60  # Days
            ),
            Attack(
                attack_type=AttackType.REGULATORY_CHANGE,
                description="New FAA requirement adds compliance work",
                severity="low",
                probability=0.10,
                impact_absolute=50000  # Additional cost
            ),
        ]
    
    def generate_attacks(
        self,
        portfolio: OptimizationResult,
        severity_threshold: str = "low"
    ) -> List[Attack]:
        """Generate relevant attacks for a portfolio."""
        severity_order = {"low": 0, "medium": 1, "high": 2}
        threshold = severity_order.get(severity_threshold, 0)
        
        attacks = []
        
        for attack_template in self.attack_library:
            if severity_order.get(attack_template.severity, 0) >= threshold:
                # Customize attack for this portfolio
                attack = deepcopy(attack_template)
                
                # For strategy failure, target top strategy
                if attack.attack_type == AttackType.STRATEGY_FAILURE:
                    if portfolio.selected_strategies:
                        top_strategy = max(
                            portfolio.selected_strategies,
                            key=lambda s: s.risk_reduction_pct
                        )
                        attack.affected_strategies = [top_strategy.id]
                        attack.description = f"Strategy '{top_strategy.name}' fails completely"
                
                attacks.append(attack)
        
        return attacks
    
    def apply_attack(
        self,
        portfolio: OptimizationResult,
        attack: Attack
    ) -> AttackResult:
        """Apply an attack and measure damage."""
        original = {
            "cost": portfolio.total_cost,
            "risk_reduction": portfolio.total_risk_reduction,
            "timeline": portfolio.total_timeline_days,
            "strategies": len(portfolio.selected_strategies)
        }
        
        degraded = deepcopy(original)
        damage = {}
        recovery = []
        
        if attack.attack_type == AttackType.COST_OVERRUN:
            degraded["cost"] = original["cost"] * attack.impact_multiplier
            damage["cost_increase"] = degraded["cost"] - original["cost"]
            recovery.append("Request emergency budget allocation")
            recovery.append("Reduce scope to high-priority items")
        
        elif attack.attack_type == AttackType.TIMELINE_DELAY:
            degraded["timeline"] = int(original["timeline"] * attack.impact_multiplier)
            damage["timeline_increase"] = degraded["timeline"] - original["timeline"]
            recovery.append("Add resources to accelerate")
            recovery.append("Parallel execution where possible")
        
        elif attack.attack_type == AttackType.STRATEGY_FAILURE:
            # Remove failed strategy's contribution
            failed_strategies = [
                s for s in portfolio.selected_strategies
                if s.id in attack.affected_strategies
            ]
            failed_reduction = sum(s.risk_reduction_pct for s in failed_strategies)
            degraded["risk_reduction"] = max(0, original["risk_reduction"] - failed_reduction)
            degraded["strategies"] = original["strategies"] - len(failed_strategies)
            damage["risk_reduction_lost"] = failed_reduction
            recovery.append("Activate backup strategy from same category")
            recovery.append("Reallocate budget to remaining strategies")
        
        elif attack.attack_type == AttackType.BUDGET_CUT:
            cut_amount = original["cost"] * abs(attack.impact_absolute)
            degraded["cost"] = original["cost"] - cut_amount
            # Proportionally reduce effectiveness
            degraded["risk_reduction"] = original["risk_reduction"] * (1 - abs(attack.impact_absolute))
            damage["budget_cut"] = cut_amount
            recovery.append("Prioritize must-have strategies")
            recovery.append("Defer nice-to-have to next quarter")
        
        elif attack.attack_type == AttackType.KEY_PERSON_LEAVES:
            degraded["cost"] = original["cost"] * attack.impact_multiplier
            degraded["timeline"] = int(original["timeline"] * 1.2)
            damage["cost_increase"] = degraded["cost"] - original["cost"]
            damage["timeline_increase"] = degraded["timeline"] - original["timeline"]
            recovery.append("Cross-train backup lead immediately")
            recovery.append("Document critical knowledge")
        
        elif attack.attack_type == AttackType.NEW_RISK_EMERGES:
            # Need to address additional risk
            degraded["risk_reduction"] = original["risk_reduction"] - (attack.impact_absolute * 100)
            damage["additional_risk"] = attack.impact_absolute * 100
            recovery.append("Add emergency mitigation strategy")
            recovery.append("Reallocate resources from lower-priority items")
        
        # Calculate degradation
        risk_degradation = 0
        if original["risk_reduction"] > 0:
            risk_degradation = (
                (original["risk_reduction"] - degraded["risk_reduction"]) 
                / original["risk_reduction"]
            ) * 100
        
        # Still viable if we achieve at least 50% of intended risk reduction
        still_viable = degraded["risk_reduction"] >= (original["risk_reduction"] * 0.5)
        
        return AttackResult(
            attack=attack,
            original_outcome=original,
            degraded_outcome=degraded,
            damage=damage,
            outcome_degradation_pct=risk_degradation,
            still_viable=still_viable,
            recovery_options=recovery
        )


# ============================================
# BLUE TEAM (Defender)
# ============================================

class BlueTeam:
    """
    Optimizes defensive strategies and backup plans.
    """
    
    def __init__(self, strategies: List[Strategy]):
        self.strategies = strategies
    
    def generate_backup_plan(
        self,
        original_portfolio: OptimizationResult,
        attack_results: List[AttackResult],
        reduced_budget: float
    ) -> OptimizationResult:
        """Generate a backup plan that works even in degraded conditions."""
        # Identify strategies that didn't fail in attacks
        failed_strategy_ids = set()
        for result in attack_results:
            if result.attack.attack_type == AttackType.STRATEGY_FAILURE:
                failed_strategy_ids.update(result.attack.affected_strategies)
        
        # Available strategies (excluding failed ones)
        available = [
            s for s in self.strategies 
            if s.id not in failed_strategy_ids
        ]
        
        # Optimize with reduced budget
        optimizer = CoreOptimizer(available, [])
        backup = optimizer.get_optimal_portfolio(
            budget_limit=reduced_budget,
            risk_tolerance="conservative"
        )
        
        return backup


# ============================================
# PURPLE TEAM (Synthesizer)
# ============================================

class PurpleTeam:
    """
    Synthesizes insights from Red and Blue teams.
    Generates robust recommendations.
    """
    
    def __init__(self, strategies: List[Strategy]):
        self.strategies = strategies
        self.red_team = RedTeam()
        self.blue_team = BlueTeam(strategies)
    
    def assess_robustness(
        self,
        portfolio: OptimizationResult,
        available_budget: float
    ) -> RobustnessAssessment:
        """
        Complete robustness assessment of a portfolio.
        """
        # Generate and apply attacks
        attacks = self.red_team.generate_attacks(portfolio, severity_threshold="low")
        attack_results = []
        
        for attack in attacks:
            result = self.red_team.apply_attack(portfolio, attack)
            attack_results.append(result)
        
        # Calculate robustness score
        total_degradation = sum(r.outcome_degradation_pct for r in attack_results)
        avg_degradation = total_degradation / len(attack_results) if attack_results else 0
        viability_rate = sum(1 for r in attack_results if r.still_viable) / len(attack_results) if attack_results else 1
        
        # Robustness score: 100 - avg_degradation, weighted by viability
        robustness_score = max(0, min(100, (100 - avg_degradation) * viability_rate))
        
        # Rating
        if robustness_score >= 85:
            rating = "A"
        elif robustness_score >= 70:
            rating = "B"
        elif robustness_score >= 55:
            rating = "C"
        elif robustness_score >= 40:
            rating = "D"
        else:
            rating = "F"
        
        # Find worst case
        worst_result = max(attack_results, key=lambda r: r.outcome_degradation_pct) if attack_results else None
        
        # Generate backup plan
        backup = self.blue_team.generate_backup_plan(
            portfolio,
            attack_results,
            available_budget * 0.6  # Assume 40% budget cut worst case
        )
        
        # Recommendations
        recommendations = self._generate_recommendations(attack_results, robustness_score)
        
        return RobustnessAssessment(
            portfolio=portfolio,
            robustness_score=robustness_score,
            resilience_rating=rating,
            attack_results=attack_results,
            worst_case_outcome=worst_result.degraded_outcome if worst_result else {},
            worst_case_description=worst_result.attack.description if worst_result else "",
            backup_plan=backup,
            recommendations=recommendations
        )
    
    def _generate_recommendations(
        self,
        attack_results: List[AttackResult],
        robustness_score: float
    ) -> List[str]:
        """Generate recommendations based on attack results."""
        recs = []
        
        # Find most damaging attacks
        high_damage = [r for r in attack_results if r.outcome_degradation_pct > 20]
        
        for result in high_damage:
            if result.attack.attack_type == AttackType.COST_OVERRUN:
                recs.append("Include 20% contingency buffer in budget")
            elif result.attack.attack_type == AttackType.STRATEGY_FAILURE:
                recs.append("Identify backup strategies for critical items")
            elif result.attack.attack_type == AttackType.BUDGET_CUT:
                recs.append("Pre-secure multi-quarter funding commitment")
            elif result.attack.attack_type == AttackType.KEY_PERSON_LEAVES:
                recs.append("Document knowledge and cross-train team members")
        
        if robustness_score < 60:
            recs.append("Consider diversifying portfolio across more strategies")
            recs.append("Prioritize strategies with higher confidence levels")
        
        return list(set(recs))  # Remove duplicates
    
    def generate_report(
        self,
        assessment: RobustnessAssessment
    ) -> str:
        """Generate war gaming report."""
        lines = [
            "=" * 70,
            "⚔️  ADVERSARIAL VALIDATION REPORT (War Gaming Results)",
            "=" * 70,
            "",
            f"📊 ROBUSTNESS SCORE: {assessment.robustness_score:.0f}/100 (Grade: {assessment.resilience_rating})",
            "",
            "🔴 RED TEAM ATTACKS:",
        ]
        
        for result in assessment.attack_results:
            status = "✅ Survived" if result.still_viable else "❌ Failed"
            lines.append(f"   • {result.attack.description}")
            lines.append(f"     └─ Degradation: {result.outcome_degradation_pct:.0f}% | {status}")
        
        lines.append("")
        lines.append("📉 WORST CASE SCENARIO:")
        lines.append(f"   {assessment.worst_case_description}")
        lines.append(f"   └─ Risk Reduction: {assessment.worst_case_outcome.get('risk_reduction', 0):.1f}%")
        lines.append(f"   └─ Still achieves {assessment.worst_case_outcome.get('risk_reduction', 0) / max(assessment.portfolio.total_risk_reduction, 1) * 100:.0f}% of original goal")
        
        lines.append("")
        lines.append("🛡️ BACKUP PLAN (if worst case occurs):")
        if assessment.backup_plan:
            lines.append(f"   Cost: ${assessment.backup_plan.total_cost:,.0f}")
            lines.append(f"   Risk Reduction: {assessment.backup_plan.total_risk_reduction:.1f}%")
            lines.append(f"   Strategies: {len(assessment.backup_plan.selected_strategies)}")
        
        lines.append("")
        lines.append("💡 RECOMMENDATIONS:")
        for rec in assessment.recommendations:
            lines.append(f"   • {rec}")
        
        lines.append("")
        lines.append("=" * 70)
        
        return "\n".join(lines)


# ============================================
# EXAMPLE USAGE
# ============================================

if __name__ == "__main__":
    from src.core.optimizer import Strategy, StrategyCategory, CoreOptimizer
    
    # Sample strategies
    strategies = [
        Strategy(
            id="MAINT_001", name="Enhanced Maintenance",
            category=StrategyCategory.MAINTENANCE,
            risk_reduction_pct=18.0, cost_estimate=120000, time_estimate=45
        ),
        Strategy(
            id="TRAIN_001", name="Fatigue Training",
            category=StrategyCategory.TRAINING,
            risk_reduction_pct=12.0, cost_estimate=45000, time_estimate=21
        ),
        Strategy(
            id="TECH_001", name="Predictive Maintenance System",
            category=StrategyCategory.TECHNOLOGY,
            risk_reduction_pct=25.0, cost_estimate=280000, time_estimate=120
        ),
        Strategy(
            id="PROC_001", name="Weather Framework",
            category=StrategyCategory.PROCESS,
            risk_reduction_pct=15.0, cost_estimate=22000, time_estimate=14
        ),
    ]
    
    # Get optimal portfolio
    optimizer = CoreOptimizer(strategies, [])
    portfolio = optimizer.get_optimal_portfolio(
        budget_limit=400000,
        risk_tolerance="balanced"
    )
    
    # Run war gaming
    purple_team = PurpleTeam(strategies)
    assessment = purple_team.assess_robustness(portfolio, available_budget=400000)
    
    print(purple_team.generate_report(assessment))
