import React from 'react';
import {
  Store,
  Bot,
  Package,
  Network,
  ShoppingBag,
  Globe,
  Terminal,
  LogOut,
  Sparkles,
  ChevronRight,
  ShieldCheck,
  UserCheck
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Sidebar({ activePage, setActivePage }) {
  const { user, logout } = useAuth();
  const isMerchant = user?.role === 'merchant';

  const merchantNavItems = [
    { id: 'ingestion', label: 'Website Ingestion', icon: Globe, badge: 'Crawl' },
    { id: 'products', label: 'Products & Bargaining Rules', icon: Package, badge: 'AI Rules' },
    { id: 'graph', label: 'Interactive Knowledge Graph', icon: Network, badge: 'Graphify' },
    { id: 'orders', label: 'Agent Orders Placed', icon: ShoppingBag, badge: 'Live' },
    { id: 'api-docs', label: 'Single LLM API (Claude/GPT)', icon: Terminal },
  ];

  const consumerNavItems = [
    { id: 'chat', label: 'AgenticBuy Chat & Bargain', icon: Bot, badge: 'Gemma' },
    { id: 'purchases', label: 'My Orders & Receipts', icon: ShoppingBag },
    { id: 'api-docs', label: 'LLM Agent Tools', icon: Terminal },
  ];

  const navItems = isMerchant ? merchantNavItems : consumerNavItems;

  return (
    <aside className="w-64 bg-slate-950 border-r border-slate-800 flex flex-col h-screen sticky top-0 shrink-0 select-none">
      {/* Brand header */}
      <div className="p-5 border-b border-slate-800 flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-slate-950 font-bold shadow-lg shadow-emerald-500/20 shrink-0">
          <Sparkles className="w-5 h-5" />
        </div>
        <div className="min-w-0">
          <div className="flex items-center space-x-2">
            <span className="font-bold text-base text-white truncate">AgenticBuy</span>
          </div>
          <span className="text-[11px] font-semibold text-emerald-400 font-mono">
            {isMerchant ? 'Merchant Hub' : 'Shopper Platform'}
          </span>
        </div>
      </div>

      {/* Navigation items */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        <div className="px-3 py-2 text-[11px] font-bold uppercase tracking-wider text-slate-500">
          {isMerchant ? 'Store Management' : 'Autonomous Shopping'}
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActivePage(item.id)}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all group ${
                isActive
                  ? 'bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/10 font-bold'
                  : 'text-slate-400 hover:text-white hover:bg-slate-900'
              }`}
            >
              <div className="flex items-center space-x-3 min-w-0">
                <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-slate-950' : 'text-slate-400 group-hover:text-emerald-400'}`} />
                <span className="truncate">{item.label}</span>
              </div>
              {item.badge && (
                <span className={`text-[10px] px-1.5 py-0.5 rounded-md font-mono ${
                  isActive ? 'bg-slate-950 text-emerald-400' : 'bg-slate-900 text-slate-400 border border-slate-800'
                }`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* User profile & Logout */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/60">
        <div className="flex items-center space-x-3 mb-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xs">
            {user?.full_name?.charAt(0) || 'U'}
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-xs font-semibold text-white truncate">{user?.full_name}</div>
            <div className="text-[10px] text-slate-400 truncate flex items-center space-x-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block"></span>
              <span className="capitalize">{user?.role}</span>
              {user?.business_name && <span>• {user.business_name}</span>}
            </div>
          </div>
        </div>

        <button
          onClick={logout}
          className="w-full flex items-center justify-center space-x-2 py-2 px-3 rounded-lg text-xs font-medium text-slate-400 hover:text-rose-400 hover:bg-rose-950/20 border border-slate-800/80 transition-colors"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
}
