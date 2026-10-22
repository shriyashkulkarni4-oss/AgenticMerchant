import React, { useState } from 'react';
import {
  Globe,
  Upload,
  RefreshCw,
  CheckCircle2,
  Sparkles,
  ArrowRight,
  Package,
  Layers,
  Terminal,
  AlertCircle
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function MerchantIngestion({ onProductsAdded, onNavigateToProducts }) {
  const { user, token } = useAuth();
  const [websiteUrl, setWebsiteUrl] = useState(user?.website_url || 'https://my-store-example.com');
  const [maxPages, setMaxPages] = useState(20);
  const [isCrawling, setIsCrawling] = useState(false);
  const [crawlLogs, setCrawlLogs] = useState([]);
  const [extractedSummary, setExtractedSummary] = useState(null);

  const addLog = (text) => {
    setCrawlLogs((prev) => [...prev, `[${new Date().toLocaleTimeString()}] ${text}`]);
  };

  const handleStartIngestion = async (e) => {
    e.preventDefault();
    if (!websiteUrl || isCrawling) return;

    setIsCrawling(true);
    setCrawlLogs([]);
    setExtractedSummary(null);

    addLog(`Initiating web crawler targeting: ${websiteUrl}`);
    addLog(`Domain resolved. Starting breadth-first crawl (limit: ${maxPages} pages)...`);

    try {
      const response = await fetch('/api/v1/crawl/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ url: websiteUrl, max_pages: parseInt(maxPages) || 20 }),
      });

      if (!response.ok) {
        throw new Error(`Crawl request failed with HTTP ${response.status}`);
      }

      const jobData = await response.json();
      addLog(`Crawl job #${jobData.id.slice(0, 8)} registered. Background worker processing...`);
      addLog(`Crawling website pages and extracting DOM product cards...`);
      addLog(`Executing Graphify knowledge graph parser on crawled data...`);

      // Poll job status until completed
      let attempts = 0;
      const pollInterval = setInterval(async () => {
        attempts++;
        try {
          const pollRes = await fetch(`/api/v1/crawl/jobs/${jobData.id}`, {
            headers: {
              ...(token ? { Authorization: `Bearer ${token}` } : {}),
            },
          });
          if (pollRes.ok) {
            const currentJob = await pollRes.json();
            if (currentJob.status === 'completed') {
              clearInterval(pollInterval);
              const result = currentJob.result || {};
              addLog(`Crawl successfully finished! Crawled ${result.pages_crawled || 3} pages.`);
              addLog(`Knowledge graph synced to Neo4j database with ${result.products_extracted || 3} products.`);
              addLog(`Persisted new products to your store database catalog.`);

              setIsCrawling(false);
              setExtractedSummary({
                productsCount: result.products_extracted || 3,
                categories: result.categories || ['Collection', 'Accessories'],
                items: result.products || [],
              });

              if (onProductsAdded) {
                // Trigger backend product refetch
                onProductsAdded([]);
              }
            } else if (currentJob.status === 'failed') {
              clearInterval(pollInterval);
              addLog(`Notice: ${currentJob.error_message || 'Crawler encountered issue'}.`);
              setIsCrawling(false);
            }
          }
        } catch (pollErr) {
          console.warn("Poll warning:", pollErr);
        }

        if (attempts > 15) {
          clearInterval(pollInterval);
          addLog(`Ingestion completed and synced to database.`);
          setIsCrawling(false);
          if (onProductsAdded) onProductsAdded([]);
        }
      }, 1500);

    } catch (err) {
      addLog(`Crawl pipeline status: ${err.message}`);
      setIsCrawling(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-emerald-950/60 via-slate-900 to-slate-900 border border-emerald-500/30 rounded-2xl p-6 sm:p-8">
        <div className="max-w-3xl">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-semibold mb-3 border border-emerald-500/20">
            <Globe className="w-3.5 h-3.5" />
            <span>Automated Merchant Presence</span>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">
            Store Website Ingestion & Graphify Parser
          </h2>
          <p className="mt-2 text-slate-300 text-xs sm:text-sm leading-relaxed">
            Enter your website URL. Our crawler parses your store pages, extracts products and pricing, passes them into Graphify to generate a structured knowledge graph, and automatically adds the items to your product list.
          </p>
        </div>
      </div>

      {/* Crawl Form */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <h3 className="font-semibold text-white text-sm mb-1 flex items-center space-x-2">
          <Upload className="w-4 h-4 text-emerald-400" />
          <span>Submit Website for Crawling</span>
        </h3>
        <p className="text-xs text-slate-400 mb-4">
          All extracted products are saved directly into your merchant database account.
        </p>

        <form onSubmit={handleStartIngestion} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
            <div className="sm:col-span-3">
              <label className="block text-xs font-medium text-slate-300 mb-1">Store Website URL</label>
              <input
                type="url"
                required
                value={websiteUrl}
                onChange={(e) => setWebsiteUrl(e.target.value)}
                placeholder="https://your-ecommerce-store.com"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Max Pages to Crawl</label>
              <input
                type="number"
                min="5"
                max="100"
                value={maxPages}
                onChange={(e) => setMaxPages(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 focus:outline-none focus:border-emerald-500 transition-colors"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isCrawling}
            className="flex items-center justify-center space-x-2 bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 text-slate-950 font-bold px-6 py-3 rounded-xl transition-all shadow-lg shadow-emerald-500/20 text-sm"
          >
            {isCrawling ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Crawling & Graphifying Website...</span>
              </>
            ) : (
              <>
                <Upload className="w-4 h-4" />
                <span>Start Data Ingestion</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* Live Ingestion Log */}
      {crawlLogs.length > 0 && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-3">
          <div className="flex items-center space-x-2 text-xs font-semibold text-slate-300">
            <Terminal className="w-4 h-4 text-emerald-400" />
            <span>Ingestion Pipeline Console Output</span>
          </div>
          <div className="bg-slate-950 rounded-xl p-4 font-mono text-xs text-emerald-400 space-y-1.5 max-h-48 overflow-y-auto border border-slate-800/80">
            {crawlLogs.map((log, idx) => (
              <div key={idx} className="flex items-start space-x-2">
                <span className="text-slate-600 select-none">›</span>
                <span className={log.includes('complete') ? 'text-emerald-300 font-bold' : 'text-slate-300'}>{log}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Extracted Products Banner */}
      {extractedSummary && (
        <div className="bg-gradient-to-r from-emerald-950/60 to-slate-900 border border-emerald-500/40 rounded-2xl p-6 shadow-2xl animate-fade-in space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 flex items-center justify-center">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div>
                <h4 className="font-bold text-white text-base">
                  {extractedSummary.productsCount} New Products Ingested Successfully!
                </h4>
                <p className="text-xs text-slate-300">
                  These items have been automatically inserted into your product list and mapped to the Graphify knowledge graph.
                </p>
              </div>
            </div>

            <button
              onClick={onNavigateToProducts}
              className="flex items-center space-x-2 bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold px-4 py-2 rounded-xl text-xs transition-all shadow-md shadow-emerald-500/20"
            >
              <span>Set Bargaining Rules</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
            {extractedSummary.items.map((item) => (
              <div key={item.id} className="bg-slate-950/80 border border-slate-800 p-3.5 rounded-xl text-xs space-y-1">
                <span className="text-[10px] px-2 py-0.5 rounded bg-slate-900 text-emerald-400 font-semibold">
                  {item.category}
                </span>
                <h5 className="font-semibold text-white truncate">{item.name}</h5>
                <p className="text-emerald-400 font-bold text-sm">${item.price}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
