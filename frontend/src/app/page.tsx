'use client';

import { useState } from 'react';
import {
    Shield, Target, TrendingUp, AlertTriangle,
    Clock, DollarSign, Users, ChevronRight,
    Activity, Layers, Brain
} from 'lucide-react';
import Dashboard from '@/components/Dashboard';
import DecisionBrief from '@/components/DecisionBrief';
import Scenarios from '@/components/Scenarios';
import HorizonPlanner from '@/components/HorizonPlanner';

export default function Home() {
    const [activeTab, setActiveTab] = useState<'dashboard' | 'brief' | 'scenarios' | 'horizons'>('dashboard');
    const [riskScore, setRiskScore] = useState(72);

    const getRiskColor = (score: number) => {
        if (score >= 75) return 'text-danger-500';
        if (score >= 50) return 'text-warning-500';
        return 'text-success-500';
    };

    const getRiskLabel = (score: number) => {
        if (score >= 75) return 'Critical';
        if (score >= 50) return 'Elevated';
        return 'Normal';
    };

    return (
        <main className="min-h-screen bg-dark-950">
            {/* Header */}
            <header className="border-b border-dark-800 bg-dark-900/50 backdrop-blur-xl sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center shadow-glow">
                                <Shield className="w-6 h-6 text-white" />
                            </div>
                            <div>
                                <h1 className="text-xl font-bold text-white">RiskAdvisor</h1>
                                <p className="text-sm text-dark-400">Enterprise Decision Intelligence</p>
                            </div>
                        </div>

                        {/* Risk Score Badge */}
                        <div className="flex items-center gap-6">
                            <div className="flex items-center gap-3 px-4 py-2 card">
                                <div className="relative">
                                    <div className={`w-3 h-3 rounded-full ${riskScore >= 75 ? 'bg-danger-500' : riskScore >= 50 ? 'bg-warning-500' : 'bg-success-500'}`} />
                                    <div className={`absolute inset-0 w-3 h-3 rounded-full ${riskScore >= 75 ? 'bg-danger-500' : riskScore >= 50 ? 'bg-warning-500' : 'bg-success-500'} pulse-ring`} />
                                </div>
                                <span className="text-sm text-dark-300">Risk Score</span>
                                <span className={`text-2xl font-bold ${getRiskColor(riskScore)}`}>{riskScore}</span>
                                <span className={`text-sm ${getRiskColor(riskScore)}`}>{getRiskLabel(riskScore)}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            {/* Navigation */}
            <nav className="border-b border-dark-800 bg-dark-900/30">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="flex gap-1">
                        {[
                            { id: 'dashboard', label: 'Dashboard', icon: Activity },
                            { id: 'brief', label: 'Decision Brief', icon: Brain },
                            { id: 'scenarios', label: 'Scenarios', icon: Target },
                            { id: 'horizons', label: 'Multi-Horizon', icon: Layers },
                        ].map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id as any)}
                                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-all
                  ${activeTab === tab.id
                                        ? 'text-primary-400 border-b-2 border-primary-400'
                                        : 'text-dark-400 hover:text-dark-200'
                                    }`}
                            >
                                <tab.icon className="w-4 h-4" />
                                {tab.label}
                            </button>
                        ))}
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <div className="max-w-7xl mx-auto px-6 py-8">
                {activeTab === 'dashboard' && <Dashboard riskScore={riskScore} />}
                {activeTab === 'brief' && <DecisionBrief riskScore={riskScore} />}
                {activeTab === 'scenarios' && <Scenarios riskScore={riskScore} />}
                {activeTab === 'horizons' && <HorizonPlanner riskScore={riskScore} />}
            </div>

            {/* Footer */}
            <footer className="border-t border-dark-800 py-6 mt-12">
                <div className="max-w-7xl mx-auto px-6 text-center text-dark-500 text-sm">
                    RiskAdvisor v4.0 • Enterprise Decision Intelligence Platform • © 2026 Umang Kumar
                </div>
            </footer>
        </main>
    );
}
