import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Bot,
  User,
  Sparkles,
  ShoppingBag,
  TrendingDown,
  CheckCircle2,
  XCircle,
  ArrowRight,
  ShieldCheck,
  RefreshCw
} from 'lucide-react';

import { useAuth } from '../context/AuthContext';

export default function ConsumerPortal({ onOrderPlaced }) {
  const { token, user } = useAuth();
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'agent',
      text: `👋 Hi ${user?.full_name || 'there'}! I'm your **AgenticBuy Agent** powered by Gemma. I have direct access to all onboarded merchants, live stock, and their bargaining algorithms. Tell me what you're looking for, or make an offer on any item!`,
      time: 'Just now',
      actions: [],
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeNegotiation, setActiveNegotiation] = useState(null);
  const [orderConfirmed, setOrderConfirmed] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e, directText = null) => {
    e?.preventDefault();
    const userText = (directText || inputMessage).trim();
    if (!userText || isLoading) return;

    const newMsg = {
      id: Date.now(),
      sender: 'user',
      text: userText,
      time: 'Just now',
    };

    setMessages((prev) => [...prev, newMsg]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/v1/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ message: userText }),
      });

      if (!response.ok) {
        throw new Error('API offline');
      }

      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'agent',
          text: data.response,
          time: 'Just now',
          actions: data.actions || [],
        },
      ]);

      // Check if negotiation action occurred
      const negAction = data.actions?.find((a) => a.tool === 'start_negotiation');
      if (negAction && negAction.result) {
        setActiveNegotiation(negAction.result);
      }

      const orderAction = data.actions?.find((a) => a.tool === 'place_order');
      if (orderAction && orderAction.result) {
        setOrderConfirmed(orderAction.result);
        setActiveNegotiation(null);
        if (onOrderPlaced) onOrderPlaced(orderAction.result);
      }
    } catch (err) {
      console.error("Chat error:", err);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'agent',
          text: `⚠️ Network error communicating with Gemma agent (${err.message}). Please check backend status.`,
          time: 'Just now',
        },
      ]);
      setIsLoading(false);
      return;
    }

    setIsLoading(false);
  };

  const handleLocalSimulation = (userText) => {
    const lower = userText.toLowerCase();

    if (lower.includes('offer') || lower.includes('bargain') || lower.includes('$')) {
      const match = userText.match(/\$?([0-9]+(?:\.[0-9]{1,2})?)/);
      const offer = match ? parseFloat(match[1]) : 120;

      if (offer >= 135) {
        // Auto accepted!
        const sess = {
          session_id: 'sess-' + Date.now().toString().slice(-4),
          status: 'accepted',
          final_price: offer,
          product_name: 'Noise-Cancelling Wireless Headphones',
        };
        setActiveNegotiation(sess);
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now(),
            sender: 'agent',
            text: `🎉 **Offer Accepted!** The merchant's threshold allows directly agreeing to **$${offer.toFixed(2)}** (original list: $149.99). Would you like me to finalize and place your order?`,
            time: 'Just now',
          },
        ]);
      } else if (offer < 110) {
        // Floor rejected
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now(),
            sender: 'agent',
            text: `❌ **Offer Too Low:** The merchant's floor price won't allow $${offer.toFixed(2)}. Their absolute lowest is $110.00. Could you raise your offer to something closer?`,
            time: 'Just now',
          },
        ]);
      } else {
        // Counter offer
        const counter = Math.round((offer + 149.99) / 2);
        setActiveNegotiation({
          session_id: 'sess-' + Date.now().toString().slice(-4),
          status: 'active',
          counter_offer: counter,
          current_offer: offer,
          product_name: 'Noise-Cancelling Wireless Headphones',
        });
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now(),
            sender: 'agent',
            text: `🤝 The merchant cannot accept $${offer.toFixed(2)} right away, but their bargaining algorithm counters with **$${counter.toFixed(2)}** (saving you $${(149.99 - counter).toFixed(2)}). Accept or counter back?`,
            time: 'Just now',
          },
        ]);
      }
    } else if (lower.includes('buy') || lower.includes('confirm') || lower.includes('yes') || lower.includes('order')) {
      const confirmedOrder = {
        order_id: 'ord-' + Math.floor(1000 + Math.random() * 9000),
        product_name: activeNegotiation?.product_name || 'Noise-Cancelling Wireless Headphones',
        unit_price: activeNegotiation?.final_price || activeNegotiation?.counter_offer || 125.0,
        quantity: 1,
        total_price: activeNegotiation?.final_price || activeNegotiation?.counter_offer || 125.0,
        status: 'confirmed',
      };
      setOrderConfirmed(confirmedOrder);
      setActiveNegotiation(null);
      if (onOrderPlaced) onOrderPlaced(confirmedOrder);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          sender: 'agent',
          text: `🎉 **Purchase Successful!** I placed order **#${confirmedOrder.order_id}** for **${confirmedOrder.product_name}** at the negotiated price of **$${confirmedOrder.unit_price.toFixed(2)}**. The merchant has been notified!`,
          time: 'Just now',
        },
      ]);
    } else {
      // General product search
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          sender: 'agent',
          text: "I traversed the **Graphify Knowledge Graph** and found these matching products from verified merchants:\n\n• **Noise-Cancelling Wireless Headphones** — Listed: $149.99 (Stock: 24) [Bargaining Open 🟢]\n• **Mechanical Ergonomic Keyboard** — Listed: $119.00 (Stock: 15) [Bargaining Open 🟢]\n• **Ultra-Fast GaN Charger 100W** — Listed: $49.99 (Stock: 50) [Firm Price 🔒]\n\nTry making an offer like: *'I offer $125 for the headphones'*!",
          time: 'Just now',
        },
      ]);
    }
  };

  const quickAction = (prompt) => {
    setInputMessage(prompt);
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Left/Main Column: Chat Area */}
      <div className="lg:col-span-2 flex flex-col h-[750px] bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
        {/* Chat Header */}
        <div className="p-4 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-slate-950 font-bold shadow-md shadow-emerald-500/20">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-semibold text-slate-100 text-sm">Gemma Shopping Agent</span>
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              </div>
              <p className="text-xs text-slate-400">Autonomous bargaining & purchase execution</p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
              Open-Weight Brain
            </span>
          </div>
        </div>

        {/* Message Thread */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((m) => (
            <div
              key={m.id}
              className={`flex items-start space-x-2.5 ${
                m.sender === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {m.sender === 'agent' && (
                <div className="w-7 h-7 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0 border border-emerald-500/30">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div
                className={`max-w-[85%] rounded-2xl p-3.5 text-sm shadow-md ${
                  m.sender === 'user'
                    ? 'bg-emerald-500 text-slate-950 font-medium rounded-br-none'
                    : 'bg-slate-950 border border-slate-800 text-slate-200 rounded-bl-none whitespace-pre-line'
                }`}
              >
                {m.text}
              </div>

              {m.sender === 'user' && (
                <div className="w-7 h-7 rounded-lg bg-slate-800 text-slate-300 flex items-center justify-center shrink-0">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex items-center space-x-2 text-slate-400 text-xs p-2">
              <RefreshCw className="w-3.5 h-3.5 animate-spin text-emerald-400" />
              <span>Gemma agent is checking merchant rules and calculating counter-offer...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Prompts */}
        <div className="px-4 py-2 bg-slate-950/60 border-t border-slate-800/80 flex items-center space-x-2 overflow-x-auto text-xs text-slate-400">
          <span className="shrink-0 text-slate-500 font-medium">Try asking:</span>
          <button
            onClick={() => quickAction("Find me wireless headphones")}
            className="shrink-0 px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 transition-colors"
          >
            🔍 "Find headphones"
          </button>
          <button
            onClick={() => quickAction("I offer $125 for wireless headphones")}
            className="shrink-0 px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-emerald-400 transition-colors"
          >
            🏷️ "I offer $125"
          </button>
          <button
            onClick={() => quickAction("Yes, confirm and buy at this price")}
            className="shrink-0 px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 transition-colors"
          >
            💳 "Confirm purchase"
          </button>
        </div>

        {/* Input Bar */}
        <form onSubmit={handleSendMessage} className="p-3 bg-slate-950 border-t border-slate-800 flex items-center space-x-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Search products, bargain a price (e.g. 'I offer $125'), or ask to buy..."
            className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors"
          />
          <button
            type="submit"
            disabled={!inputMessage.trim() || isLoading}
            className="bg-emerald-500 hover:bg-emerald-600 disabled:opacity-40 text-slate-950 p-3 rounded-xl transition-all font-semibold"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>

      {/* Right Column: Negotiation & Purchase Status Card */}
      <div className="space-y-6">
        {/* Live Deal State Machine */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
          <div className="flex items-center space-x-2 pb-3 border-b border-slate-800 mb-4">
            <TrendingDown className="w-5 h-5 text-emerald-400" />
            <h3 className="font-semibold text-white text-sm">Agentic Bargaining Engine</h3>
          </div>

          {activeNegotiation ? (
            <div className="space-y-4">
              <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
                <span className="text-xs text-slate-400 block mb-1">Product in Negotiation</span>
                <span className="font-semibold text-white text-sm">{activeNegotiation.product_name || 'Item'}</span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-center">
                <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                  <span className="text-xs text-slate-400 block">Your Offer</span>
                  <span className="text-base font-bold text-slate-200">
                    ${activeNegotiation.current_offer || activeNegotiation.final_price || 0}
                  </span>
                </div>
                <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                  <span className="text-xs text-emerald-400 block">Agent Counter</span>
                  <span className="text-base font-bold text-emerald-400">
                    ${activeNegotiation.counter_offer || activeNegotiation.final_price || 'Agreed'}
                  </span>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-300 flex items-center space-x-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>
                  {activeNegotiation.status === 'accepted'
                    ? 'Price accepted by merchant rules!'
                    : 'Negotiation in progress within merchant bounds.'}
                </span>
              </div>

              <button
                onClick={() => handleSendMessage(null, "Yes, confirm and buy at this price")}
                className="w-full py-2.5 bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold rounded-xl text-xs transition-all flex items-center justify-center space-x-1.5 shadow-lg shadow-emerald-500/20"
              >
                <span>Accept & Complete Purchase</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="text-center py-8 text-slate-500 text-xs space-y-2">
              <ShoppingBag className="w-8 h-8 mx-auto text-slate-600" />
              <p>No active price negotiation session.</p>
              <p className="text-slate-400">Type an offer in the chat to start automated bargaining with the merchant!</p>
            </div>
          )}
        </div>

        {/* Order Receipt when placed */}
        {orderConfirmed && (
          <div className="bg-gradient-to-b from-slate-900 to-emerald-950/40 border border-emerald-500/40 rounded-2xl p-5 shadow-2xl animate-fade-in">
            <div className="flex items-center space-x-2 text-emerald-400 mb-3">
              <CheckCircle2 className="w-5 h-5" />
              <span className="font-bold text-sm">Order Placed Successfully!</span>
            </div>

            <div className="space-y-2 text-xs text-slate-300">
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Order ID:</span>
                <span className="font-mono font-bold text-white">{orderConfirmed.order_id}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Product:</span>
                <span className="text-white font-medium">{orderConfirmed.product_name}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Negotiated Price:</span>
                <span className="text-emerald-400 font-bold text-sm">${orderConfirmed.unit_price?.toFixed(2)}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400">Fulfillment Status:</span>
                <span className="text-emerald-400 font-semibold uppercase">{orderConfirmed.status}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
