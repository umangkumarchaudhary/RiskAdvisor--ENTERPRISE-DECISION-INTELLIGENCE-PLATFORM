'use client';

import { useState, useEffect } from 'react';
import {
    Zap, Clock, Target, ArrowRight,
    CheckCircle, AlertTriangle, TrendingUp, Loader2
} from 'lucide-react';
import { getSampleStrategies, getHorizonPlan, Strategy } from '@/lib/api';

interface HorizonPlannerProps {
    riskScore: number;
}

export default function HorizonPlanner({ riskScore }: HorizonPlannerProps) {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [horizonPlan, setHorizonPlan] = useState<any>(null);

    useEffect(() => {
        loadHorizonPlan();
    }, [riskScore]);

    const loadHorizonPlan = async () => {
        try {
            setLoading(true);
            setError(null);

            const strategies = await getSampleStrategies();
            const plan = await getHorizonPlan({
                strategies,
                budget: 500000,
                risk_score: riskScore
            });

            setHorizonPlan(plan);
        } catch (err: any) {
            setError('Failed to generate horizon plan');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
                <span className="ml-3 text-dark-400">Generating horizon plan...</span>
            </div>
        );
    }

    if (error) {
        return (
            <div className="card p-8 text-center">
                <AlertTriangle className="w-12 h-12 text-danger-500 mx-auto mb-4" />
                <p className="text-dark-400">{error}</p>
            </div>
        );
    }

    const horizons = [
        {
            key: 'immediate',
            label: 'Immediate',
            subtitle: '0-30 days',
            icon: Zap,
            bgColor: 'bg-danger-500/10',
            borderColor: 'border-danger-500/30',
            iconBg: 'bg-danger-500/20',
            iconColor: 'text-danger-400',
            data: horizonPlan?.immediate
        },
        {
            key: 'tactical',
            label: 'Tactical',
            subtitle: '30-180 days',
            icon: Clock,
            bgColor: 'bg-warning-500/10',
            borderColor: 'border-warning-500/30',
            iconBg: 'bg-warning-500/20',
            iconColor: 'text-warning-400',
            data: horizonPlan?.tactical
        },
        {
            key: 'strategic',
            label: 'Strategic',
            subtitle: '180+ days',
            icon: Target,
            bgColor: 'bg-success-500/10',
            borderColor: 'border-success-500/30',
            iconBg: 'bg-success-500/20',
            iconColor: 'text-success-400',
            data: horizonPlan?.strategic
        }
    ];

    const totalCost = horizonPlan?.total_cost || 0;
    const totalReduction = horizonPlan?.total_risk_reduction || 0;

    return (
        <div className="space-y-8 animate-fade-in">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-white">Multi-Horizon Planner</h2>
                    <p className="text-dark-400 mt-1">
                        Optimize across Immediate, Tactical, and Strategic time horizons
                    </p>
                </div>
                <div className="flex items-center gap-4">
                    <div className="text-right">
                        <p className="text-sm text-dark-400">Total Investment</p>
                        <p className="text-2xl font-bold gradient-text">${(totalCost / 1000).toFixed(0)}K</p>
                    </div>
                    <ArrowRight className="w-6 h-6 text-dark-500" />
                    <div className="text-right">
                        <p className="text-sm text-dark-400">Total Risk Reduction</p>
                        <p className="text-2xl font-bold text-success-400">{totalReduction.toFixed(0)}%</p>
                    </div>
                </div>
            </div>

            {/* Timeline Visualization */}
            <div className="relative">
                <div className="absolute left-8 top-0 bottom-0 w-1 bg-gradient-to-b from-danger-500 via-warning-500 to-success-500 rounded-full" />

                <div className="space-y-8">
                    {horizons.map((horizon, index) => (
                        <div key={horizon.key} className="relative pl-20">
                            {/* Timeline Node */}
                            <div className={`absolute left-6 w-5 h-5 rounded-full ${horizon.iconBg} border-2 ${horizon.borderColor} -translate-x-1/2`}>
                                <div className={`absolute inset-1 rounded-full ${horizon.iconBg}`} />
                            </div>

                            {/* Content Card */}
                            <div className={`card ${horizon.bgColor} ${horizon.borderColor} border p-6`}>
                                <div className="flex items-start justify-between mb-6">
                                    <div className="flex items-center gap-4">
                                        <div className={`w-12 h-12 rounded-xl ${horizon.iconBg} flex items-center justify-center`}>
                                            <horizon.icon className={`w-6 h-6 ${horizon.iconColor}`} />
                                        </div>
                                        <div>
                                            <h3 className="text-xl font-semibold text-white">{horizon.label}</h3>
                                            <p className="text-dark-400">{horizon.data?.label || horizon.subtitle}</p>
                                        </div>
                                    </div>
                                    {horizon.data?.decision_deadline && (
                                        <div className={`px-3 py-1.5 rounded-lg ${horizon.bgColor} ${horizon.borderColor} border`}>
                                            <p className={`text-sm font-medium ${horizon.iconColor}`}>{horizon.data.decision_deadline}</p>
                                        </div>
                                    )}
                                </div>

                                {/* Strategies */}
                                {horizon.data?.strategies?.length > 0 ? (
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                                        {horizon.data.strategies.map((strategyName: string, idx: number) => (
                                            <div key={idx} className="p-4 bg-dark-800/30 rounded-xl border border-dark-700/50">
                                                <div className="flex items-center gap-2">
                                                    <CheckCircle className={`w-4 h-4 ${horizon.iconColor}`} />
                                                    <span className="font-medium text-white">{strategyName}</span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="p-4 bg-dark-800/30 rounded-xl text-center mb-6">
                                        <p className="text-dark-500">No strategies in this horizon</p>
                                    </div>
                                )}

                                {/* Action Items */}
                                {horizon.data?.action_items?.length > 0 && (
                                    <div className="mb-6">
                                        <p className="text-sm text-dark-400 mb-2">Action Items:</p>
                                        <div className="space-y-2">
                                            {horizon.data.action_items.map((item: string, idx: number) => (
                                                <p key={idx} className="text-sm text-dark-300">{item}</p>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Summary */}
                                <div className="flex items-center justify-between p-4 bg-dark-800/50 rounded-xl">
                                    <div className="flex items-center gap-6">
                                        <div>
                                            <p className="text-sm text-dark-400">Cost</p>
                                            <p className="text-lg font-semibold text-white">
                                                ${((horizon.data?.cost || 0) / 1000).toFixed(0)}K
                                            </p>
                                        </div>
                                        <div>
                                            <p className="text-sm text-dark-400">Risk Reduction</p>
                                            <p className="text-lg font-semibold text-success-400">
                                                {(horizon.data?.risk_reduction || 0).toFixed(0)}%
                                            </p>
                                        </div>
                                        <div>
                                            <p className="text-sm text-dark-400">Strategies</p>
                                            <p className="text-lg font-semibold text-white">
                                                {horizon.data?.strategies?.length || 0}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Trade-off Analysis */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="card p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Quick Fix vs Sustainable</h3>
                    <div className="space-y-4">
                        <div className="flex justify-between items-center p-4 bg-danger-500/10 rounded-xl border border-danger-500/30">
                            <div>
                                <p className="font-medium text-white">Immediate Actions Only</p>
                                <p className="text-sm text-dark-400">Fast but temporary</p>
                            </div>
                            <div className="text-right">
                                <p className="text-xl font-bold text-danger-400">
                                    {horizonPlan?.immediate?.risk_reduction?.toFixed(0) || 0}%
                                </p>
                                <p className="text-sm text-dark-400">
                                    ${((horizonPlan?.immediate?.cost || 0) / 1000).toFixed(0)}K
                                </p>
                            </div>
                        </div>
                        <div className="flex justify-between items-center p-4 bg-success-500/10 rounded-xl border border-success-500/30">
                            <div>
                                <p className="font-medium text-white">Full Multi-Horizon</p>
                                <p className="text-sm text-dark-400">Sustainable improvement</p>
                            </div>
                            <div className="text-right">
                                <p className="text-xl font-bold text-success-400">{totalReduction.toFixed(0)}%</p>
                                <p className="text-sm text-dark-400">${(totalCost / 1000).toFixed(0)}K</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="card p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Recommendation</h3>
                    <div className={`p-4 rounded-xl ${riskScore >= 75
                            ? 'bg-danger-500/10 border border-danger-500/30'
                            : riskScore >= 50
                                ? 'bg-warning-500/10 border border-warning-500/30'
                                : 'bg-success-500/10 border border-success-500/30'
                        }`}>
                        <div className="flex items-start gap-3">
                            <AlertTriangle className={`w-5 h-5 flex-shrink-0 mt-0.5 ${riskScore >= 75 ? 'text-danger-400' : riskScore >= 50 ? 'text-warning-400' : 'text-success-400'
                                }`} />
                            <div>
                                <p className={`font-medium ${riskScore >= 75 ? 'text-danger-400' : riskScore >= 50 ? 'text-warning-400' : 'text-success-400'
                                    }`}>
                                    {horizonPlan?.tradeoff?.recommendation ||
                                        (riskScore >= 75
                                            ? 'URGENT: Prioritize immediate actions'
                                            : riskScore >= 50
                                                ? 'BALANCED: Execute all three horizons'
                                                : 'STRATEGIC: Focus on long-term improvements'
                                        )
                                    }
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="mt-6 flex items-center justify-between">
                        <div>
                            <p className="text-sm text-dark-400">Cost Effectiveness</p>
                            <p className="text-2xl font-bold gradient-text">
                                ${totalReduction > 0 ? (totalCost / totalReduction / 1000).toFixed(1) : 0}K
                            </p>
                            <p className="text-sm text-dark-500">per 1% risk reduction</p>
                        </div>
                        <button className="btn-primary">
                            <TrendingUp className="w-4 h-4 mr-2" />
                            Execute Plan
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
