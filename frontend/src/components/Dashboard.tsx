'use client';

import { useState, useEffect, useCallback } from 'react';
import {
    TrendingUp, DollarSign, Clock, Shield,
    ArrowUpRight, ArrowDownRight, Activity,
    AlertTriangle, CheckCircle, XCircle, Loader2, RefreshCw
} from 'lucide-react';
import { getSampleStrategies, optimizePortfolio, runWarGaming, Strategy } from '@/lib/api';

interface DashboardProps {
    riskScore: number;
}

export default function Dashboard({ riskScore }: DashboardProps) {
    const [strategies, setStrategies] = useState<Strategy[]>([]);
    const [optimizationResult, setOptimizationResult] = useState<any>(null);
    const [warGamingResult, setWarGamingResult] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [optimizing, setOptimizing] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Fetch strategies on mount
    useEffect(() => {
        fetchStrategies();
    }, []);

    const fetchStrategies = async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await getSampleStrategies();
            setStrategies(data);
        } catch (err: any) {
            setError('Failed to load strategies. Is the backend running?');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleOptimize = async () => {
        if (strategies.length === 0) return;

        try {
            setOptimizing(true);
            setError(null);

            const result = await optimizePortfolio({
                strategies,
                budget_limit: 500000,
                timeline_limit: 365,
                risk_tolerance: 'balanced'
            });

            setOptimizationResult(result);

            // Also run war gaming
            const warGame = await runWarGaming({
                strategies,
                budget_limit: 500000,
                risk_tolerance: 'balanced'
            });

            setWarGamingResult(warGame);

        } catch (err: any) {
            setError('Optimization failed. Check console for details.');
            console.error(err);
        } finally {
            setOptimizing(false);
        }
    };

    const stats = optimizationResult ? [
        {
            label: 'Risk Reduction',
            value: `${optimizationResult.total_risk_reduction?.toFixed(0)}%`,
            change: 'Optimized',
            positive: true,
            icon: TrendingUp
        },
        {
            label: 'Investment',
            value: `$${(optimizationResult.total_cost / 1000).toFixed(0)}K`,
            change: 'Within budget',
            positive: true,
            icon: DollarSign
        },
        {
            label: 'Timeline',
            value: `${optimizationResult.total_timeline_days} days`,
            change: 'Feasible',
            positive: true,
            icon: Clock
        },
        {
            label: 'Robustness',
            value: warGamingResult ? `${warGamingResult.robustness_score?.toFixed(0)}/100` : 'N/A',
            change: warGamingResult?.resilience_rating || 'Pending',
            positive: true,
            icon: Shield
        },
    ] : [
        { label: 'Strategies Available', value: strategies.length.toString(), change: 'Ready', positive: true, icon: TrendingUp },
        { label: 'Max Budget', value: '$500K', change: 'Configurable', positive: true, icon: DollarSign },
        { label: 'Max Timeline', value: '365 days', change: 'Configurable', positive: true, icon: Clock },
        { label: 'Status', value: 'Ready', change: 'Click Optimize', positive: true, icon: Shield },
    ];

    const getCategoryColor = (category: string) => {
        const colors: Record<string, string> = {
            process: 'bg-blue-500/20 text-blue-400',
            training: 'bg-purple-500/20 text-purple-400',
            maintenance: 'bg-orange-500/20 text-orange-400',
            technology: 'bg-green-500/20 text-green-400',
            policy: 'bg-pink-500/20 text-pink-400',
        };
        return colors[category] || 'bg-gray-500/20 text-gray-400';
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
                <span className="ml-3 text-dark-400">Loading strategies...</span>
            </div>
        );
    }

    if (error) {
        return (
            <div className="card p-8 text-center">
                <AlertTriangle className="w-12 h-12 text-danger-500 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">Connection Error</h3>
                <p className="text-dark-400 mb-4">{error}</p>
                <button onClick={fetchStrategies} className="btn-primary">
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Retry
                </button>
            </div>
        );
    }

    return (
        <div className="space-y-8 animate-fade-in">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {stats.map((stat, index) => (
                    <div key={index} className="card p-6 animate-slide-up" style={{ animationDelay: `${index * 0.1}s` }}>
                        <div className="flex items-start justify-between">
                            <div>
                                <p className="text-sm text-dark-400 mb-1">{stat.label}</p>
                                <p className="stat-value">{stat.value}</p>
                            </div>
                            <div className="w-10 h-10 rounded-lg bg-primary-500/20 flex items-center justify-center">
                                <stat.icon className="w-5 h-5 text-primary-400" />
                            </div>
                        </div>
                        <div className="mt-4 flex items-center gap-1">
                            <ArrowUpRight className="w-4 h-4 text-success-500" />
                            <span className="text-success-500">{stat.change}</span>
                        </div>
                    </div>
                ))}
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Strategy Portfolio */}
                <div className="lg:col-span-2 card p-6">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-lg font-semibold text-white">
                            Strategy Portfolio
                            <span className="text-dark-400 font-normal ml-2">
                                ({strategies.length} available)
                            </span>
                        </h2>
                        <button
                            onClick={handleOptimize}
                            disabled={optimizing}
                            className="btn-primary flex items-center gap-2"
                        >
                            {optimizing ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    Optimizing...
                                </>
                            ) : (
                                <>
                                    <TrendingUp className="w-4 h-4" />
                                    Optimize
                                </>
                            )}
                        </button>
                    </div>

                    <div className="space-y-4">
                        {strategies.map((strategy, index) => {
                            const isSelected = optimizationResult?.selected_strategies?.some(
                                (s: any) => s.id === strategy.id
                            );

                            return (
                                <div
                                    key={strategy.id}
                                    className={`flex items-center justify-between p-4 rounded-xl border transition-all cursor-pointer
                    ${isSelected
                                            ? 'bg-success-500/10 border-success-500/50'
                                            : 'bg-dark-800/30 border-dark-700/50 hover:border-primary-500/30'
                                        }`}
                                >
                                    <div className="flex items-center gap-4">
                                        {isSelected ? (
                                            <CheckCircle className="w-5 h-5 text-success-500" />
                                        ) : (
                                            <div className="w-5 h-5 rounded-full border-2 border-dark-600" />
                                        )}
                                        <div>
                                            <p className="font-medium text-white">{strategy.name}</p>
                                            <div className="flex items-center gap-2 mt-1">
                                                <span className={`text-xs px-2 py-0.5 rounded-full ${getCategoryColor(strategy.category)}`}>
                                                    {strategy.category}
                                                </span>
                                                <span className="text-xs text-dark-500">
                                                    {strategy.time_estimate} days
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="font-semibold text-success-400">-{strategy.risk_reduction_pct}%</p>
                                        <p className="text-sm text-dark-400">${(strategy.cost_estimate / 1000).toFixed(0)}K</p>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* War Gaming Results */}
                <div className="card p-6">
                    <h2 className="text-lg font-semibold text-white mb-6">War Gaming Results</h2>

                    {warGamingResult ? (
                        <div className="space-y-4">
                            {/* Robustness Score */}
                            <div className="p-4 bg-dark-800/50 rounded-xl text-center">
                                <p className="text-sm text-dark-400 mb-2">Robustness Score</p>
                                <p className="text-4xl font-bold gradient-text">
                                    {warGamingResult.robustness_score?.toFixed(0)}
                                </p>
                                <p className={`text-lg font-medium mt-1 ${warGamingResult.resilience_rating === 'A' ? 'text-success-400' :
                                        warGamingResult.resilience_rating === 'B' ? 'text-primary-400' :
                                            warGamingResult.resilience_rating === 'C' ? 'text-warning-400' :
                                                'text-danger-400'
                                    }`}>
                                    Grade: {warGamingResult.resilience_rating}
                                </p>
                            </div>

                            {/* Attack Results */}
                            <div>
                                <p className="text-sm text-dark-400 mb-3">Attack Scenarios</p>
                                <div className="space-y-2">
                                    {warGamingResult.attack_results?.slice(0, 3).map((attack: any, idx: number) => (
                                        <div key={idx} className="flex items-center gap-2 text-sm">
                                            {attack.still_viable ? (
                                                <CheckCircle className="w-4 h-4 text-success-400" />
                                            ) : (
                                                <XCircle className="w-4 h-4 text-danger-400" />
                                            )}
                                            <span className="text-dark-300 truncate">{attack.attack}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Recommendations */}
                            {warGamingResult.recommendations?.length > 0 && (
                                <div className="p-3 bg-primary-500/10 rounded-lg border border-primary-500/30">
                                    <p className="text-sm text-primary-400 font-medium mb-2">Recommendations</p>
                                    <ul className="text-xs text-dark-300 space-y-1">
                                        {warGamingResult.recommendations.slice(0, 2).map((rec: string, idx: number) => (
                                            <li key={idx}>• {rec}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="text-center py-8">
                            <Activity className="w-12 h-12 text-dark-600 mx-auto mb-3" />
                            <p className="text-dark-400">Run optimization to see war gaming results</p>
                        </div>
                    )}

                    {/* Risk Gauge */}
                    <div className="mt-6 p-4 bg-dark-800/50 rounded-xl">
                        <p className="text-sm text-dark-400 mb-3">Current Risk Level</p>
                        <div className="relative h-3 bg-dark-700 rounded-full overflow-hidden">
                            <div
                                className="absolute left-0 top-0 h-full bg-gradient-to-r from-success-500 via-warning-500 to-danger-500"
                                style={{ width: `${riskScore}%` }}
                            />
                        </div>
                        <div className="flex justify-between mt-2 text-xs text-dark-500">
                            <span>Low (0)</span>
                            <span className="font-medium text-white">{riskScore}</span>
                            <span>Critical (100)</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
