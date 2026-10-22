import React from 'react';
import { ShoppingBag, CheckCircle2, ShieldCheck, ArrowRight, Bot } from 'lucide-react';

export default function ConsumerOrders({ purchases = [] }) {
  const displayPurchases = purchases;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <ShoppingBag className="w-5 h-5 text-emerald-400" />
            <span>My Negotiated Purchases</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            All purchases finalized and secured by your Gemma agent on AgenticBuy.
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {displayPurchases.length === 0 ? (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center shadow-xl space-y-3">
            <ShoppingBag className="w-10 h-10 mx-auto text-slate-600" />
            <h4 className="text-white font-semibold text-sm">No Purchases Yet</h4>
            <p className="text-slate-400 text-xs max-w-sm mx-auto">
              You haven't placed any orders yet. Open the Gemma Agentic Chat, search for products, make an offer, and complete your purchase!
            </p>
          </div>
        ) : (
          displayPurchases.map((p) => (
          <div
            key={p.id}
            className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4"
          >
            <div className="space-y-1.5">
              <div className="flex items-center space-x-2">
                <span className="text-xs font-mono font-bold text-white bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                  #{p.id}
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  {p.status.toUpperCase()}
                </span>
              </div>
              <h4 className="font-bold text-white text-base">{p.product_name}</h4>
              <p className="text-xs text-slate-400">
                Merchant: <span className="text-emerald-400 font-semibold">{p.merchant_name || 'TechGear Store'}</span> • {p.timestamp}
              </p>
            </div>

            <div className="text-right sm:border-l sm:border-slate-800 sm:pl-6">
              <div className="text-lg font-bold text-emerald-400">${p.agreed_price?.toFixed(2)}</div>
              {p.original_price && (
                <div className="text-xs text-slate-500 line-through">${p.original_price.toFixed(2)}</div>
              )}
              {p.savings && (
                <span className="text-xs font-medium text-emerald-500 block mt-1">
                  Saved {p.savings}
                </span>
              )}
            </div>
          </div>
        )))}
      </div>
    </div>
  );
}
