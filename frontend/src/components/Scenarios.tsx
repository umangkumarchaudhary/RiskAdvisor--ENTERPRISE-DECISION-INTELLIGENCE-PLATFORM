'use client';

import { useState, useEffect } from 'react';
import {
    CheckCircle, XCircle, AlertTriangle,
    TrendingUp, DollarSign, Clock, Target, Loader2
} from 'lucide-react';
import { getSampleStrategies, getDecisionPackage, Strategy } from '@/lib/api';

interface ScenariosProps {
    riskScore: number;
}

export default function Scenarios({ riskScore }: ScenariosProps) {
    const [selectedScenario, setSelectedScenario] = useState<string>('');
    const [scenarios, setScenarios] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadScenarios();
    }, [riskScore]);

    const loadScenarios = async () => {
        try {
            setLoading(true);
            setError(null);

            const strategies = await getSampleStrategies();
            const pkg = await getDecisionPackage({
                strategies,
                budget: 500000,
                risk_score: riskScore
            });

            setScenarios(pkg.scenarios || []);

            // Select recommended by default
            const recommended = pkg.scenarios?.find((s: any) => s.recommended);
            if (recommended) {
                setSelectedScenario(recommended.id);
            }
        } catch (err: any) {
            setError('Failed to load scenarios');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
                <span className="ml-3 text-dark-400">Generating scenarios...</span>
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

    const selectedData = scenarios.find(s => s.id === selectedScenario);

    return (
        <div className="space-y-8 animate-fade-in">
            {/* Header */}
            <div>
                <h2 className="text-2xl font-bold text-white">Scenario Comparison</h2>
                <p className="text-dark-400 mt-1">Compare different decision paths and their outcomes</p>
            </div>

            {/* Scenario Cards */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                {scenarios.map((scenario) => (
                    <button
                        key={scenario.id}
                        onClick={() => setSelectedScenario(scenario.id)}
                        className={`p-4 rounded-xl border text-left transition-all
              ${selectedScenario === scenario.id
                                ? 'bg-primary-500/20 border-primary-500/50'
                                : 'bg-dark-800/30 border-dark-700/50 hover:border-dark-600'
                            }
              ${scenario.recommended ? 'ring-2 ring-success-500/50' : ''}
            `}
                    >
                        <div className="flex items-center justify-between mb-2">
                            <span className={`text-sm font-medium ${selectedScenario === scenario.id ? 'text-white' : 'text-dark-300'
                                }`}>
                                {scenario.name}
                            </span>
                            {scenario.recommended && (
                                <CheckCircle className="w-4 h-4 text-success-400" />
                            )}
                        </div>
                        <p className="text-xs text-dark-500 line-clamp-1">{scenario.description}</p>
                        <div className="mt-3 flex items-center gap-2">
                            <span className="text-lg font-bold text-white">
                                {scenario.risk_reduction?.toFixed(0)}%
                            </span>
                            <span className="text-xs text-dark-500">risk ↓</span>
                        </div>
                    </button>
                ))}
            </div>

            {/* Selected Scenario Details */}
            {selectedData && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Metrics */}
                    <div className="card p-6">
                        <h3 className="text-lg font-semibold text-white mb-6">{selectedData.name} - Details</h3>

                        <div className="grid grid-cols-2 gap-6">
                            <div className="space-y-4">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-lg bg-primary-500/20 flex items-center justify-center">
                                        <DollarSign className="w-5 h-5 text-primary-400" />
                                    </div>
                                    <div>
                                        <p className="text-sm text-dark-400">Cost</p>
                                        <p className="text-xl font-bold text-white">
                                            ${(selectedData.cost / 1000).toFixed(0)}K
                                        </p>
                                    </div>
                                </div>

                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-lg bg-success-500/20 flex items-center justify-center">
                                        <TrendingUp className="w-5 h-5 text-success-400" />
                                    </div>
                                    <div>
                                        <p className="text-sm text-dark-400">Risk Reduction</p>
                                        <p className="text-xl font-bold text-white">{selectedData.risk_reduction?.toFixed(0)}%</p>
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-4">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-lg bg-warning-500/20 flex items-center justify-center">
                                        <Clock className="w-5 h-5 text-warning-400" />
                                    </div>
                                    <div>
                                        <p className="text-sm text-dark-400">Timeline</p>
                                        <p className="text-xl font-bold text-white">{selectedData.timeline_days} days</p>
                                    </div>
                                </div>

                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-lg bg-dark-600/50 flex items-center justify-center">
                                        <Target className="w-5 h-5 text-dark-300" />
                                    </div>
                                    <div>
                                        <p className="text-sm text-dark-400">Confidence</p>
                                        <p className="text-xl font-bold text-white">{(selectedData.confidence * 100).toFixed(0)}%</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="mt-6 p-4 bg-dark-800/50 rounded-xl">
                            <p className="text-sm text-dark-400 mb-1">Disruption Level</p>
                            <div className="flex items-center gap-3">
                                <div className="flex-1 h-2 bg-dark-700 rounded-full overflow-hidden">
                                    <div
                                        className={`h-full ${selectedData.disruption_level === 'None' ? 'w-0' :
                                                selectedData.disruption_level === 'Low' ? 'w-1/4 bg-success-500' :
                                                    selectedData.disruption_level === 'Medium' ? 'w-1/2 bg-warning-500' :
                                                        'w-full bg-danger-500'
                                            }`}
                                    />
                                </div>
                                <span className="text-sm text-dark-300">{selectedData.disruption_level}</span>
                            </div>
                        </div>
                    </div>

                    {/* Rationale */}
                    <div className="card p-6">
                        <h3 className="text-lg font-semibold text-white mb-6">Analysis</h3>

                        <div className={`p-4 rounded-xl ${selectedData.recommended
                                ? 'bg-success-500/10 border border-success-500/30'
                                : 'bg-dark-800/50 border border-dark-700/50'
                            }`}>
                            {selectedData.recommended ? (
                                <div className="flex items-start gap-3">
                                    <CheckCircle className="w-5 h-5 text-success-400 flex-shrink-0 mt-0.5" />
                                    <div>
                                        <p className="font-medium text-success-400">Recommended Choice</p>
                                        <p className="text-dark-200 mt-1">{selectedData.rationale}</p>
                                    </div>
                                </div>
                            ) : (
                                <div className="flex items-start gap-3">
                                    <AlertTriangle className="w-5 h-5 text-warning-400 flex-shrink-0 mt-0.5" />
                                    <div>
                                        <p className="font-medium text-warning-400">Trade-off</p>
                                        <p className="text-dark-200 mt-1">{selectedData.rationale}</p>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Cost Effectiveness */}
                        <div className="mt-6">
                            <h4 className="text-sm font-semibold text-dark-300 uppercase tracking-wider mb-4">
                                Cost Effectiveness
                            </h4>
                            <div className="flex items-center gap-4">
                                <div className="flex-1">
                                    <p className="text-3xl font-bold gradient-text">
                                        ${selectedData.cost > 0 && selectedData.risk_reduction > 0
                                            ? (selectedData.cost / selectedData.risk_reduction / 1000).toFixed(1)
                                            : '0'}K
                                    </p>
                                    <p className="text-sm text-dark-400 mt-1">per 1% risk reduction</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Comparison Table */}
            <div className="card overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-dark-800/50">
                            <tr>
                                <th className="px-6 py-4 text-left text-sm font-semibold text-dark-300">Scenario</th>
                                <th className="px-6 py-4 text-right text-sm font-semibold text-dark-300">Cost</th>
                                <th className="px-6 py-4 text-right text-sm font-semibold text-dark-300">Risk ↓</th>
                                <th className="px-6 py-4 text-right text-sm font-semibold text-dark-300">Timeline</th>
                                <th className="px-6 py-4 text-center text-sm font-semibold text-dark-300">Disruption</th>
                                <th className="px-6 py-4 text-right text-sm font-semibold text-dark-300">Confidence</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-dark-700/50">
                            {scenarios.map((s) => (
                                <tr
                                    key={s.id}
                                    className={`hover:bg-dark-800/30 transition-colors cursor-pointer ${s.recommended ? 'bg-success-500/5' : ''
                                        }`}
                                    onClick={() => setSelectedScenario(s.id)}
                                >
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-2">
                                            <span className="font-medium text-white">{s.name}</span>
                                            {s.recommended && (
                                                <span className="text-xs px-2 py-0.5 bg-success-500/20 text-success-400 rounded-full">
                                                    Recommended
                                                </span>
                                            )}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-right text-dark-200">
                                        ${(s.cost / 1000).toFixed(0)}K
                                    </td>
                                    <td className="px-6 py-4 text-right text-success-400 font-medium">
                                        {s.risk_reduction?.toFixed(0)}%
                                    </td>
                                    <td className="px-6 py-4 text-right text-dark-200">
                                        {s.timeline_days}d
                                    </td>
                                    <td className="px-6 py-4 text-center">
                                        <span className={`text-xs px-2 py-1 rounded-full ${s.disruption_level === 'None' ? 'bg-dark-600/50 text-dark-300' :
                                                s.disruption_level === 'Low' ? 'bg-success-500/20 text-success-400' :
                                                    s.disruption_level === 'Medium' ? 'bg-warning-500/20 text-warning-400' :
                                                        'bg-danger-500/20 text-danger-400'
                                            }`}>
                                            {s.disruption_level}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-right text-dark-200">{(s.confidence * 100).toFixed(0)}%</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
