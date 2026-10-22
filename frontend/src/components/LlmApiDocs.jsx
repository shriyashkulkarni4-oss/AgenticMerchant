import React, { useState } from 'react';
import { Terminal, Copy, Check, Sparkles, Code2, Globe } from 'lucide-react';

export default function LlmApiDocs() {
  const [copiedSection, setCopiedSection] = useState(null);

  const copyToClipboard = (text, section) => {
    navigator.clipboard.writeText(text);
    setCopiedSection(section);
    setTimeout(() => setCopiedSection(null), 2000);
  };

  const claudeToolDefinition = `{
  "tools": [
    {
      "name": "agenticbuy_search_products",
      "description": "Search onboarded merchants and products on AgenticBuy. Traverses Graphify knowledge graph and embeddings.",
      "input_schema": {
        "type": "object",
        "properties": {
          "query": { "type": "string", "description": "Product search query" },
          "category": { "type": "string", "description": "Optional category filter" },
          "max_price": { "type": "number", "description": "Maximum price in USD" }
        },
        "required": ["query"]
      }
    },
    {
      "name": "agenticbuy_negotiate_price",
      "description": "Start or counter a price negotiation with a merchant within their preconfigured auto-accept and floor thresholds.",
      "input_schema": {
        "type": "object",
        "properties": {
          "product_id": { "type": "string", "description": "UUID of the product" },
          "offered_price": { "type": "number", "description": "User's price offer" },
          "message": { "type": "string", "description": "Negotiation opening note" }
        },
        "required": ["product_id", "offered_price"]
      }
    },
    {
      "name": "agenticbuy_place_order",
      "description": "Complete payment and place an order on behalf of the user using an agreed negotiated price session or listed price.",
      "input_schema": {
        "type": "object",
        "properties": {
          "product_id": { "type": "string", "description": "UUID of the product" },
          "quantity": { "type": "integer", "default": 1 },
          "negotiation_session_id": { "type": "string", "description": "Accepted negotiation session UUID" }
        },
        "required": ["product_id"]
      }
    }
  ]
}`;

  const sampleCurl = `# 1. Search products across all merchants
curl -X GET "http://localhost:8080/api/v1/products/?search=headphones"

# 2. Negotiate price with merchant's AI rules
curl -X POST "http://localhost:8080/api/v1/negotiate/" \\
  -H "Content-Type: application/json" \\
  -d '{"product_id": "UUID-HERE", "offered_price": 125.0}'

# 3. Complete purchase & place order
curl -X POST "http://localhost:8080/api/v1/orders/" \\
  -H "Content-Type: application/json" \\
  -d '{"product_id": "UUID-HERE", "quantity": 1, "negotiation_session_id": "SESSION-UUID"}'`;

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Banner */}
      <div className="bg-gradient-to-r from-blue-950/60 via-slate-900 to-slate-900 border border-blue-500/30 rounded-2xl p-6 sm:p-8">
        <div className="max-w-3xl">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 text-xs font-semibold mb-3 border border-blue-500/20">
            <Terminal className="w-3.5 h-3.5" />
            <span>Single Unified Agentic API</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            One Single API for Claude, GPT, and Autonomous Agents
          </h1>
          <p className="mt-2 text-slate-300 text-sm leading-relaxed">
            Connect Claude or any LLM agent directly to AgenticBuy. The model discovers merchants, traverses the Graphify knowledge graph, bargains within merchant-configured thresholds, and executes final purchases for the consumer.
          </p>
        </div>
      </div>

      {/* Endpoints Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800">
          <h3 className="font-semibold text-white text-sm">Core REST Endpoints for AI Agents</h3>
        </div>

        <div className="divide-y divide-slate-800 text-xs font-mono">
          <div className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div className="flex items-center space-x-3">
              <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 font-bold">GET</span>
              <span className="text-slate-200">/api/v1/merchants</span>
            </div>
            <span className="text-slate-400 font-sans">List all onboarded merchants and their catalog metadata</span>
          </div>

          <div className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div className="flex items-center space-x-3">
              <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 font-bold">GET</span>
              <span className="text-slate-200">/api/v1/products</span>
            </div>
            <span className="text-slate-400 font-sans">Search and filter products (category, price, search query)</span>
          </div>

          <div className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div className="flex items-center space-x-3">
              <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold">POST</span>
              <span className="text-slate-200">/api/v1/graph/query</span>
            </div>
            <span className="text-slate-400 font-sans">Query Graphify knowledge graph for relationships & alternatives</span>
          </div>

          <div className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div className="flex items-center space-x-3">
              <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold">POST</span>
              <span className="text-slate-200">/api/v1/negotiate</span>
            </div>
            <span className="text-slate-400 font-sans">Initiate or advance price bargaining with merchant rules</span>
          </div>

          <div className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div className="flex items-center space-x-3">
              <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold">POST</span>
              <span className="text-slate-200">/api/v1/orders</span>
            </div>
            <span className="text-slate-400 font-sans">Execute user checkout / order with agreed price</span>
          </div>
        </div>
      </div>

      {/* Claude Tool Schema Snippet */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Code2 className="w-5 h-5 text-emerald-400" />
            <h3 className="font-semibold text-white text-sm">Anthropic Claude / Agent Tool Schema</h3>
          </div>
          <button
            onClick={() => copyToClipboard(claudeToolDefinition, 'claude')}
            className="flex items-center space-x-1.5 text-xs text-slate-300 hover:text-white bg-slate-800 px-3 py-1.5 rounded-lg transition-colors"
          >
            {copiedSection === 'claude' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copiedSection === 'claude' ? 'Copied!' : 'Copy Tool Spec'}</span>
          </button>
        </div>
        <p className="text-xs text-slate-400">
          Provide this tool definition directly to Claude (e.g. Anthropic API or Claude Code). Claude will autonomously invoke AgenticBuy to discover products, negotiate with merchants, and place orders.
        </p>
        <pre className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-emerald-300 overflow-x-auto max-h-72">
          {claudeToolDefinition}
        </pre>
      </div>

      {/* cURL Example */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Terminal className="w-5 h-5 text-blue-400" />
            <h3 className="font-semibold text-white text-sm">cURL / CLI Agent Execution Flow</h3>
          </div>
          <button
            onClick={() => copyToClipboard(sampleCurl, 'curl')}
            className="flex items-center space-x-1.5 text-xs text-slate-300 hover:text-white bg-slate-800 px-3 py-1.5 rounded-lg transition-colors"
          >
            {copiedSection === 'curl' ? <Check className="w-3.5 h-3.5 text-blue-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copiedSection === 'curl' ? 'Copied!' : 'Copy cURL'}</span>
          </button>
        </div>
        <pre className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-slate-300 overflow-x-auto">
          {sampleCurl}
        </pre>
      </div>
    </div>
  );
}
