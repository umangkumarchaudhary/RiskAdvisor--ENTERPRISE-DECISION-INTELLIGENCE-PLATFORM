"""
RiskAdvisor - Layer 6: Context Intelligence Engine
====================================================
Detects organizational context and adapts recommendations accordingly.

Key Features:
- Organizational state detection (normal, crisis, post-incident)
- Stakeholder sentiment analysis
- Resource reality assessment
- Change saturation monitoring
- Context-aware recommendation adaptation

Author: Umang Kumar
Date: January 2026
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import logging
from datetime import datetime, date

from src.core.optimizer import Strategy, OptimizationResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================
# DATA MODELS
# ============================================

class OrgState(Enum):
    NORMAL = "normal"              # Business as usual
    POST_INCIDENT = "post_incident"  # Recently had an incident
    CRISIS = "crisis"              # Active crisis mode
    AUDIT_PREP = "audit_prep"      # Preparing for audit
    PEAK_SEASON = "peak_season"    # High operational demand
    TRANSITION = "transition"      # Leadership/strategic change
    BUDGET_FREEZE = "budget_freeze"  # Limited financial resources


class StakeholderSentiment(Enum):
    SUPPORTIVE = "supportive"
    NEUTRAL = "neutral"
    RESISTANT = "resistant"
    FATIGUED = "fatigued"


@dataclass
class OrganizationalContext:
    """Current organizational context snapshot."""
    # State
    org_state: OrgState
    state_since: Optional[date] = None
    
    # Resources
    available_budget: float = 0
    available_fte: float = 0
    budget_flexibility: str = "medium"  # low, medium, high
    
    # Change capacity
    active_initiatives: int = 0
    change_capacity_pct: float = 100  # How much more change can org absorb
    
    # Stakeholders
    leadership_support: StakeholderSentiment = StakeholderSentiment.NEUTRAL
    employee_sentiment: StakeholderSentiment = StakeholderSentiment.NEUTRAL
    union_sentiment: StakeholderSentiment = StakeholderSentiment.NEUTRAL
    
    # External factors
    regulatory_pressure: str = "normal"  # low, normal, high, critical
    media_attention: bool = False
    competitive_pressure: bool = False
    
    # Timing
    is_peak_season: bool = False
    quarter: str = "Q1"
    days_to_year_end: int = 365


@dataclass
class ContextAdaptation:
    """How to adapt recommendations based on context."""
    approach_name: str
    approach_description: str
    
    # Modifications
    budget_multiplier: float = 1.0
    timeline_multiplier: float = 1.0
    scope_adjustment: str = "full"  # full, reduced, minimal, phased
    
    # Prioritization
    prioritize_categories: List[str] = field(default_factory=list)
    avoid_categories: List[str] = field(default_factory=list)
    
    # Communication
    framing: str = ""
    key_messages: List[str] = field(default_factory=list)
    
    # Risk
    confidence_score: float = 0.8


@dataclass
class ContextualRecommendation:
    """Recommendation adapted to organizational context."""
    context: OrganizationalContext
    adaptation: ContextAdaptation
    
    # Original vs adapted
    original_strategies: List[Strategy]
    adapted_strategies: List[Strategy]
    
    # Outcomes
    original_cost: float
    adapted_cost: float
    original_risk_reduction: float
    adapted_risk_reduction: float
    
    # Explanation
    adaptation_rationale: str
    trade_offs: List[str] = field(default_factory=list)


# ============================================
# CONTEXT INTELLIGENCE ENGINE
# ============================================

class ContextIntelligenceEngine:
    """
    Detects organizational context and adapts recommendations.
    
    Same risk score can lead to DIFFERENT recommendations based on:
    - Is this post-incident? → Need visible quick wins
    - Is budget frozen? → Focus on no-cost process changes
    - Is it peak season? → Minimize operational disruption
    - Is leadership supportive? → Can push ambitious plans
    """
    
    def __init__(self):
        self.adaptation_rules = self._build_adaptation_rules()
    
    def _build_adaptation_rules(self) -> Dict[OrgState, ContextAdaptation]:
        """Build adaptation rules for each organizational state."""
        return {
            OrgState.NORMAL: ContextAdaptation(
                approach_name="Balanced Optimization",
                approach_description="Standard optimization balancing risk, cost, and timeline",
                budget_multiplier=1.0,
                timeline_multiplier=1.0,
                scope_adjustment="full",
                prioritize_categories=["maintenance", "training"],
                framing="Proactive risk management investment",
                key_messages=[
                    "Building sustainable safety improvements",
                    "Cost-effective risk reduction portfolio",
                    "Long-term value creation"
                ],
                confidence_score=0.9
            ),
            
            OrgState.POST_INCIDENT: ContextAdaptation(
                approach_name="Recovery & Visibility",
                approach_description="Quick wins for visible progress + root cause fixes",
                budget_multiplier=1.3,  # Usually get more budget post-incident
                timeline_multiplier=0.7,  # Need faster execution
                scope_adjustment="phased",
                prioritize_categories=["process", "policy"],  # Quick to implement
                avoid_categories=["technology"],  # Takes too long
                framing="Incident response and prevention",
                key_messages=[
                    "Immediate actions to prevent recurrence",
                    "Demonstrating commitment to safety",
                    "Addressing root causes identified in investigation"
                ],
                confidence_score=0.85
            ),
            
            OrgState.CRISIS: ContextAdaptation(
                approach_name="Emergency Response",
                approach_description="Minimum viable interventions, maximum speed",
                budget_multiplier=1.5,  # Emergency funding available
                timeline_multiplier=0.5,  # Extremely urgent
                scope_adjustment="minimal",
                prioritize_categories=["policy", "process"],
                avoid_categories=["technology", "training"],
                framing="Crisis stabilization",
                key_messages=[
                    "Stop the bleeding NOW",
                    "Minimum viable safety actions",
                    "Full plan to follow once stable"
                ],
                confidence_score=0.7
            ),
            
            OrgState.BUDGET_FREEZE: ContextAdaptation(
                approach_name="Zero-Cost Innovation",
                approach_description="Process changes and policy updates only",
                budget_multiplier=0.2,
                timeline_multiplier=1.0,
                scope_adjustment="reduced",
                prioritize_categories=["process", "policy"],
                avoid_categories=["technology", "training"],  # Cost money
                framing="Efficiency through process optimization",
                key_messages=[
                    "No-cost and low-cost improvements",
                    "Building the case for future investment",
                    "Data collection for next budget cycle"
                ],
                confidence_score=0.75
            ),
            
            OrgState.PEAK_SEASON: ContextAdaptation(
                approach_name="Minimal Disruption",
                approach_description="Defer non-critical items, protect operations",
                budget_multiplier=0.8,
                timeline_multiplier=1.5,  # Extended timeline, post-peak
                scope_adjustment="reduced",
                prioritize_categories=["policy"],  # Low disruption
                avoid_categories=["maintenance"],  # High disruption
                framing="Operational protection with safety maintenance",
                key_messages=[
                    "Don't disrupt during critical period",
                    "Queue improvements for post-peak",
                    "Address only immediate safety concerns"
                ],
                confidence_score=0.8
            ),
            
            OrgState.AUDIT_PREP: ContextAdaptation(
                approach_name="Compliance Focus",
                approach_description="Prioritize audit-visible improvements",
                budget_multiplier=1.0,
                timeline_multiplier=0.8,  # Need before audit
                scope_adjustment="full",
                prioritize_categories=["process", "training"],  # Auditable
                framing="Audit readiness and compliance excellence",
                key_messages=[
                    "Addressing known audit findings",
                    "Demonstrating proactive compliance",
                    "Documentation and evidence trail"
                ],
                confidence_score=0.85
            ),
        }
    
    def detect_context(
        self,
        indicators: Dict
    ) -> OrganizationalContext:
        """
        Detect organizational context from indicators.
        
        Indicators can include:
        - Recent incidents
        - Budget status
        - Current initiatives
        - Time of year
        - Leadership changes
        """
        # Determine org state
        org_state = OrgState.NORMAL
        
        if indicators.get("recent_incident_days", 365) < 30:
            org_state = OrgState.POST_INCIDENT
        elif indicators.get("active_crisis", False):
            org_state = OrgState.CRISIS
        elif indicators.get("budget_frozen", False):
            org_state = OrgState.BUDGET_FREEZE
        elif indicators.get("peak_season", False):
            org_state = OrgState.PEAK_SEASON
        elif indicators.get("audit_days", 365) < 60:
            org_state = OrgState.AUDIT_PREP
        
        # Calculate change capacity
        active_initiatives = indicators.get("active_initiatives", 0)
        max_initiatives = indicators.get("max_initiatives", 5)
        change_capacity = max(0, (max_initiatives - active_initiatives) / max_initiatives * 100)
        
        # Determine stakeholder sentiments
        leadership = StakeholderSentiment.NEUTRAL
        if indicators.get("leadership_support_score", 50) > 70:
            leadership = StakeholderSentiment.SUPPORTIVE
        elif indicators.get("leadership_support_score", 50) < 30:
            leadership = StakeholderSentiment.RESISTANT
        
        return OrganizationalContext(
            org_state=org_state,
            available_budget=indicators.get("available_budget", 0),
            available_fte=indicators.get("available_fte", 0),
            active_initiatives=active_initiatives,
            change_capacity_pct=change_capacity,
            leadership_support=leadership,
            regulatory_pressure=indicators.get("regulatory_pressure", "normal"),
            media_attention=indicators.get("media_attention", False),
            is_peak_season=indicators.get("peak_season", False),
            quarter=indicators.get("quarter", "Q1")
        )
    
    def adapt_recommendations(
        self,
        original_result: OptimizationResult,
        context: OrganizationalContext,
        strategies: List[Strategy]
    ) -> ContextualRecommendation:
        """
        Adapt recommendations based on organizational context.
        """
        adaptation = self.adaptation_rules.get(
            context.org_state,
            self.adaptation_rules[OrgState.NORMAL]
        )
        
        # Apply scope adjustment
        adapted_strategies = []
        
        if adaptation.scope_adjustment == "full":
            adapted_strategies = original_result.selected_strategies.copy()
        
        elif adaptation.scope_adjustment == "reduced":
            # Keep high-priority strategies only
            adapted_strategies = [
                s for s in original_result.selected_strategies
                if s.category.value in adaptation.prioritize_categories
                or s.risk_reduction_pct >= 15  # High impact
            ]
        
        elif adaptation.scope_adjustment == "minimal":
            # Only quick wins
            adapted_strategies = [
                s for s in original_result.selected_strategies
                if s.category.value in adaptation.prioritize_categories
                and s.cost_estimate < 50000
                and s.time_estimate < 30
            ]
        
        elif adaptation.scope_adjustment == "phased":
            # Prioritize by category, phase the rest
            priority = [
                s for s in original_result.selected_strategies
                if s.category.value in adaptation.prioritize_categories
            ]
            adapted_strategies = priority[:3] if len(priority) > 3 else priority
        
        # Remove avoided categories
        adapted_strategies = [
            s for s in adapted_strategies
            if s.category.value not in adaptation.avoid_categories
        ]
        
        # Apply budget constraints
        available = context.available_budget * adaptation.budget_multiplier
        final_strategies = []
        total_cost = 0
        
        for s in adapted_strategies:
            if total_cost + s.cost_estimate <= available:
                final_strategies.append(s)
                total_cost += s.cost_estimate
        
        # Calculate outcomes
        adapted_cost = sum(s.cost_estimate for s in final_strategies)
        adapted_risk_reduction = sum(s.risk_reduction_pct for s in final_strategies)
        
        # Generate rationale
        rationale = self._generate_rationale(
            context, adaptation, original_result, final_strategies
        )
        
        # Identify trade-offs
        trade_offs = []
        if len(final_strategies) < len(original_result.selected_strategies):
            trade_offs.append(
                f"Reduced from {len(original_result.selected_strategies)} to "
                f"{len(final_strategies)} strategies due to {context.org_state.value} context"
            )
        if adapted_risk_reduction < original_result.total_risk_reduction:
            trade_offs.append(
                f"Risk reduction reduced from {original_result.total_risk_reduction:.0f}% to "
                f"{adapted_risk_reduction:.0f}% but achievable in current context"
            )
        
        return ContextualRecommendation(
            context=context,
            adaptation=adaptation,
            original_strategies=original_result.selected_strategies,
            adapted_strategies=final_strategies,
            original_cost=original_result.total_cost,
            adapted_cost=adapted_cost,
            original_risk_reduction=original_result.total_risk_reduction,
            adapted_risk_reduction=adapted_risk_reduction,
            adaptation_rationale=rationale,
            trade_offs=trade_offs
        )
    
    def _generate_rationale(
        self,
        context: OrganizationalContext,
        adaptation: ContextAdaptation,
        original: OptimizationResult,
        adapted: List[Strategy]
    ) -> str:
        """Generate explanation for adaptation."""
        return (
            f"Given the organization is in {context.org_state.value} state, "
            f"we've adapted the recommendation to use the '{adaptation.approach_name}' approach. "
            f"{adaptation.approach_description}. "
            f"This reduces scope from {len(original.selected_strategies)} to {len(adapted)} strategies, "
            f"focusing on {', '.join(adaptation.prioritize_categories) if adaptation.prioritize_categories else 'all categories'}."
        )
    
    def generate_context_report(
        self,
        context: OrganizationalContext,
        adapted_rec: ContextualRecommendation
    ) -> str:
        """Generate context-aware recommendation report."""
        lines = [
            "=" * 70,
            "🎯 CONTEXT-AWARE RECOMMENDATION",
            "=" * 70,
            "",
            f"📊 ORGANIZATIONAL STATE: {context.org_state.value.upper()}",
            f"   Change Capacity: {context.change_capacity_pct:.0f}%",
            f"   Leadership Support: {context.leadership_support.value}",
            f"   Regulatory Pressure: {context.regulatory_pressure}",
            "",
            "─" * 70,
            f"🔄 ADAPTATION: {adapted_rec.adaptation.approach_name}",
            "─" * 70,
            f"   {adapted_rec.adaptation.approach_description}",
            "",
            "   Key Messages:",
        ]
        
        for msg in adapted_rec.adaptation.key_messages:
            lines.append(f"   • {msg}")
        
        lines.extend([
            "",
            "─" * 70,
            "📋 ADAPTED RECOMMENDATIONS",
            "─" * 70,
        ])
        
        for s in adapted_rec.adapted_strategies:
            lines.append(f"   ✓ {s.name}")
            lines.append(f"     Cost: ${s.cost_estimate:,.0f} | Risk↓: {s.risk_reduction_pct}%")
        
        lines.extend([
            "",
            "─" * 70,
            "⚖️ TRADE-OFFS",
            "─" * 70,
        ])
        
        for trade in adapted_rec.trade_offs:
            lines.append(f"   • {trade}")
        
        if not adapted_rec.trade_offs:
            lines.append("   • No significant trade-offs")
        
        lines.extend([
            "",
            f"📈 OUTCOME: ${adapted_rec.adapted_cost:,.0f} → "
            f"{adapted_rec.adapted_risk_reduction:.0f}% risk reduction",
            "",
            f"💡 {adapted_rec.adaptation.framing}",
            "",
            "=" * 70,
        ])
        
        return "\n".join(lines)


# ============================================
# EXAMPLE USAGE
# ============================================

if __name__ == "__main__":
    from src.core.optimizer import Strategy, StrategyCategory, CoreOptimizer
    
    # Sample strategies
    strategies = [
        Strategy(
            id="PROC_001", name="Emergency Protocol Update",
            category=StrategyCategory.PROCESS,
            risk_reduction_pct=10.0, cost_estimate=15000, time_estimate=14
        ),
        Strategy(
            id="TRAIN_001", name="Crew Fatigue Training",
            category=StrategyCategory.TRAINING,
            risk_reduction_pct=12.0, cost_estimate=45000, time_estimate=45
        ),
        Strategy(
            id="TECH_001", name="Safety Management System",
            category=StrategyCategory.TECHNOLOGY,
            risk_reduction_pct=25.0, cost_estimate=280000, time_estimate=120
        ),
    ]
    
    # Get optimal portfolio (ignoring context)
    optimizer = CoreOptimizer(strategies, [])
    optimal = optimizer.get_optimal_portfolio(budget_limit=500000)
    
    # Initialize context engine
    engine = ContextIntelligenceEngine()
    
    # Scenario 1: Post-incident
    print("\n" + "=" * 70)
    print("SCENARIO: POST-INCIDENT CONTEXT")
    print("=" * 70)
    
    context1 = engine.detect_context({
        "recent_incident_days": 15,
        "available_budget": 200000,
        "active_initiatives": 2,
        "leadership_support_score": 85
    })
    
    adapted1 = engine.adapt_recommendations(optimal, context1, strategies)
    print(engine.generate_context_report(context1, adapted1))
    
    # Scenario 2: Budget freeze
    print("\n" + "=" * 70)
    print("SCENARIO: BUDGET FREEZE CONTEXT")
    print("=" * 70)
    
    context2 = engine.detect_context({
        "budget_frozen": True,
        "available_budget": 50000,
        "active_initiatives": 4,
        "leadership_support_score": 40
    })
    
    adapted2 = engine.adapt_recommendations(optimal, context2, strategies)
    print(engine.generate_context_report(context2, adapted2))
