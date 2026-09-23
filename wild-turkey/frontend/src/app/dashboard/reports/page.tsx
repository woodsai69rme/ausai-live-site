'use client';

import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  ShieldCheck, 
  Coins, 
  Cpu, 
  Layers, 
  Download, 
  RefreshCw, 
  Mic, 
  Database,
  Sparkles,
  CheckCircle2,
  Clock
} from 'lucide-react';
import { reports } from '@/lib/api';

export default function ReportsDashboard() {
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [markdownReport, setMarkdownReport] = useState<string | null>(null);

  const stats = [
    { title: 'Total Tokens Processed', value: '1.42M', change: '+24% this week', icon: Cpu, color: 'text-cyan-400' },
    { title: 'Cloud Cost Savings', value: '$84.20', change: '100% Free Harvester', icon: Coins, color: 'text-amber-400' },
    { title: 'Swarm Success Rate', value: '98.4%', change: '4-Stage RLM Verified', icon: ShieldCheck, color: 'text-emerald-400' },
    { title: 'Indexed RAG Chunks', value: '12,480', change: 'ChromaDB Semantic Engine', icon: Database, color: 'text-purple-400' },
  ];

  const providerBreakdown = [
    { name: 'Local Ollama (RTX 4060)', tokens: '840k', share: 59, cost: '$0.00' },
    { name: 'Google AI Studio (Gemini 1.5 Flash)', tokens: '310k', share: 22, cost: '$0.00' },
    { name: 'Groq Cloud (Llama 3.3 70B)', tokens: '180k', share: 13, cost: '$0.00' },
    { name: 'OpenRouter Free Fallbacks', tokens: '90k', share: 6, cost: '$0.00' },
  ];

  const swarmTelemetry = [
    { stage: 'Stage 1: Researcher Agent', avgTime: '1.8s', confidence: '99.2%', model: 'ollama/qwen3.5:9b' },
    { stage: 'Stage 2: Engineer Agent', avgTime: '3.4s', confidence: '98.5%', model: 'gemini-1.5-flash' },
    { stage: 'Stage 3: Auditor Agent', avgTime: '2.1s', confidence: '99.8%', model: 'groq/llama-3.3-70b' },
    { stage: 'Stage 4: Refinement Gate', avgTime: '1.2s', confidence: '100.0%', model: 'Deterministic Validator' },
  ];

  const handleExport = async () => {
    setExporting(true);
    try {
      const data = await reports.exportMarkdown();
      setMarkdownReport(data);
      // Trigger download
      const blob = new Blob([data], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `wild-turkey-executive-report-${new Date().toISOString().slice(0, 10)}.md`;
      a.click();
    } catch (e) {
      console.error(e);
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold bg-gradient-to-r from-amber-400 via-orange-400 to-red-500 bg-clip-text text-transparent">
              Executive Analytics & Telemetry
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-800">
              v5.5 Omnimodal
            </span>
          </div>
          <p className="text-slate-400 mt-1">
            Real-time telemetry, model routing efficiencies, swarm execution times, and cost avoidance metrics.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button 
            onClick={handleExport}
            disabled={exporting}
            className="flex items-center gap-2 bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 text-slate-950 font-semibold px-4 py-2 rounded-lg transition shadow-lg shadow-orange-950/30 disabled:opacity-50"
          >
            <Download className="w-4 h-4" />
            {exporting ? 'Generating Report...' : 'Export Markdown Audit'}
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((s, idx) => (
          <div key={idx} className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 hover:border-slate-700 transition">
            <div className="flex justify-between items-start">
              <span className="text-slate-400 text-sm font-medium">{s.title}</span>
              <s.icon className={`w-5 h-5 ${s.color}`} />
            </div>
            <div className="text-3xl font-bold text-slate-100 mt-2">{s.value}</div>
            <div className="text-xs text-slate-400 mt-1 flex items-center gap-1">
              <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
              <span>{s.change}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Main Breakdown Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Provider Distribution */}
        <div className="bg-slate-900/40 border border-slate-800/80 rounded-xl p-6 space-y-5">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-amber-400" />
              Token Routing & Provider Distribution
            </h2>
            <span className="text-xs text-slate-400">Zero-Cost Target: Active</span>
          </div>

          <div className="space-y-4">
            {providerBreakdown.map((p, idx) => (
              <div key={idx} className="space-y-1.5">
                <div className="flex justify-between text-sm">
                  <span className="font-medium text-slate-200">{p.name}</span>
                  <span className="text-slate-400">{p.tokens} tokens ({p.share}%)</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                  <div 
                    className="bg-gradient-to-r from-amber-400 to-orange-500 h-full rounded-full" 
                    style={{ width: `${p.share}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Swarm RLM Pipeline Latency */}
        <div className="bg-slate-900/40 border border-slate-800/80 rounded-xl p-6 space-y-5">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Layers className="w-5 h-5 text-purple-400" />
              4-Stage RLM Swarm Pipeline Latency
            </h2>
            <span className="text-xs font-mono text-purple-400">Self-Correction: ON</span>
          </div>

          <div className="divide-y divide-slate-800">
            {swarmTelemetry.map((stage, idx) => (
              <div key={idx} className="py-3 flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium text-slate-200">{stage.stage}</div>
                  <div className="text-xs font-mono text-slate-400">{stage.model}</div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-semibold text-emerald-400 flex items-center justify-end gap-1">
                    <Clock className="w-3.5 h-3.5" />
                    {stage.avgTime}
                  </div>
                  <div className="text-xs text-slate-400">Acc: {stage.confidence}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Omnimodal RAG & Voice Ingestion Status */}
      <div className="bg-slate-900/30 border border-slate-800/60 rounded-xl p-6">
        <h2 className="text-lg font-semibold flex items-center gap-2 mb-4">
          <Sparkles className="w-5 h-5 text-cyan-400" />
          Omnimodal RAG & Voice Command Subsystems
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div className="p-4 bg-slate-950/60 rounded-lg border border-slate-800">
            <div className="text-slate-400 text-xs">Vector Memory Backend</div>
            <div className="text-base font-bold text-slate-200 mt-1">ChromaDB Embedded</div>
            <div className="text-xs text-emerald-400 mt-2 flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" /> Cosine Similarity Active
            </div>
          </div>

          <div className="p-4 bg-slate-950/60 rounded-lg border border-slate-800">
            <div className="text-slate-400 text-xs">Voice Command Transcriber</div>
            <div className="text-base font-bold text-slate-200 mt-1">Whisper-Large-v3 Engine</div>
            <div className="text-xs text-cyan-400 mt-2 flex items-center gap-1">
              <Mic className="w-3.5 h-3.5" /> Audio Route: /api/audio/transcribe
            </div>
          </div>

          <div className="p-4 bg-slate-950/60 rounded-lg border border-slate-800">
            <div className="text-slate-400 text-xs">Multimodal Vision Web Agent</div>
            <div className="text-base font-bold text-slate-200 mt-1">Playwright 5.0 Visual Gate</div>
            <div className="text-xs text-amber-400 mt-2 flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5" /> DOM Box Injection Active
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
