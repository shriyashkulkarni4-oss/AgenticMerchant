import React, { useState, useEffect } from 'react';
import {
  Network,
  Layers,
  Share2,
  Tag,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Store,
  Package,
  FolderTree,
  DollarSign,
  Info,
  CheckCircle2,
  RefreshCw
} from 'lucide-react';

export default function FullGraphVisualizer({ merchantData, products = [] }) {
  const [zoom, setZoom] = useState(1);
  const [selectedNode, setSelectedNode] = useState(null);
  const [filterType, setFilterType] = useState('all'); // all, products, categories
  const [liveGraphData, setLiveGraphData] = useState(null);

  useEffect(() => {
    fetch('/api/v1/graph/mine')
      .then((res) => res.json())
      .then((data) => {
        if (data && data.nodes && data.nodes.length > 0) {
          setLiveGraphData(data);
        }
      })
      .catch((err) => console.warn("Could not fetch remote graph:", err));
  }, [products]);

  const storeName = liveGraphData?.store_name || merchantData?.business_name || 'TechGear Store';

  // Build nodes and edges based on merchant products
  const categorySet = new Set(products.map((p) => p.category || 'General'));
  const categories = Array.from(categorySet);

  // Layout coordinates for whole graph representation
  // Center: Store node (cx=400, cy=280)
  // Circle 1: Category nodes around store
  // Circle 2: Product nodes around corresponding categories
  const centerX = 440;
  const centerY = 300;

  const categoryPositions = {};
  categories.forEach((cat, idx) => {
    const angle = (idx / (categories.length || 1)) * 2 * Math.PI - Math.PI / 2;
    categoryPositions[cat] = {
      x: centerX + Math.cos(angle) * 160,
      y: centerY + Math.sin(angle) * 140,
    };
  });

  const productNodes = products.map((p, idx) => {
    const catPos = categoryPositions[p.category || 'General'] || { x: centerX + 150, y: centerY };
    // Distribute products around category
    const countInCat = products.filter((item) => (item.category || 'General') === (p.category || 'General')).length;
    const catProds = products.filter((item) => (item.category || 'General') === (p.category || 'General'));
    const prodIdx = catProds.findIndex((item) => item.id === p.id);

    const offsetAngle = ((prodIdx - (countInCat - 1) / 2) * 0.7) || (idx * 0.5);
    const dist = 130;

    return {
      id: p.id,
      name: p.name,
      type: 'product',
      price: p.price,
      auto_accept_threshold: p.auto_accept_threshold,
      min_acceptable_price: p.min_acceptable_price,
      stock_quantity: p.stock_quantity,
      bargaining_enabled: p.bargaining_enabled,
      category: p.category || 'General',
      x: catPos.x + Math.cos(offsetAngle) * dist,
      y: catPos.y + Math.sin(offsetAngle) * dist,
    };
  });

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-semibold mb-2 border border-emerald-500/20">
            <Network className="w-3.5 h-3.5" />
            <span>Graphify Deterministic Knowledge Graph</span>
          </div>
          <h2 className="text-xl font-bold text-white tracking-tight">
            Visual Entity & Relationship Graph
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Complete interconnected view of your store, categories, and products as traversed by AI agents. Click any node to inspect parameters.
          </p>
        </div>

        {/* Graph Controls */}
        <div className="flex items-center space-x-2 bg-slate-950 p-1.5 rounded-xl border border-slate-800">
          <button
            onClick={() => setZoom((z) => Math.min(z + 0.15, 1.6))}
            className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={() => setZoom((z) => Math.max(z - 0.15, 0.6))}
            className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <button
            onClick={() => setZoom(1)}
            className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white transition-colors"
            title="Reset Zoom"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Canvas Area & Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* SVG Canvas Area */}
        <div className="lg:col-span-3 bg-slate-950 border border-slate-800 rounded-2xl relative overflow-hidden h-[620px] shadow-2xl flex items-center justify-center">
          {/* Legend */}
          <div className="absolute top-4 left-4 z-10 bg-slate-900/90 backdrop-blur-md border border-slate-800 p-3 rounded-xl text-xs space-y-1.5 shadow-lg">
            <span className="font-semibold text-slate-300 block mb-1">Entity Legend</span>
            <div className="flex items-center space-x-2">
              <span className="w-3 h-3 rounded-full bg-emerald-500 ring-2 ring-emerald-500/30"></span>
              <span className="text-slate-400">Merchant Node</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="w-3 h-3 rounded-md bg-purple-500 ring-2 ring-purple-500/30"></span>
              <span className="text-slate-400">Category Nodes</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="w-3 h-3 rounded-full bg-blue-500 ring-2 ring-blue-500/30"></span>
              <span className="text-slate-400">Product Nodes</span>
            </div>
          </div>

          <svg
            viewBox="0 0 880 600"
            className="w-full h-full transition-transform duration-200 cursor-grab active:cursor-grabbing"
            style={{ transform: `scale(${zoom})` }}
          >
            <defs>
              <linearGradient id="edgeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#10b981" stopOpacity="0.4" />
                <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.3" />
              </linearGradient>
              <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="4" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>

            {/* Edges from Center Store to Categories */}
            {categories.map((cat, idx) => {
              const pos = categoryPositions[cat];
              return (
                <g key={`edge-cat-${idx}`}>
                  <line
                    x1={centerX}
                    y1={centerY}
                    x2={pos.x}
                    y2={pos.y}
                    stroke="#334155"
                    strokeWidth="2.5"
                    strokeDasharray="4 4"
                  />
                  <text
                    x={(centerX + pos.x) / 2}
                    y={(centerY + pos.y) / 2 - 6}
                    fill="#64748b"
                    fontSize="9"
                    textAnchor="middle"
                    className="font-mono select-none"
                  >
                    SELLS
                  </text>
                </g>
              );
            })}

            {/* Edges from Categories to Products */}
            {productNodes.map((p, idx) => {
              const catPos = categoryPositions[p.category] || { x: centerX, y: centerY };
              return (
                <g key={`edge-prod-${idx}`}>
                  <line
                    x1={catPos.x}
                    y1={catPos.y}
                    x2={p.x}
                    y2={p.y}
                    stroke="url(#edgeGrad)"
                    strokeWidth="2"
                  />
                  <text
                    x={(catPos.x + p.x) / 2}
                    y={(catPos.y + p.y) / 2 - 5}
                    fill="#475569"
                    fontSize="8"
                    textAnchor="middle"
                    className="font-mono select-none"
                  >
                    BELONGS_TO
                  </text>
                </g>
              );
            })}

            {/* Center Store Node */}
            <g
              transform={`translate(${centerX}, ${centerY})`}
              className="cursor-pointer"
              onClick={() =>
                setSelectedNode({
                  type: 'merchant',
                  name: storeName,
                  categoriesCount: categories.length,
                  productsCount: products.length,
                })
              }
            >
              <circle r="46" fill="#064e3b" stroke="#10b981" strokeWidth="3" filter="url(#glow)" />
              <circle r="36" fill="#022c22" />
              <text y="-8" fill="#10b981" fontSize="11" fontWeight="bold" textAnchor="middle">
                STORE
              </text>
              <text y="10" fill="#ffffff" fontSize="10" fontWeight="600" textAnchor="middle">
                {storeName.length > 13 ? storeName.slice(0, 11) + '..' : storeName}
              </text>
            </g>

            {/* Category Nodes */}
            {categories.map((cat, idx) => {
              const pos = categoryPositions[cat];
              return (
                <g
                  key={`cat-node-${idx}`}
                  transform={`translate(${pos.x}, ${pos.y})`}
                  className="cursor-pointer"
                  onClick={() =>
                    setSelectedNode({
                      type: 'category',
                      name: cat,
                      productsCount: products.filter((item) => (item.category || 'General') === cat).length,
                    })
                  }
                >
                  <rect
                    x="-42"
                    y="-24"
                    width="84"
                    height="48"
                    rx="12"
                    fill="#3b0764"
                    stroke="#a855f7"
                    strokeWidth="2"
                    filter="url(#glow)"
                  />
                  <text y="4" fill="#f3e8ff" fontSize="10" fontWeight="600" textAnchor="middle">
                    {cat.length > 12 ? cat.slice(0, 10) + '..' : cat}
                  </text>
                </g>
              );
            })}

            {/* Product Nodes */}
            {productNodes.map((p, idx) => (
              <g
                key={`prod-node-${idx}`}
                transform={`translate(${p.x}, ${p.y})`}
                className="cursor-pointer group"
                onClick={() => setSelectedNode(p)}
              >
                <circle
                  r="32"
                  fill={p.bargaining_enabled ? '#0c4a6e' : '#1e293b'}
                  stroke={p.bargaining_enabled ? '#0284c7' : '#64748b'}
                  strokeWidth="2.5"
                  className="group-hover:stroke-emerald-400 transition-colors"
                />
                <text y="-6" fill="#ffffff" fontSize="8.5" fontWeight="600" textAnchor="middle">
                  {p.name.length > 11 ? p.name.slice(0, 9) + '..' : p.name}
                </text>
                <text y="10" fill="#38bdf8" fontSize="10" fontWeight="bold" textAnchor="middle">
                  ${p.price}
                </text>
                {p.bargaining_enabled && (
                  <circle cx="20" cy="-20" r="5" fill="#10b981" />
                )}
              </g>
            ))}
          </svg>
        </div>

        {/* Node Inspector Panel */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col justify-between h-[620px]">
          <div>
            <div className="flex items-center space-x-2 pb-3 border-b border-slate-800 mb-4">
              <Info className="w-4 h-4 text-emerald-400" />
              <h3 className="font-semibold text-white text-sm">Node Inspector</h3>
            </div>

            {selectedNode ? (
              <div className="space-y-4">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-800 text-emerald-400">
                    {selectedNode.type} Entity
                  </span>
                  <h4 className="text-base font-bold text-white mt-2">{selectedNode.name}</h4>
                </div>

                {selectedNode.type === 'product' && (
                  <div className="space-y-2 text-xs">
                    <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 flex justify-between">
                      <span className="text-slate-400">Listed Price:</span>
                      <span className="font-bold text-white">${selectedNode.price}</span>
                    </div>

                    <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 flex justify-between">
                      <span className="text-emerald-400">Directly Agreeable:</span>
                      <span className="font-bold text-emerald-400">${selectedNode.auto_accept_threshold || selectedNode.price}</span>
                    </div>

                    <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 flex justify-between">
                      <span className="text-rose-400">Floor Minimum:</span>
                      <span className="font-bold text-rose-400">${selectedNode.min_acceptable_price || selectedNode.price}</span>
                    </div>

                    <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 flex justify-between">
                      <span className="text-slate-400">Stock Available:</span>
                      <span className="font-bold text-slate-200">{selectedNode.stock_quantity || 10} units</span>
                    </div>

                    <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 flex justify-between">
                      <span className="text-slate-400">AI Bargaining:</span>
                      <span className={`font-semibold ${selectedNode.bargaining_enabled ? 'text-emerald-400' : 'text-slate-500'}`}>
                        {selectedNode.bargaining_enabled ? 'Open for Offers' : 'Firm Price'}
                      </span>
                    </div>
                  </div>
                )}

                {selectedNode.type === 'category' && (
                  <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 text-xs text-slate-300">
                    <p>Total Products in this Category: <strong className="text-white">{selectedNode.productsCount}</strong></p>
                    <p className="mt-2 text-slate-400">Agents traverse this node when shoppers ask for product alternatives or category queries.</p>
                  </div>
                )}

                {selectedNode.type === 'merchant' && (
                  <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 text-xs text-slate-300 space-y-2">
                    <p>Root Store Node for AI agents.</p>
                    <p>Categories: <strong className="text-emerald-400">{selectedNode.categoriesCount}</strong></p>
                    <p>Catalog Size: <strong className="text-emerald-400">{selectedNode.productsCount} items</strong></p>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-16 text-slate-500 text-xs space-y-2">
                <Network className="w-8 h-8 mx-auto text-slate-600" />
                <p>Click any node on the graph canvas to inspect its details and AI negotiation boundaries.</p>
              </div>
            )}
          </div>

          <div className="p-3 bg-slate-950/70 rounded-xl border border-slate-800/80 text-[11px] text-slate-400">
            💡 AI Agents query this deterministic graph structure to discover products before bargaining.
          </div>
        </div>
      </div>
    </div>
  );
}
