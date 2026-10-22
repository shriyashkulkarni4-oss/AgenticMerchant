import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import AuthScreen from './components/AuthScreen';
import Sidebar from './components/Sidebar';
import MerchantIngestion from './components/MerchantIngestion';
import MerchantProducts from './components/MerchantProducts';
import FullGraphVisualizer from './components/FullGraphVisualizer';
import MerchantOrders from './components/MerchantOrders';
import ConsumerPortal from './components/ConsumerPortal';
import ConsumerOrders from './components/ConsumerOrders';
import LlmApiDocs from './components/LlmApiDocs';
import { ArrowLeft, Sparkles, Store, Bot } from 'lucide-react';

function MainApp() {
  const { user, token, isAuthenticated, logout } = useAuth();
  const [activePage, setActivePage] = useState('chat');
  const [viewingPublicApi, setViewingPublicApi] = useState(false);

  // Merchant products state - populated dynamically from database
  const [products, setProducts] = useState([]);

  // Merchant orders & Consumer purchases - populated dynamically from database
  const [merchantOrders, setMerchantOrders] = useState([]);
  const [consumerPurchases, setConsumerPurchases] = useState([]);
  const [isLoadingData, setIsLoadingData] = useState(true);

  // Load products from backend database
  const fetchProductsFromBackend = async () => {
    try {
      const res = await fetch('/api/v1/products/?limit=100');
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data)) {
          setProducts(data);
        }
      }
    } catch (e) {
      console.warn("Could not fetch remote products:", e);
    }
  };

  // Load orders dynamically from backend database
  const fetchOrdersFromBackend = async () => {
    try {
      const res = await fetch('/api/v1/orders/?limit=50', {
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      });
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data)) {
          const mOrders = data.map((o) => ({
            id: String(o.id).slice(0, 8),
            product_name: o.product_name || 'Product Item',
            buyer: o.buyer_name || 'Autonomous Shopper Agent',
            original_price: Number(o.original_price) || Number(o.unit_price),
            agreed_price: Number(o.unit_price),
            discount: o.original_price && Number(o.original_price) > Number(o.unit_price)
              ? `${Math.round(((Number(o.original_price) - Number(o.unit_price)) / Number(o.original_price)) * 100)}%`
              : '0%',
            status: o.status || 'confirmed',
            timestamp: o.created_at ? new Date(o.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Recent',
          }));
          setMerchantOrders(mOrders);

          const cPurchases = data.map((o) => ({
            id: String(o.id).slice(0, 8),
            product_name: o.product_name || 'Product Item',
            merchant_name: o.merchant_name || 'Merchant Store',
            agreed_price: Number(o.unit_price),
            original_price: Number(o.original_price) || Number(o.unit_price),
            savings: o.original_price && Number(o.original_price) > Number(o.unit_price)
              ? `$${(Number(o.original_price) - Number(o.unit_price)).toFixed(2)} (${Math.round(((Number(o.original_price) - Number(o.unit_price)) / Number(o.original_price)) * 100)}% off)`
              : null,
            status: o.status || 'confirmed',
            timestamp: o.created_at ? new Date(o.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Recent',
          }));
          setConsumerPurchases(cPurchases);
        }
      }
    } catch (e) {
      console.warn("Could not fetch remote orders:", e);
    } finally {
      setIsLoadingData(false);
    }
  };

  useEffect(() => {
    fetchProductsFromBackend();
    fetchOrdersFromBackend();
  }, [user, token]);

  // Set default page whenever user logs in based on their role
  useEffect(() => {
    if (user?.role === 'merchant') {
      setActivePage('products');
    } else if (user?.role === 'consumer') {
      setActivePage('chat'); // Direct to agent negotiation engine on login!
    }
  }, [user]);

  // Handler when products are auto-extracted from crawling
  const handleProductsAdded = async (newItems = []) => {
    if (Array.isArray(newItems) && newItems.length > 0) {
      for (const item of newItems) {
        try {
          await fetch('/api/v1/products/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              ...(token ? { Authorization: `Bearer ${token}` } : {}),
            },
            body: JSON.stringify({
              name: item.name,
              description: item.description || '',
              price: parseFloat(item.price),
              min_acceptable_price: parseFloat(item.min_acceptable_price),
              auto_accept_threshold: parseFloat(item.auto_accept_threshold),
              bargaining_enabled: item.bargaining_enabled ?? true,
              stock_quantity: parseInt(item.stock_quantity) || 10,
              category: item.category || 'General',
            }),
          });
        } catch (err) {
          console.error("Failed to persist product to DB:", err);
        }
      }
    }
    await fetchProductsFromBackend();
    await fetchOrdersFromBackend();
  };

  const handleUpdateProduct = async (id, field, value) => {
    setProducts((prev) =>
      prev.map((p) => (p.id === id ? { ...p, [field]: value } : p))
    );

    // If UUID, update backend database
    if (typeof id === 'string' && id.length > 30) {
      try {
        await fetch(`/api/v1/products/${id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({ [field]: value }),
        });
      } catch (e) {
        console.warn("Could not sync product update to backend:", e);
      }
    }
  };

  const handleAddProduct = async (newProd) => {
    try {
      const res = await fetch('/api/v1/products/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          name: newProd.name,
          description: newProd.description || '',
          price: parseFloat(newProd.price),
          min_acceptable_price: parseFloat(newProd.min_acceptable_price),
          auto_accept_threshold: parseFloat(newProd.auto_accept_threshold),
          bargaining_enabled: newProd.bargaining_enabled ?? true,
          stock_quantity: parseInt(newProd.stock_quantity) || 10,
          category: newProd.category || 'General',
        }),
      });
      if (res.ok) {
        await fetchProductsFromBackend();
      }
    } catch (err) {
      console.error("Failed to add product to backend DB:", err);
    }
  };

  const handleOrderPlaced = async (orderData) => {
    if (orderData.product_id) {
      try {
        await fetch('/api/v1/orders/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({
            product_id: orderData.product_id,
            quantity: 1,
            negotiation_session_id: orderData.negotiation_session_id || null,
          }),
        });
      } catch (err) {
        console.warn("Order placement note:", err);
      }
    }
    await fetchOrdersFromBackend();
    await fetchProductsFromBackend();
  };

  // If user clicked public API explorer from Auth screen
  if (viewingPublicApi) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
        <header className="border-b border-slate-800 bg-slate-950 p-4 flex items-center justify-between">
          <button
            onClick={() => setViewingPublicApi(false)}
            className="flex items-center space-x-2 text-xs font-semibold text-slate-300 hover:text-white bg-slate-900 px-3 py-2 rounded-xl border border-slate-800 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Login & Signup</span>
          </button>
          <div className="flex items-center space-x-2">
            <span className="font-bold text-white text-sm">AgenticBuy API Docs</span>
          </div>
        </header>
        <main className="flex-1 p-6">
          <LlmApiDocs />
        </main>
      </div>
    );
  }

  // If not logged in -> Show Auth Screen with separate Merchant vs Consumer tabs & Demo logins!
  if (!isAuthenticated) {
    return <AuthScreen onOpenApiDocs={() => setViewingPublicApi(true)} />;
  }

  // Authenticated Layout with Modern Sidebar and Separated Pages
  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100">
      {/* Sidebar Navigation */}
      <Sidebar activePage={activePage} setActivePage={setActivePage} />

      {/* Main Content Area */}
      <main className="flex-1 min-w-0 flex flex-col h-screen overflow-y-auto">
        {/* Top Header */}
        <header className="border-b border-slate-800/80 bg-slate-950/60 backdrop-blur-md px-8 py-4 flex items-center justify-between sticky top-0 z-20">
          <div className="flex items-center space-x-3">
            <h1 className="text-base font-bold text-white capitalize">
              {activePage === 'ingestion' && 'Website Ingestion & Graphify'}
              {activePage === 'products' && 'Product Inventory & AI Rules'}
              {activePage === 'graph' && 'Whole Knowledge Graph Visualizer'}
              {activePage === 'orders' && 'Incoming Agent Orders'}
              {activePage === 'chat' && 'AgenticBuy Autonomous Shopping Agent'}
              {activePage === 'purchases' && 'My Negotiated Orders'}
              {activePage === 'api-docs' && 'Single API for Claude & Agents'}
            </h1>
          </div>

          <div className="flex items-center space-x-3">
            <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
              {user?.role === 'merchant' ? `🏪 ${user.business_name || 'Store Account'}` : `🛒 Shopper: ${user.full_name}`}
            </span>
          </div>
        </header>

        {/* Page Content */}
        <div className="p-6 sm:p-8 flex-1">
          {/* Merchant Views */}
          {user?.role === 'merchant' && (
            <>
              {activePage === 'ingestion' && (
                <MerchantIngestion
                  onProductsAdded={handleProductsAdded}
                  onNavigateToProducts={() => setActivePage('products')}
                />
              )}
              {activePage === 'products' && (
                <MerchantProducts
                  products={products}
                  onUpdateProduct={handleUpdateProduct}
                  onAddProduct={handleAddProduct}
                />
              )}
              {activePage === 'graph' && (
                <FullGraphVisualizer
                  merchantData={user}
                  products={products}
                />
              )}
              {activePage === 'orders' && (
                <MerchantOrders orders={merchantOrders} />
              )}
              {activePage === 'api-docs' && <LlmApiDocs />}
            </>
          )}

          {/* Consumer Views */}
          {user?.role === 'consumer' && (
            <>
              {activePage === 'chat' && (
                <ConsumerPortal onOrderPlaced={handleOrderPlaced} />
              )}
              {activePage === 'purchases' && (
                <ConsumerOrders purchases={consumerPurchases} />
              )}
              {activePage === 'api-docs' && <LlmApiDocs />}
            </>
          )}
        </div>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
}
