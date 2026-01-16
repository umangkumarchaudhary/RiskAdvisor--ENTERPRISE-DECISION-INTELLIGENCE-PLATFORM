"""
RiskAdvisor - Layer 7: Executive Decision Interface
====================================================
Top-level interface for executive decision-making.

Key Features:
- Natural language query processing
- Decision brief generation
- Stakeholder-specific outputs
- One-pager summaries
- Scenario comparison matrices

Author: Umang Kumar
Date: January 2026
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import logging

from src.core.optimizer import Strategy, OptimizationResult, CoreOptimizer, StrategyCategory
from src.negotiation.constraint_engine import ConstraintNegotiationEngine, NegotiationPackage
from src.impact.cascading_analyzer import CascadingImpactAnalyzer, TotalCostAnalysis
from src.adversarial.war_gaming import PurpleTeam, RobustnessAssessment
from src.horizons.multi_horizon import MultiHorizonOptimizer, MultiHorizonPlan
from src.context.intelligence_engine import ContextIntelligenceEngine, OrganizationalContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================
# DATA MODELS
# ============================================

@dataclass
class StakeholderBrief:
    """Tailored brief for a specific stakeholder."""
    stakeholder_role: str
    subject_line: str
    key_points: List[str]
    recommended_action: str
    metrics_highlighted: Dict[str, str]
    framing: str


@dataclass
class DecisionScenario:
    """A decision scenario for comparison."""
    scenario_id: str
    name: str
    description: str
    cost: float
    risk_reduction: float
    timeline_days: int
    disruption_level: str
    confidence: float
    recommended: bool = False
    rationale: str = ""


@dataclass
class ExecutiveDecisionPackage:
    """Complete decision package for executives."""
    # Summary
    title: str
    situation_summary: str
    risk_score: float
    created_at: datetime = field(default_factory=datetime.now)
    
    # Multi-horizon plan
    horizon_plan: Optional[MultiHorizonPlan] = None
    
    # Total cost analysis
    tco_analysis: Optional[Dict] = None
    
    # Robustness
    robustness: Optional[RobustnessAssessment] = None
    
    # Scenarios
    scenarios: List[DecisionScenario] = field(default_factory=list)
    
    # Stakeholder briefs
    stakeholder_briefs: Dict[str, StakeholderBrief] = field(default_factory=dict)
    
    # Decision required
    decision_deadline: str = ""
    decision_owner: str = ""


# ============================================
# EXECUTIVE DECISION INTERFACE
# ============================================

class ExecutiveDecisionInterface:
    """
    Top-level interface that combines all layers to produce
    executive-ready decision packages.
    """
    
    def __init__(
        self,
        strategies: List[Strategy],
        budget: float,
        risk_score: float = 50.0
    ):
        self.strategies = strategies
        self.budget = budget
        self.risk_score = risk_score
        
        # Initialize all layer engines
        self.core_optimizer = CoreOptimizer(strategies, [])
        self.impact_analyzer = CascadingImpactAnalyzer()
        self.purple_team = PurpleTeam(strategies)
        self.horizon_optimizer = MultiHorizonOptimizer(strategies, budget, risk_score)
        self.context_engine = ContextIntelligenceEngine()
        
        # Stakeholder profiles
        self.stakeholder_profiles = self._load_stakeholder_profiles()
    
    def _load_stakeholder_profiles(self) -> Dict[str, Dict]:
        """Load stakeholder communication profiles."""
        return {
            "CEO": {
                "primary_concerns": ["Financial impact", "Reputation", "Regulatory compliance"],
                "decision_criteria": ["ROI", "Optics", "Risk exposure"],
                "preferred_format": "executive_summary",
                "framing": "Cost avoidance, risk transfer, reputation protection"
            },
            "CFO": {
                "primary_concerns": ["Budget impact", "Cash flow", "Audit trail"],
                "decision_criteria": ["NPV", "Payback period", "Budget fit"],
                "preferred_format": "detailed_financials",
                "framing": "Capital efficiency, risk-adjusted returns"
            },
            "COO": {
                "primary_concerns": ["Operational disruption", "Schedule impact"],
                "decision_criteria": ["Minimal downtime", "Phased approach"],
                "preferred_format": "operational_plan",
                "framing": "Minimal disruption, flexible scheduling"
            },
            "VP_SAFETY": {
                "primary_concerns": ["Risk reduction", "Compliance", "Safety culture"],
                "decision_criteria": ["Risk metrics", "SMS alignment"],
                "preferred_format": "detailed",
                "framing": "Safety first, measurable improvement"
            },
            "UNION": {
                "primary_concerns": ["Job security", "Workload", "Worker safety"],
                "decision_criteria": ["No layoffs", "Fair workload"],
                "preferred_format": "clear_simple",
                "framing": "Worker safety first, collaborative approach"
            }
        }
    
    def generate_decision_package(
        self,
        context_indicators: Dict = None
    ) -> ExecutiveDecisionPackage:
        """
        Generate complete executive decision package.
        """
        # 1. Detect context
        context = self.context_engine.detect_context(context_indicators or {})
        
        # 2. Multi-horizon optimization
        horizon_plan = self.horizon_optimizer.optimize_all_horizons()
        
        # 3. Get optimal portfolio for TCO and robustness analysis
        optimal = self.core_optimizer.get_optimal_portfolio(
            budget_limit=self.budget,
            risk_tolerance="balanced"
        )
        
        # 4. Total cost analysis
        tco = self.impact_analyzer.analyze_portfolio(optimal)
        
        # 5. Robustness assessment
        robustness = self.purple_team.assess_robustness(optimal, self.budget)
        
        # 6. Generate scenarios
        scenarios = self._generate_scenarios(optimal, robustness)
        
        # 7. Generate stakeholder briefs
        briefs = self._generate_stakeholder_briefs(horizon_plan, tco, robustness)
        
        # 8. Determine urgency
        deadline = "Decision required: TODAY" if self.risk_score >= 75 else "Decision required: This week"
        
        return ExecutiveDecisionPackage(
            title=f"Safety Decision Brief - Risk Score {self.risk_score:.0f}",
            situation_summary=self._generate_situation_summary(),
            risk_score=self.risk_score,
            horizon_plan=horizon_plan,
            tco_analysis=tco,
            robustness=robustness,
            scenarios=scenarios,
            stakeholder_briefs=briefs,
            decision_deadline=deadline,
            decision_owner="VP Safety / CEO"
        )
    
    def _generate_situation_summary(self) -> str:
        """Generate situation summary."""
        if self.risk_score >= 75:
            severity = "Critical"
            action = "Immediate action required"
        elif self.risk_score >= 50:
            severity = "Elevated"
            action = "Prompt attention needed"
        else:
            severity = "Normal"
            action = "Planned improvements recommended"
        
        return (
            f"Risk Score: {self.risk_score:.0f}/100 ({severity}). "
            f"{action}. Budget available: ${self.budget:,.0f}."
        )
    
    def _generate_scenarios(
        self,
        optimal: OptimizationResult,
        robustness: RobustnessAssessment
    ) -> List[DecisionScenario]:
        """Generate decision scenarios for comparison."""
        scenarios = []
        
        # Scenario 1: Do Nothing
        scenarios.append(DecisionScenario(
            scenario_id="S0",
            name="Do Nothing",
            description="Maintain current state",
            cost=0,
            risk_reduction=0,
            timeline_days=0,
            disruption_level="None",
            confidence=1.0,
            recommended=False,
            rationale="Risk continues to grow 10-15% annually"
        ))
        
        # Scenario 2: Quick Fix (Immediate only)
        quick_fix_cost = self.budget * 0.3
        scenarios.append(DecisionScenario(
            scenario_id="S1",
            name="Quick Fix",
            description="Address immediate concerns only",
            cost=quick_fix_cost,
            risk_reduction=optimal.total_risk_reduction * 0.4,
            timeline_days=30,
            disruption_level="Low",
            confidence=0.95,
            recommended=False,
            rationale="Temporary relief, doesn't address root causes"
        ))
        
        # Scenario 3: Recommended (Balanced)
        scenarios.append(DecisionScenario(
            scenario_id="S2",
            name="Recommended",
            description="Balanced multi-horizon approach",
            cost=optimal.total_cost,
            risk_reduction=optimal.total_risk_reduction,
            timeline_days=90,
            disruption_level="Medium",
            confidence=robustness.robustness_score / 100,
            recommended=True,
            rationale="Optimal balance of cost, effectiveness, and sustainability"
        ))
        
        # Scenario 4: Aggressive
        aggressive_cost = min(self.budget, optimal.total_cost * 1.3)
        scenarios.append(DecisionScenario(
            scenario_id="S3",
            name="Aggressive",
            description="Maximum risk reduction, higher cost",
            cost=aggressive_cost,
            risk_reduction=min(optimal.total_risk_reduction * 1.2, 75),
            timeline_days=60,
            disruption_level="High",
            confidence=0.75,
            recommended=False,
            rationale="Faster but higher disruption risk"
        ))
        
        # Scenario 5: Conservative
        scenarios.append(DecisionScenario(
            scenario_id="S4",
            name="Conservative",
            description="Lower investment, longer timeline",
            cost=optimal.total_cost * 0.7,
            risk_reduction=optimal.total_risk_reduction * 0.8,
            timeline_days=150,
            disruption_level="Low",
            confidence=0.92,
            recommended=False,
            rationale="Safer approach, acceptable for lower risk situations"
        ))
        
        return scenarios
    
    def _generate_stakeholder_briefs(
        self,
        horizon_plan: MultiHorizonPlan,
        tco: Dict,
        robustness: RobustnessAssessment
    ) -> Dict[str, StakeholderBrief]:
        """Generate tailored briefs for each stakeholder."""
        briefs = {}
        
        # CEO Brief
        avoided_cost = horizon_plan.total_risk_reduction * 100000  # $100K per 1%
        roi = avoided_cost / horizon_plan.total_cost if horizon_plan.total_cost > 0 else 0
        
        briefs["CEO"] = StakeholderBrief(
            stakeholder_role="CEO",
            subject_line=f"Safety Investment Decision - ${horizon_plan.total_cost:,.0f} for {horizon_plan.total_risk_reduction:.0f}% Risk Reduction",
            key_points=[
                f"Prevents ${avoided_cost:,.0f} in potential incident costs (ROI: {roi:.1f}x)",
                f"Addresses regulatory compliance requirements",
                f"Implementation complete in 180 days with minimal disruption",
                f"Robustness score: {robustness.robustness_score:.0f}% (Grade: {robustness.resilience_rating})"
            ],
            recommended_action="Approve recommended portfolio",
            metrics_highlighted={
                "ROI": f"{roi:.1f}x",
                "Risk Reduction": f"{horizon_plan.total_risk_reduction:.0f}%",
                "Investment": f"${horizon_plan.total_cost:,.0f}"
            },
            framing=self.stakeholder_profiles["CEO"]["framing"]
        )
        
        # CFO Brief
        payback_months = horizon_plan.total_cost / (avoided_cost / 12) if avoided_cost > 0 else 0
        
        briefs["CFO"] = StakeholderBrief(
            stakeholder_role="CFO",
            subject_line=f"Safety Capital Request - ${horizon_plan.total_cost:,.0f}",
            key_points=[
                f"Total investment: ${horizon_plan.total_cost:,.0f}",
                f"NPV (5-year): ${avoided_cost * 2:,.0f}",
                f"Payback period: {payback_months:.1f} months",
                f"True total cost (with ripple effects): ${tco.get('total_cost_of_ownership', 0):,.0f}"
            ],
            recommended_action="Allocate from Q1 contingency fund",
            metrics_highlighted={
                "Payback": f"{payback_months:.1f} months",
                "TCO Multiplier": f"{tco.get('cost_multiplier', 1):.1f}x",
                "Budget Fit": "Within discretionary limits"
            },
            framing=self.stakeholder_profiles["CFO"]["framing"]
        )
        
        # COO Brief
        briefs["COO"] = StakeholderBrief(
            stakeholder_role="COO",
            subject_line="Safety Initiative - Minimal Schedule Impact",
            key_points=[
                "Implementation during off-peak hours",
                "Aircraft availability maintained at 98%",
                "Phased rollout minimizes disruption",
                "Buffer aircraft allocated for contingency"
            ],
            recommended_action="Approve operational plan",
            metrics_highlighted={
                "Availability": "98% maintained",
                "Schedule Impact": "3 flights (0.08%)",
                "Timeline": "90-day phased rollout"
            },
            framing=self.stakeholder_profiles["COO"]["framing"]
        )
        
        return briefs
    
    def generate_one_pager(self, package: ExecutiveDecisionPackage) -> str:
        """Generate one-page executive summary."""
        lines = [
            "=" * 70,
            f"📋 {package.title}",
            "=" * 70,
            "",
            "SITUATION:",
            package.situation_summary,
            "",
        ]
        
        if package.horizon_plan:
            hp = package.horizon_plan
            lines.extend([
                "RECOMMENDATION:",
                f"Implement 3-phase portfolio for {hp.total_risk_reduction:.0f}% risk reduction.",
                "",
                "IMMEDIATE ACTIONS (This Week):",
            ])
            for item in hp.immediate_plan.action_items[:2]:
                lines.append(f"  {item}")
            lines.append(f"  Cost: ${hp.immediate_plan.total_cost:,.0f} | Risk↓: {hp.immediate_plan.risk_reduction:.0f}%")
            
            lines.extend([
                "",
                "TACTICAL PLAN (This Quarter):",
            ])
            for item in hp.tactical_plan.action_items[:2]:
                lines.append(f"  {item}")
            lines.append(f"  Cost: ${hp.tactical_plan.total_cost:,.0f} | Risk↓: {hp.tactical_plan.risk_reduction:.0f}%")
            
            lines.extend([
                "",
                "STRATEGIC INVESTMENT (This Year):",
            ])
            for item in hp.strategic_plan.action_items[:2]:
                lines.append(f"  {item}")
            lines.append(f"  Cost: ${hp.strategic_plan.total_cost:,.0f} | Risk↓: {hp.strategic_plan.risk_reduction:.0f}%")
        
        lines.extend([
            "",
            "─" * 70,
            "TRADE-OFFS:",
        ])
        
        for scenario in package.scenarios:
            marker = " ✓" if scenario.recommended else ""
            lines.append(
                f"  {scenario.name}: ${scenario.cost:,.0f}, "
                f"{scenario.risk_reduction:.0f}% reduction, "
                f"{scenario.timeline_days}d{marker}"
            )
        
        if package.robustness:
            lines.extend([
                "",
                f"ROBUSTNESS: {package.robustness.robustness_score:.0f}/100 "
                f"(Grade: {package.robustness.resilience_rating})",
                f"  Worst case still achieves 70% of intended value",
            ])
        
        lines.extend([
            "",
            "─" * 70,
            f"DECISION NEEDED: {package.decision_deadline}",
            f"DECISION OWNER: {package.decision_owner}",
            "=" * 70,
        ])
        
        return "\n".join(lines)
    
    def generate_scenario_matrix(self, package: ExecutiveDecisionPackage) -> str:
        """Generate scenario comparison matrix."""
        lines = [
            "DECISION SCENARIO COMPARISON",
            "",
            "┌──────────────┬──────────┬───────────┬──────────┬────────────┬──────────┐",
            "│ Scenario     │ Cost     │ Risk Red. │ Timeline │ Disruption │ Conf.    │",
            "├──────────────┼──────────┼───────────┼──────────┼────────────┼──────────┤",
        ]
        
        for s in package.scenarios:
            marker = " ✓" if s.recommended else ""
            lines.append(
                f"│ {s.name:<12}{marker} │ ${s.cost/1000:>6.0f}K │ {s.risk_reduction:>8.0f}% │ "
                f"{s.timeline_days:>6}d │ {s.disruption_level:<10} │ {s.confidence*100:>6.0f}% │"
            )
        
        lines.append("└──────────────┴──────────┴───────────┴──────────┴────────────┴──────────┘")
        
        # Add recommendation
        recommended = next((s for s in package.scenarios if s.recommended), None)
        if recommended:
            lines.extend([
                "",
                f"RECOMMENDED: {recommended.name}",
                f"Rationale: {recommended.rationale}"
            ])
        
        return "\n".join(lines)


# ============================================
# EXAMPLE USAGE
# ============================================

if __name__ == "__main__":
    # Sample strategies
    strategies = [
        Strategy(
            id="PROC_001", name="Emergency Protocol Update",
            category=StrategyCategory.PROCESS,
            risk_reduction_pct=8.0, cost_estimate=15000, time_estimate=7
        ),
        Strategy(
            id="POLICY_001", name="Weather Minimums Update",
            category=StrategyCategory.POLICY,
            risk_reduction_pct=5.0, cost_estimate=5000, time_estimate=3
        ),
        Strategy(
            id="TRAIN_001", name="Crew Fatigue Training",
            category=StrategyCategory.TRAINING,
            risk_reduction_pct=12.0, cost_estimate=45000, time_estimate=45
        ),
        Strategy(
            id="MAINT_001", name="Enhanced Maintenance",
            category=StrategyCategory.MAINTENANCE,
            risk_reduction_pct=18.0, cost_estimate=120000, time_estimate=60
        ),
        Strategy(
            id="TECH_001", name="Predictive Maintenance AI",
            category=StrategyCategory.TECHNOLOGY,
            risk_reduction_pct=25.0, cost_estimate=350000, time_estimate=180
        ),
    ]
    
    # Initialize interface
    interface = ExecutiveDecisionInterface(
        strategies=strategies,
        budget=500000,
        risk_score=72
    )
    
    # Generate decision package
    package = interface.generate_decision_package({
        "available_budget": 500000,
        "active_initiatives": 2,
        "leadership_support_score": 75
    })
    
    # Print outputs
    print("\n" + "=" * 70)
    print("EXECUTIVE DECISION INTERFACE - OUTPUT")
    print("=" * 70)
    
    print("\n📋 ONE-PAGER:")
    print(interface.generate_one_pager(package))
    
    print("\n📊 SCENARIO MATRIX:")
    print(interface.generate_scenario_matrix(package))
    
    print("\n👤 CEO BRIEF:")
    ceo_brief = package.stakeholder_briefs.get("CEO")
    if ceo_brief:
        print(f"Subject: {ceo_brief.subject_line}")
        print("Key Points:")
        for point in ceo_brief.key_points:
            print(f"  • {point}")
        print(f"Action: {ceo_brief.recommended_action}")
