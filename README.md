# RiskAdvisor v4.0

🚀 **Enterprise Decision Intelligence Platform**

> From Analytics to Autonomous Decisions

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn src.api.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Architecture

```
┌────────────────────────────────────────────────────────┐
│         LAYER 7: Executive Decision Interface          │
├────────────────────────────────────────────────────────┤
│         LAYER 6: Context Intelligence Engine           │
├────────────────────────────────────────────────────────┤
│  LAYER 5: Multi-Horizon Optimization (0-30/30-180/180+)│
├────────────────────────────────────────────────────────┤
│      LAYER 4: Adversarial Validation (Red/Blue)        │
├────────────────────────────────────────────────────────┤
│   LAYER 3: Cascading Impact Analyzer (2nd/3rd order)   │
├────────────────────────────────────────────────────────┤
│         LAYER 2: Constraint Negotiation Engine         │
├────────────────────────────────────────────────────────┤
│      LAYER 1: Core Optimization (Pareto + Monte)       │
└────────────────────────────────────────────────────────┘
```

## Tech Stack

- **Backend**: FastAPI + Python 3.11
- **Frontend**: Next.js 14 + TypeScript
- **Database**: PostgreSQL (shared with AeroRisk)
- **Optimization**: PuLP, OR-Tools, CVXPY
- **ML**: XGBoost, Transformers
- **Integration**: AeroRisk API

## Features

- ✅ Multi-Horizon Decision Optimization
- ✅ Intelligent Constraint Negotiation
- ✅ Adversarial Testing (War Gaming)
- ✅ Contextual Intelligence
- ✅ Cascading Impact Analysis
- ✅ Negotiation Engine
- ✅ Continuous Learning Loop
- ✅ Stakeholder Alignment Matrix

## Author
Umang Kumar - January 2026
