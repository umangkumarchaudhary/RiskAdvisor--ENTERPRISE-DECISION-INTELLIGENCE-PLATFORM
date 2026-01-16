import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Types
export interface Strategy {
    id: string;
    name: string;
    category: string;
    risk_reduction_pct: number;
    cost_estimate: number;
    cost_min?: number;
    cost_max?: number;
    time_estimate: number;
    time_min?: number;
    time_max?: number;
}

export interface ContextInput {
    recent_incident_days?: number;
    budget_frozen?: boolean;
    peak_season?: boolean;
    audit_days?: number;
    available_budget?: number;
    active_initiatives?: number;
    leadership_support_score?: number;
}

export interface OptimizationRequest {
    strategies: Strategy[];
    budget_limit: number;
    timeline_limit?: number;
    risk_tolerance?: 'aggressive' | 'balanced' | 'conservative';
}

export interface DecisionPackageRequest {
    strategies: Strategy[];
    budget: number;
    risk_score: number;
    context?: ContextInput;
}

// API Functions

/**
 * Health check
 */
export async function checkHealth() {
    const response = await api.get('/health');
    return response.data;
}

/**
 * Get sample strategies
 */
export async function getSampleStrategies(): Promise<Strategy[]> {
    const response = await api.get('/api/v1/strategies/sample');
    return response.data.strategies;
}

/**
 * Optimize portfolio
 */
export async function optimizePortfolio(request: OptimizationRequest) {
    const response = await api.post('/api/v1/optimize', request);
    return response.data;
}

/**
 * Get Pareto frontier
 */
export async function getParetoFrontier(request: OptimizationRequest) {
    const response = await api.post('/api/v1/optimize/pareto', request);
    return response.data;
}

/**
 * Analyze cascading impact
 */
export async function analyzeImpact(strategy: Strategy) {
    const response = await api.post('/api/v1/impact/analyze', strategy);
    return response.data;
}

/**
 * Run war gaming
 */
export async function runWarGaming(request: OptimizationRequest) {
    const response = await api.post('/api/v1/wargame', request);
    return response.data;
}

/**
 * Get multi-horizon plan
 */
export async function getHorizonPlan(request: DecisionPackageRequest) {
    const response = await api.post('/api/v1/horizon/plan', request);
    return response.data;
}

/**
 * Detect organizational context
 */
export async function detectContext(context: ContextInput) {
    const response = await api.post('/api/v1/context/detect', context);
    return response.data;
}

/**
 * Generate executive decision package
 */
export async function getDecisionPackage(request: DecisionPackageRequest) {
    const response = await api.post('/api/v1/decision/package', request);
    return response.data;
}

export default api;
