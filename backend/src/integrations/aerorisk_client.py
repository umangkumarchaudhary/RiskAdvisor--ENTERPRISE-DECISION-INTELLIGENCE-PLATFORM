"""
RiskAdvisor - AeroRisk Integration
===================================
Client for connecting to the AeroRisk API to fetch risk predictions.

This enables RiskAdvisor to use real risk data from your deployed AeroRisk system
to make context-aware recommendations.
"""

import os
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AeroRisk API URL - use environment variable or default
AERORISK_API_URL = os.getenv("AERORISK_API_URL", "https://aerorisk-1.onrender.com")


@dataclass
class RiskPrediction:
    """A risk prediction from AeroRisk."""
    risk_score: float  # 0-100
    severity: str  # low, medium, high, critical
    confidence: float
    risk_factors: List[str]
    recommendations: List[str]


@dataclass 
class AeroRiskHealth:
    """AeroRisk API health status."""
    status: str
    api_available: bool
    models_loaded: bool


class AeroRiskClient:
    """
    Client for AeroRisk API.
    
    Usage:
        client = AeroRiskClient()
        risk = await client.get_risk_score(
            flight_data={"origin": "ORD", "dest": "LAX", ...}
        )
    """
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or AERORISK_API_URL
        self.timeout = 30.0  # seconds
        
    async def check_health(self) -> AeroRiskHealth:
        """Check if AeroRisk API is available."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/health")
                
                if response.status_code == 200:
                    data = response.json()
                    return AeroRiskHealth(
                        status=data.get("status", "unknown"),
                        api_available=True,
                        models_loaded=data.get("models_loaded", False)
                    )
                else:
                    return AeroRiskHealth(
                        status="error",
                        api_available=False,
                        models_loaded=False
                    )
        except Exception as e:
            logger.error(f"AeroRisk health check failed: {e}")
            return AeroRiskHealth(
                status="unreachable",
                api_available=False,
                models_loaded=False
            )
    
    async def get_risk_score(
        self,
        origin: str = "ORD",
        destination: str = "LAX",
        aircraft_type: str = "B737",
        month: int = 1,
        day_of_week: int = 1,
        scheduled_dep_time: float = 10.0,
        dep_delay: float = 0.0,
        distance: float = 1000.0,
        air_time: float = 120.0,
        **kwargs
    ) -> Optional[RiskPrediction]:
        """
        Get risk prediction from AeroRisk API.
        
        Returns None if API is unavailable.
        """
        try:
            payload = {
                "Origin": origin,
                "Dest": destination,
                "AircraftType": aircraft_type,
                "Month": month,
                "DayOfWeek": day_of_week,
                "CRSDepTime": scheduled_dep_time,
                "DepDelay": dep_delay,
                "Distance": distance,
                "AirTime": air_time,
            }
            
            # Add any extra fields
            payload.update(kwargs)
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/predict",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract risk score from prediction
                    risk_score = data.get("ensemble_risk_score", 50.0)
                    
                    # Determine severity
                    if risk_score >= 75:
                        severity = "critical"
                    elif risk_score >= 50:
                        severity = "high"
                    elif risk_score >= 25:
                        severity = "medium"
                    else:
                        severity = "low"
                    
                    return RiskPrediction(
                        risk_score=risk_score,
                        severity=severity,
                        confidence=data.get("confidence", 0.8),
                        risk_factors=data.get("risk_factors", []),
                        recommendations=data.get("recommendations", [])
                    )
                else:
                    logger.error(f"AeroRisk prediction failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"AeroRisk prediction error: {e}")
            return None
    
    async def get_recommendations(
        self,
        risk_score: float,
        context: Dict = None
    ) -> List[Dict]:
        """
        Get recommendations from AeroRisk for a given risk score.
        """
        try:
            payload = {
                "risk_score": risk_score,
                "context": context or {}
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/recommend",
                    json=payload
                )
                
                if response.status_code == 200:
                    return response.json().get("recommendations", [])
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"AeroRisk recommendations error: {e}")
            return []
    
    async def get_analytics(
        self,
        start_date: str = None,
        end_date: str = None,
        category: str = None
    ) -> Dict:
        """
        Get analytics data from AeroRisk.
        """
        try:
            params = {}
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            if category:
                params["category"] = category
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/analytics",
                    params=params
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": "Failed to fetch analytics"}
                    
        except Exception as e:
            logger.error(f"AeroRisk analytics error: {e}")
            return {"error": str(e)}


# Singleton instance
aerorisk_client = AeroRiskClient()


# ============================================
# EXAMPLE USAGE
# ============================================

if __name__ == "__main__":
    import asyncio
    
    async def test_client():
        client = AeroRiskClient()
        
        print("Checking AeroRisk health...")
        health = await client.check_health()
        print(f"Status: {health.status}")
        print(f"API Available: {health.api_available}")
        print(f"Models Loaded: {health.models_loaded}")
        
        if health.api_available:
            print("\nGetting risk prediction...")
            risk = await client.get_risk_score(
                origin="ORD",
                destination="LAX",
                aircraft_type="B737"
            )
            if risk:
                print(f"Risk Score: {risk.risk_score}")
                print(f"Severity: {risk.severity}")
                print(f"Confidence: {risk.confidence}")
    
    asyncio.run(test_client())
