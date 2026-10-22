import React from 'react';
import { Network, Tag, Layers, Share2 } from 'lucide-react';

export default function KnowledgeGraphViewer({ graphData }) {
  const nodes = graphData?.nodes || [
    { id: '1', label: 'Merchant', properties: { name: 'TechGear Store' } },
    { id: '2', label: 'Category', properties: { name: 'Audio' } },
    { id: '3', label: 'Category', properties: { name: 'Wearables' } },
    { id: '4', label: 'Product', properties: { name: 'Pro Wireless Headphones', price: 149.99 } },
    { id: '5', label: 'Product', properties: { name: 'Noise-Cancelling Earbuds', price: 89.99 } },
    { id: '6', label: 'Product', properties: { name: 'Smart Fitness Tracker', price: 69.99 } },
  ];

  const edges = graphData?.edges || [
    { source: 'TechGear Store', target: 'Audio', type: 'SELLS_CATEGORY' },
    { source: 'TechGear Store', target: 'Wearables', type: 'SELLS_CATEGORY' },
    { source: 'Pro Wireless Headphones', target: 'Audio', type: 'BELONGS_TO' },
    { source: 'Noise-Cancelling Earbuds', target: 'Audio', type: 'BELONGS_TO' },
    { source: 'Smart Fitness Tracker', target: 'Wearables', type: 'BELONGS_TO' },
    { source: 'Pro Wireless Headphones', target: 'Noise-Cancelling Earbuds', type: 'SIMILAR_TO' },
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
        <div className="flex items-center space-x-2">
          <Network className="w-5 h-5 text-emerald-400" />
          <h3 className="font-semibold text-slate-100">Graphify AI Knowledge Graph</h3>
        </div>
        <span className="text-xs bg-emerald-500/10 text-emerald-400 px-2.5 py-1 rounded-full border border-emerald-500/20 font-mono">
          Neo4j + Graphify Synced
        </span>
      </div>

      <p className="text-xs text-slate-400 mb-4">
        Structural entity graph parsed from crawled pages. AI agents traverse these relationships to discover products, find alternatives, and evaluate bargains.
      </p>

      {/* Nodes Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
        <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
          <div className="flex items-center space-x-2 text-xs font-medium text-slate-400 mb-1">
            <Layers className="w-3.5 h-3.5 text-blue-400" />
            <span>Entities (Nodes)</span>
          </div>
          <span className="text-xl font-bold text-slate-100">{nodes.length}</span>
        </div>

        <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
          <div className="flex items-center space-x-2 text-xs font-medium text-slate-400 mb-1">
            <Share2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>Relationships (Edges)</span>
          </div>
          <span className="text-xl font-bold text-slate-100">{edges.length}</span>
        </div>

        <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
          <div className="flex items-center space-x-2 text-xs font-medium text-slate-400 mb-1">
            <Tag className="w-3.5 h-3.5 text-purple-400" />
            <span>Agent Traversal Type</span>
          </div>
          <span className="text-sm font-semibold text-purple-300">Deterministic AST + Graph</span>
        </div>
      </div>

      {/* Visual representation card */}
      <div className="bg-slate-950 rounded-xl p-4 border border-slate-800/70 overflow-hidden">
        <div className="text-xs font-medium text-slate-400 mb-2">Graph Relationships:</div>
        <div className="space-y-2 max-h-48 overflow-y-auto pr-2">
          {edges.map((edge, idx) => (
            <div
              key={idx}
              className="flex items-center text-xs bg-slate-900/80 px-3 py-2 rounded-lg border border-slate-800/60 text-slate-300"
            >
              <span className="font-semibold text-emerald-400 truncate max-w-[140px]">
                {edge.source}
              </span>
              <span className="mx-2 text-slate-500 font-mono">──[{edge.type}]──▶</span>
              <span className="text-blue-300 truncate max-w-[140px]">{edge.target}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
