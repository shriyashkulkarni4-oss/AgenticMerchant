import React from 'react';
import { Bot, Store, Terminal, Sparkles, ExternalLink } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab }) {
  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <Sparkles className="w-5 h-5 text-slate-950 font-bold" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                AgenticBuy
              </span>
              <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Gemma 2 Brain
              </span>
            </div>
            <p className="text-xs text-slate-400">Autonomous Merchant & Buyer Network</p>
          </div>
        </div>

        <nav className="flex items-center space-x-1 sm:space-x-2 bg-slate-900/90 p-1.5 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab('consumer')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'consumer'
                ? 'bg-emerald-500 text-slate-950 shadow-md font-semibold'
                : 'text-slate-300 hover:text-white hover:bg-slate-800'
            }`}
          >
            <Bot className="w-4 h-4" />
            <span>AgenticBuy Chat</span>
          </button>

          <button
            onClick={() => setActiveTab('merchant')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'merchant'
                ? 'bg-emerald-500 text-slate-950 shadow-md font-semibold'
                : 'text-slate-300 hover:text-white hover:bg-slate-800'
            }`}
          >
            <Store className="w-4 h-4" />
            <span>Merchant Portal</span>
          </button>

          <button
            onClick={() => setActiveTab('api')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'api'
                ? 'bg-emerald-500 text-slate-950 shadow-md font-semibold'
                : 'text-slate-300 hover:text-white hover:bg-slate-800'
            }`}
          >
            <Terminal className="w-4 h-4" />
            <span>LLM API (Claude/GPT)</span>
          </button>
        </nav>

        <div className="hidden md:flex items-center space-x-3 text-xs">
          <a
            href="http://localhost:8080/docs"
            target="_blank"
            rel="noreferrer"
            className="flex items-center space-x-1 text-slate-400 hover:text-emerald-400 transition-colors"
          >
            <span>OpenAPI Docs</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>
    </header>
  );
}
