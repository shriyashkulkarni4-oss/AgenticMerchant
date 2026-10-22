import React, { useState } from 'react';
import {
  Package,
  Plus,
  Sliders,
  DollarSign,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  Search,
  Tag,
  Save
} from 'lucide-react';

export default function MerchantProducts({ products, onUpdateProduct, onAddProduct }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState('');

  // Add Product Modal form states
  const [newName, setNewName] = useState('');
  const [newPrice, setNewPrice] = useState('');
  const [newAutoAccept, setNewAutoAccept] = useState('');
  const [newFloor, setNewFloor] = useState('');
  const [newStock, setNewStock] = useState('15');
  const [newCategory, setNewCategory] = useState('');

  const filteredProducts = products.filter(
    (p) =>
      p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (p.category && p.category.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const handleSaveAll = () => {
    setSaveSuccessMsg('All product bargaining thresholds saved successfully!');
    setTimeout(() => setSaveSuccessMsg(''), 3000);
  };

  const handleCreateProduct = (e) => {
    e.preventDefault();
    if (!newName || !newPrice) return;

    const priceNum = parseFloat(newPrice);
    const prod = {
      id: 'p-' + Date.now(),
      name: newName,
      price: priceNum,
      auto_accept_threshold: parseFloat(newAutoAccept) || priceNum * 0.9,
      min_acceptable_price: parseFloat(newFloor) || priceNum * 0.8,
      stock_quantity: parseInt(newStock) || 10,
      bargaining_enabled: true,
      max_rounds: 5,
      category: newCategory || 'General',
      description: 'Manually added merchant inventory item.',
    };

    onAddProduct(prod);
    setShowAddModal(false);
    setNewName('');
    setNewPrice('');
    setNewAutoAccept('');
    setNewFloor('');
    setNewCategory('');
    setSaveSuccessMsg(`Added "${prod.name}" to inventory!`);
    setTimeout(() => setSaveSuccessMsg(''), 3000);
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <Package className="w-5 h-5 text-emerald-400" />
            <span>Product Inventory & AI Bargaining Rules</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Configure listed price, auto-accept threshold, and minimum floor price for each product. The Gemma agent bargains with shoppers strictly within these bounds.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center space-x-2 bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold px-4 py-2.5 rounded-xl text-xs transition-all shadow-md shadow-emerald-500/20"
          >
            <Plus className="w-4 h-4" />
            <span>Add Product</span>
          </button>
          <button
            onClick={handleSaveAll}
            className="flex items-center space-x-2 bg-slate-800 hover:bg-slate-700 text-white font-semibold px-4 py-2.5 rounded-xl text-xs transition-all border border-slate-700"
          >
            <Save className="w-4 h-4 text-emerald-400" />
            <span>Save All Rules</span>
          </button>
        </div>
      </div>

      {saveSuccessMsg && (
        <div className="p-3.5 bg-emerald-950/40 border border-emerald-500/30 rounded-xl text-xs text-emerald-300 flex items-center space-x-2 animate-fade-in">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{saveSuccessMsg}</span>
        </div>
      )}

      {/* Search & Stats Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-md">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search products or categories..."
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors"
          />
        </div>
        <div className="text-xs text-slate-400 font-medium">
          Showing <span className="text-white font-bold">{filteredProducts.length}</span> of {products.length} products
        </div>
      </div>

      {/* Products List */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl divide-y divide-slate-800">
        {filteredProducts.map((p) => (
          <div
            key={p.id}
            className="p-5 flex flex-col lg:flex-row lg:items-center justify-between gap-4 hover:bg-slate-800/30 transition-colors"
          >
            <div className="space-y-1.5 max-w-md">
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                {p.category || 'General'}
              </span>
              <h4 className="font-semibold text-white text-sm">{p.name}</h4>
              <p className="text-xs text-slate-400 line-clamp-1">{p.description || 'Catalog item'}</p>
              <div className="text-[11px] text-slate-500 flex items-center space-x-3 pt-1">
                <span>Stock: <strong className="text-slate-300">{p.stock_quantity || 10} units</strong></span>
                <span>•</span>
                <span className={p.bargaining_enabled ? 'text-emerald-400 font-semibold' : 'text-slate-500'}>
                  {p.bargaining_enabled ? '🟢 Bargaining Active' : '🔒 Firm Price'}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">
              {/* Listed Price */}
              <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                <span className="text-slate-400 block mb-1 text-[11px]">Listed Price</span>
                <div className="flex items-center text-slate-200 font-semibold text-sm">
                  <span>$</span>
                  <input
                    type="number"
                    step="0.01"
                    value={p.price}
                    onChange={(e) => onUpdateProduct(p.id, 'price', parseFloat(e.target.value) || 0)}
                    className="w-16 bg-transparent ml-1 focus:outline-none focus:text-emerald-400"
                  />
                </div>
              </div>

              {/* Directly Agreeable */}
              <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                <span className="text-emerald-400 font-semibold block mb-1 text-[11px]">Agree Directly</span>
                <div className="flex items-center text-slate-200 font-semibold text-sm">
                  <span>$</span>
                  <input
                    type="number"
                    step="0.01"
                    value={p.auto_accept_threshold}
                    onChange={(e) => onUpdateProduct(p.id, 'auto_accept_threshold', parseFloat(e.target.value) || 0)}
                    className="w-16 bg-transparent ml-1 focus:outline-none focus:text-emerald-400"
                  />
                </div>
              </div>

              {/* Floor Price */}
              <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                <span className="text-rose-400 font-semibold block mb-1 text-[11px]">Floor Minimum</span>
                <div className="flex items-center text-slate-200 font-semibold text-sm">
                  <span>$</span>
                  <input
                    type="number"
                    step="0.01"
                    value={p.min_acceptable_price}
                    onChange={(e) => onUpdateProduct(p.id, 'min_acceptable_price', parseFloat(e.target.value) || 0)}
                    className="w-16 bg-transparent ml-1 focus:outline-none focus:text-emerald-400"
                  />
                </div>
              </div>

              {/* Toggle Bargaining */}
              <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 flex flex-col justify-between">
                <span className="text-slate-400 block mb-1 text-[11px]">AI Bargaining</span>
                <button
                  type="button"
                  onClick={() => onUpdateProduct(p.id, 'bargaining_enabled', !p.bargaining_enabled)}
                  className={`px-2 py-1 rounded text-[11px] font-bold text-center transition-all ${
                    p.bargaining_enabled
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  {p.bargaining_enabled ? 'Enabled' : 'Disabled'}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Add Product Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 max-w-lg w-full shadow-2xl space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center space-x-2">
              <Plus className="w-5 h-5 text-emerald-400" />
              <span>Add New Product Listing</span>
            </h3>

            <form onSubmit={handleCreateProduct} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-300 font-medium mb-1">Product Name</label>
                <input
                  type="text"
                  required
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="e.g. Ergonomic Standing Desk"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Listed Price ($)</label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={newPrice}
                    onChange={(e) => setNewPrice(e.target.value)}
                    placeholder="199.99"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-emerald-400 font-medium mb-1">Directly Agreeable ($)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={newAutoAccept}
                    onChange={(e) => setNewAutoAccept(e.target.value)}
                    placeholder="180.00"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-rose-400 font-medium mb-1">Floor Minimum ($)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={newFloor}
                    onChange={(e) => setNewFloor(e.target.value)}
                    placeholder="160.00"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Stock Quantity</label>
                  <input
                    type="number"
                    value={newStock}
                    onChange={(e) => setNewStock(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">Category</label>
                <input
                  type="text"
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value)}
                  placeholder="Furniture / Office"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="flex items-center justify-end space-x-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold rounded-xl shadow-lg shadow-emerald-500/20"
                >
                  Save Product
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
