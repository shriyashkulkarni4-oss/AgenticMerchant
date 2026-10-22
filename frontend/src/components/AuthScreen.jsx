import React, { useState } from 'react';
import {
  Store,
  Bot,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Globe,
  Mail,
  Lock,
  User,
  Terminal,
  Zap,
  AlertCircle
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function AuthScreen({ onOpenApiDocs }) {
  const { login, register } = useAuth();
  const [selectedRole, setSelectedRole] = useState('consumer'); // 'merchant' or 'consumer'
  const [isSignUp, setIsSignUp] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Form states
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [businessName, setBusinessName] = useState('');
  const [websiteUrl, setWebsiteUrl] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isSignUp) {
        await register({
          email,
          password,
          full_name: fullName,
          role: selectedRole,
          business_name: selectedRole === 'merchant' ? businessName : null,
          website_url: selectedRole === 'merchant' ? websiteUrl : null,
        });
      } else {
        await login(email, password, selectedRole);
      }
    } catch (err) {
      setError(err.message || 'Authentication failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async (role) => {
    setError('');
    setLoading(true);
    try {
      if (role === 'merchant') {
        await login('merchant@techgear.com', 'merchant123', 'merchant');
      } else {
        await login('shopper@agenticbuy.com', 'shopper123', 'consumer');
      }
    } catch (err) {
      setError(err.message || 'Demo login error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background glow effects */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[350px] bg-gradient-to-tr from-emerald-600/10 via-teal-500/10 to-blue-600/10 rounded-full blur-3xl pointer-events-none" />

      {/* Top Header */}
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center mb-6 relative z-10">
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-emerald-500 to-teal-400 text-slate-950 font-bold shadow-xl shadow-emerald-500/20 mb-3">
          <Sparkles className="w-7 h-7" />
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">AgenticBuy</h1>
        <p className="mt-1 text-sm text-slate-400">
          Autonomous Merchant & AI Bargaining Network powered by Gemma
        </p>
      </div>

      <div className="sm:mx-auto sm:w-full sm:max-w-xl relative z-10">
        {/* Role Selector Tabs */}
        <div className="bg-slate-900/90 p-1.5 rounded-2xl border border-slate-800 flex space-x-2 mb-6 shadow-xl">
          <button
            type="button"
            onClick={() => {
              setSelectedRole('consumer');
              setError('');
            }}
            className={`flex-1 flex items-center justify-center space-x-2.5 py-3 rounded-xl text-sm font-semibold transition-all ${
              selectedRole === 'consumer'
                ? 'bg-emerald-500 text-slate-950 shadow-lg shadow-emerald-500/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <Bot className="w-4 h-4" />
            <span>Shopper / Consumer</span>
          </button>

          <button
            type="button"
            onClick={() => {
              setSelectedRole('merchant');
              setError('');
            }}
            className={`flex-1 flex items-center justify-center space-x-2.5 py-3 rounded-xl text-sm font-semibold transition-all ${
              selectedRole === 'merchant'
                ? 'bg-emerald-500 text-slate-950 shadow-lg shadow-emerald-500/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <Store className="w-4 h-4" />
            <span>Merchant Portal</span>
          </button>
        </div>

        {/* Main Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl backdrop-blur-xl">
          <div className="flex items-center justify-between pb-5 border-b border-slate-800 mb-6">
            <div>
              <h2 className="text-lg font-bold text-white">
                {selectedRole === 'merchant'
                  ? isSignUp ? 'Register as Merchant' : 'Merchant Sign In'
                  : isSignUp ? 'Create Shopper Account' : 'Shopper Sign In'}
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                {selectedRole === 'merchant'
                  ? 'Manage catalog ingestion, Graphify knowledge graph, and AI bargaining rules.'
                  : 'Start bargaining and shopping with the Gemma autonomous agent.'}
              </p>
            </div>

            <div className="flex items-center space-x-1 bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs font-medium">
              <button
                type="button"
                onClick={() => { setIsSignUp(false); setError(''); }}
                className={`px-3 py-1.5 rounded-lg transition-all ${
                  !isSignUp ? 'bg-slate-800 text-white font-semibold' : 'text-slate-400 hover:text-white'
                }`}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => { setIsSignUp(true); setError(''); }}
                className={`px-3 py-1.5 rounded-lg transition-all ${
                  isSignUp ? 'bg-slate-800 text-white font-semibold' : 'text-slate-400 hover:text-white'
                }`}
              >
                Sign Up
              </button>
            </div>
          </div>

          {error && (
            <div className="mb-5 p-3.5 bg-rose-950/40 border border-rose-500/30 rounded-xl text-xs text-rose-300 flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {isSignUp && (
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Full Name</label>
                <div className="relative">
                  <User className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder={selectedRole === 'merchant' ? 'Alex Rivera' : 'Alice Chen'}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors"
                  />
                </div>
              </div>
            )}

            {isSignUp && selectedRole === 'merchant' && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Store / Business Name</label>
                  <div className="relative">
                    <Store className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type="text"
                      required
                      value={businessName}
                      onChange={(e) => setBusinessName(e.target.value)}
                      placeholder="TechGear Store"
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Website URL</label>
                  <div className="relative">
                    <Globe className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type="url"
                      value={websiteUrl}
                      onChange={(e) => setWebsiteUrl(e.target.value)}
                      placeholder="https://techgear.com"
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors"
                    />
                  </div>
                </div>
              </div>
            )}

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Email Address</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={selectedRole === 'merchant' ? 'merchant@store.com' : 'shopper@email.com'}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-3 bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 text-slate-950 font-bold rounded-xl text-sm transition-all flex items-center justify-center space-x-2 shadow-lg shadow-emerald-500/20"
            >
              <span>{loading ? 'Authenticating...' : isSignUp ? 'Create Account & Continue' : 'Sign In'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* Quick Demo Login Buttons */}
          <div className="mt-6 pt-5 border-t border-slate-800/80">
            <span className="text-xs text-slate-500 block mb-3 font-medium text-center">
              Or instant 1-click test login:
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              <button
                type="button"
                onClick={() => handleDemoLogin('merchant')}
                className="flex items-center justify-center space-x-2 py-2 px-3 bg-slate-950 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-white rounded-xl text-xs font-medium transition-colors"
              >
                <Store className="w-3.5 h-3.5 text-emerald-400" />
                <span>Demo Merchant (TechGear)</span>
              </button>

              <button
                type="button"
                onClick={() => handleDemoLogin('consumer')}
                className="flex items-center justify-center space-x-2 py-2 px-3 bg-slate-950 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-white rounded-xl text-xs font-medium transition-colors"
              >
                <Bot className="w-3.5 h-3.5 text-blue-400" />
                <span>Demo Shopper (Alice)</span>
              </button>
            </div>
          </div>
        </div>

        {/* Public API docs shortcut */}
        <div className="mt-6 text-center">
          <button
            onClick={onOpenApiDocs}
            className="inline-flex items-center space-x-2 text-xs text-slate-400 hover:text-emerald-400 transition-colors"
          >
            <Terminal className="w-3.5 h-3.5" />
            <span>Looking for the Single API for Claude / GPT? View API Documentation</span>
          </button>
        </div>
      </div>
    </div>
  );
}
