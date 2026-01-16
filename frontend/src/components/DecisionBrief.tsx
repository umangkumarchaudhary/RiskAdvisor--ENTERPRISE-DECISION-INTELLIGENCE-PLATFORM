'use client';

import { useState, useEffect } from 'react';
import {
    FileText, Users, Building2, DollarSign,
    Clock, TrendingUp, ChevronRight, Shield,
    Download, Send, Loader2, AlertTriangle
} from 'lucide-react';
import { getSampleStrategies, getDecisionPackage, Strategy } from '@/lib/api';

interface DecisionBriefProps {
    riskScore: number;
}

export default function DecisionBrief({ riskScore }: DecisionBriefProps) {
    const [selectedStakeholder, setSelectedStakeholder] = useState<string>('CEO');
    const [strategies, setStrategies] = useState<Strategy[]>([]);
    const [decisionPackage, setDecisionPackage] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadData();
    }, [riskScore]);

    const loadData = async () => {
        try {
            setLoading(true);
            setError(null);

            // Get strategies
            const strats = await getSampleStrategies();
            setStrategies(strats);

            // Get decision package
            const pkg = await getDecisionPackage({
                strategies: strats,
                budget: 500000,
                risk_score: riskScore,
                context: {
                    available_budget: 500000,
                    active_initiatives: 2,
                    leadership_support_score: 75
                }
            });

            setDecisionPackage(pkg);
        } catch (err: any) {
            setError('Failed to generate decision package');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const stakeholders = [
        { id: 'CEO', label: 'CEO', icon: Building2 },
        { id: 'CFO', label: 'CFO', icon: DollarSign },
        { id: 'COO', label: 'COO', icon: Clock },
    ];

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
                <span className="ml-3 text-dark-400">Generating decision package...</span>
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

    const currentBrief = decisionPackage?.stakeholder_briefs?.[selectedStakeholder];

    return (
        <div className="space-y-8 animate-fade-in">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-white">Executive Decision Brief</h2>
                    <p className="text-dark-400 mt-1">
                        {decisionPackage?.title || 'Tailored communication for each stakeholder'}
                    </p>
                </div>
                <div className="flex gap-3">
                    <button className="btn-secondary flex items-center gap-2">
                        <Download className="w-4 h-4" />
                        Export PDF
                    </button>
                    <button className="btn-primary flex items-center gap-2">
                        <Send className="w-4 h-4" />
                        Send to All
                    </button>
                </div>
            </div>

            {/* Stakeholder Selector */}
            <div className="flex gap-4">
                {stakeholders.map((s) => (
                    <button
                        key={s.id}
                        onClick={() => setSelectedStakeholder(s.id)}
                        className={`flex items-center gap-3 px-6 py-4 rounded-xl border transition-all
              ${selectedStakeholder === s.id
                                ? 'bg-primary-500/20 border-primary-500/50 text-white'
                                : 'bg-dark-800/30 border-dark-700/50 text-dark-400 hover:border-dark-600'
                            }`}
                    >
                        <s.icon className="w-5 h-5" />
                        <span className="font-medium">{s.label}</span>
                    </button>
                ))}
            </div>

            {/* Brief Content */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main Brief */}
                <div className="lg:col-span-2 card p-8">
                    <div className="flex items-start gap-4 mb-6">
                        <div className="w-12 h-12 rounded-xl bg-primary-500/20 flex items-center justify-center">
                            <FileText className="w-6 h-6 text-primary-400" />
                        </div>
                        <div>
                            <p className="text-sm text-dark-400">To: {selectedStakeholder}</p>
                            <h3 className="text-xl font-semibold text-white mt-1">
                                {currentBrief?.subject_line || 'Safety Investment Decision'}
                            </h3>
                        </div>
                    </div>

                    <div className="space-y-6">
                        <div>
                            <h4 className="text-sm font-semibold text-dark-300 uppercase tracking-wider mb-4">Key Points</h4>
                            <ul className="space-y-3">
                                {(currentBrief?.key_points || []).map((point: string, index: number) => (
                                    <li key={index} className="flex items-start gap-3">
                                        <ChevronRight className="w-5 h-5 text-primary-400 flex-shrink-0 mt-0.5" />
                                        <span className="text-dark-200">{point}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>

                        <div className="p-4 bg-success-500/10 border border-success-500/30 rounded-xl">
                            <p className="text-sm text-success-400 font-medium">Recommended Action</p>
                            <p className="text-white mt-1">{currentBrief?.recommended_action || 'Approve recommended portfolio'}</p>
                        </div>
                    </div>
                </div>

                {/* Metrics Sidebar */}
                <div className="space-y-6">
                    <div className="card p-6">
                        <h4 className="text-sm font-semibold text-dark-300 uppercase tracking-wider mb-4">
                            Key Metrics
                        </h4>
                        <div className="space-y-4">
                            {currentBrief?.metrics && Object.entries(currentBrief.metrics).map(([key, value]) => (
                                <div key={key} className="flex justify-between items-center">
                                    <span className="text-dark-400">{key}</span>
                                    <span className="text-xl font-bold gradient-text">{value as string}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="card p-6">
                        <h4 className="text-sm font-semibold text-dark-300 uppercase tracking-wider mb-4">
                            Decision Deadline
                        </h4>
                        <div className="text-center py-4">
                            <p className={`text-2xl font-bold ${riskScore >= 75 ? 'text-danger-500' : 'text-warning-500'}`}>
                                {decisionPackage?.decision_deadline || (riskScore >= 75 ? 'TODAY' : 'This Week')}
                            </p>
                            <p className="text-sm text-dark-400 mt-2">
                                Risk score: {riskScore}/100
                            </p>
                        </div>
                    </div>

                    <div className="card p-6">
                        <h4 className="text-sm font-semibold text-dark-300 uppercase tracking-wider mb-4">
                            Robustness
                        </h4>
                        <div className="text-center">
                            <p className="text-3xl font-bold gradient-text">
                                {decisionPackage?.robustness?.score?.toFixed(0) || 'N/A'}
                            </p>
                            <p className="text-dark-400">Grade: {decisionPackage?.robustness?.rating || 'N/A'}</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
