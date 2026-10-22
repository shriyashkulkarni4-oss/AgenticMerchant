import React from 'react';
import { ShoppingBag, CheckCircle2, Clock, DollarSign, Bot, ArrowUpRight } from 'lucide-react';

export default function MerchantOrders({ orders = [] }) {
  const displayOrders = orders;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <ShoppingBag className="w-5 h-5 text-emerald-400" />
            <span>Autonomous Purchases Placed by AI Agents</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Orders concluded and posted directly by AI agents (Claude, GPT, Gemma) on behalf of shoppers according to your price rules.
          </p>
        </div>
        <div className="text-xs text-slate-400 bg-slate-950 px-3.5 py-2 rounded-xl border border-slate-800">
          Total AI Orders: <strong className="text-emerald-400">{displayOrders.length}</strong>
        </div>
      </div>

      {/* Orders List */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl divide-y divide-slate-800">
        {displayOrders.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <ShoppingBag className="w-10 h-10 mx-auto text-slate-600" />
            <h4 className="text-white font-semibold text-sm">No Orders Received Yet</h4>
            <p className="text-slate-400 text-xs max-w-sm mx-auto">
              When consumer AI agents negotiate and complete purchases for your products, the real-time transactions will appear here and in your database.
            </p>
          </div>
        ) : (
          displayOrders.map((o) => (
          <div
            key={o.id}
            className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-800/40 transition-colors"
          >
            <div className="space-y-1.5">
              <div className="flex items-center space-x-2.5">
                <span className="text-xs font-mono font-bold text-slate-300 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                  #{o.id}
                </span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                  o.status === 'confirmed'
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                    : o.status === 'shipped'
                    ? 'bg-blue-500/10 text-blue-400 border-blue-500/20'
                    : 'bg-purple-500/10 text-purple-400 border-purple-500/20'
                }`}>
                  {o.status.toUpperCase()}
                </span>
              </div>
              <h4 className="font-semibold text-white text-sm">{o.product_name}</h4>
              <p className="text-xs text-slate-400 flex items-center space-x-1.5">
                <Bot className="w-3.5 h-3.5 text-emerald-400" />
                <span>Placed via: <strong className="text-slate-300">{o.buyer}</strong></span>
                <span>•</span>
                <span className="text-slate-500">{o.timestamp}</span>
              </p>
            </div>

            <div className="text-right sm:border-l sm:border-slate-800 sm:pl-6">
              <div className="text-base font-bold text-emerald-400">${o.agreed_price?.toFixed(2)}</div>
              {o.original_price && o.original_price !== o.agreed_price && (
                <div className="text-xs text-slate-500 line-through">${o.original_price.toFixed(2)}</div>
              )}
              <span className="text-[11px] font-medium text-emerald-500 block mt-0.5">
                {o.discount ? `Bargained: ${o.discount}` : 'Agreed Price'}
              </span>
            </div>
          </div>
        )))}
      </div>
    </div>
  );
}
