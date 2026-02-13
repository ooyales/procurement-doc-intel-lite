import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Package,
  Search,
  RefreshCw,
  Calculator,
  ChevronDown,
  ChevronRight,
  ChevronLeft,
  Loader2,
  X,
  TrendingUp,
  Tag,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import client from '@/api/client';

interface Product {
  id: string;
  canonical_name: string;
  category: string | null;
  manufacturer: string | null;
  known_part_numbers: string[];
  known_aliases: string[];
  last_known_price: number | null;
  last_price_date: string | null;
  avg_price: number | null;
  min_price: number | null;
  max_price: number | null;
  price_history: Array<{ price: number; date: string; vendor: string }>;
  created_at: string;
}

interface ProductDetail extends Product {
  recent_line_items: Array<any>;
  line_item_count: number;
}

interface IGCEResult {
  product_name: string;
  category: string | null;
  manufacturer: string | null;
  quantity: number;
  avg_unit_price: number;
  min_price: number | null;
  max_price: number | null;
  escalation_rate: number;
  estimated_unit_price: number;
  estimated_total: number;
  price_sources: Array<{ price: number; date: string; vendor: string }>;
  data_points: number;
}

const CATEGORIES = [
  { value: '', label: 'All Categories' },
  { value: 'hardware', label: 'Hardware' },
  { value: 'software', label: 'Software' },
  { value: 'service', label: 'Service' },
  { value: 'license', label: 'License' },
  { value: 'maintenance', label: 'Maintenance' },
  { value: 'labor', label: 'Labor' },
  { value: 'other', label: 'Other' },
];

function formatCurrency(val: number | null | undefined): string {
  if (val == null) return '--';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);
}

function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return '--';
  try {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

export default function ProductCatalogPage() {
  const navigate = useNavigate();

  // Filters
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [page, setPage] = useState(1);
  const perPage = 25;

  // Data
  const [products, setProducts] = useState<Product[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [rebuilding, setRebuilding] = useState(false);
  const [rebuildMessage, setRebuildMessage] = useState<string | null>(null);

  // Detail expansion
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [detailData, setDetailData] = useState<ProductDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // IGCE modal
  const [igceProductId, setIgceProductId] = useState<string | null>(null);
  const [igceQuantity, setIgceQuantity] = useState('1');
  const [igceEscalation, setIgceEscalation] = useState('3');
  const [igceResult, setIgceResult] = useState<IGCEResult | null>(null);
  const [igceLoading, setIgceLoading] = useState(false);

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string | number> = { page, per_page: perPage };
      if (search) params.search = search;
      if (category) params.category = category;

      const res = await client.get('/products', { params });
      setProducts(res.data.items);
      setTotal(res.data.total);
    } catch {
      // Silent fail
    } finally {
      setLoading(false);
    }
  }, [page, search, category]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  useEffect(() => {
    setPage(1);
  }, [search, category]);

  const handleRebuild = async () => {
    if (!confirm('Rebuild the product catalog from all extracted line items? This may take a moment.')) return;
    setRebuilding(true);
    setRebuildMessage(null);
    try {
      const res = await client.post('/products/rebuild');
      setRebuildMessage(res.data.message);
      fetchProducts();
    } catch (err: any) {
      setRebuildMessage(err?.response?.data?.error || 'Rebuild failed.');
    } finally {
      setRebuilding(false);
    }
  };

  const handleExpand = async (productId: string) => {
    if (expandedId === productId) {
      setExpandedId(null);
      setDetailData(null);
      return;
    }
    setExpandedId(productId);
    setDetailLoading(true);
    try {
      const res = await client.get(`/products/${productId}`);
      setDetailData(res.data);
    } catch {
      setDetailData(null);
    } finally {
      setDetailLoading(false);
    }
  };

  const openIGCE = (productId: string) => {
    setIgceProductId(productId);
    setIgceQuantity('1');
    setIgceEscalation('3');
    setIgceResult(null);
  };

  const closeIGCE = () => {
    setIgceProductId(null);
    setIgceResult(null);
  };

  const calculateIGCE = async () => {
    if (!igceProductId) return;
    setIgceLoading(true);
    try {
      const res = await client.post(`/products/${igceProductId}/igce`, {
        quantity: parseFloat(igceQuantity) || 1,
        escalation_rate: (parseFloat(igceEscalation) || 3) / 100,
      });
      setIgceResult(res.data);
    } catch (err: any) {
      alert(err?.response?.data?.error || 'IGCE calculation failed.');
    } finally {
      setIgceLoading(false);
    }
  };

  const totalPages = Math.ceil(total / perPage);

  return (
    <div>
      {/* Page Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Package size={18} className="text-eaw-primary" />
            <h1 className="text-xl font-bold text-eaw-font">Product Catalog</h1>
          </div>
          <p className="text-sm text-eaw-muted">
            Canonical products with pricing intelligence and IGCE estimates.
          </p>
        </div>
        <button
          className="btn-secondary"
          onClick={handleRebuild}
          disabled={rebuilding}
        >
          {rebuilding ? (
            <Loader2 size={14} className="animate-spin" />
          ) : (
            <RefreshCw size={14} />
          )}
          {rebuilding ? 'Rebuilding...' : 'Rebuild Catalog'}
        </button>
      </div>

      {/* Rebuild message */}
      {rebuildMessage && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded text-sm text-blue-700">
          {rebuildMessage}
        </div>
      )}

      {/* Search / Filter Bar */}
      <div className="eaw-card mb-4">
        <div className="flex flex-wrap gap-3 items-end">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-xs font-medium text-eaw-muted mb-1">Search</label>
            <div className="relative">
              <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="input-field pl-8"
                placeholder="Search products, manufacturers..."
              />
            </div>
          </div>
          <div className="min-w-[150px]">
            <label className="block text-xs font-medium text-eaw-muted mb-1">Category</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="select-field"
            >
              {CATEGORIES.map((c) => (
                <option key={c.value} value={c.value}>{c.label}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Product Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 size={24} className="animate-spin text-eaw-primary" />
        </div>
      ) : products.length === 0 ? (
        <div className="eaw-card text-center py-16">
          <Package size={32} className="mx-auto text-gray-300 mb-3" />
          <p className="text-eaw-muted text-sm">
            No products in the catalog yet. Process some documents and rebuild the catalog.
          </p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 mb-6">
            {products.map((product) => (
              <div key={product.id} className="eaw-card hover:shadow-md transition-shadow">
                {/* Product Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1 min-w-0">
                    <h3
                      className="font-semibold text-sm text-eaw-font truncate cursor-pointer hover:text-eaw-link"
                      onClick={() => handleExpand(product.id)}
                      title={product.canonical_name}
                    >
                      {product.canonical_name}
                    </h3>
                    {product.manufacturer && (
                      <p className="text-xs text-eaw-muted mt-0.5">{product.manufacturer}</p>
                    )}
                  </div>
                  <button
                    className="ml-2 p-1 text-gray-400 hover:text-eaw-primary"
                    onClick={() => handleExpand(product.id)}
                  >
                    {expandedId === product.id ? (
                      <ChevronDown size={16} />
                    ) : (
                      <ChevronRight size={16} />
                    )}
                  </button>
                </div>

                {/* Category badge */}
                {product.category && (
                  <div className="mb-3">
                    <span className="badge-info">{product.category}</span>
                  </div>
                )}

                {/* Price Info */}
                <div className="space-y-1.5 mb-3">
                  <div className="flex justify-between text-xs">
                    <span className="text-eaw-muted">Last Price</span>
                    <span className="font-medium text-eaw-font">{formatCurrency(product.last_known_price)}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-eaw-muted">Avg Price</span>
                    <span className="font-medium text-eaw-font">{formatCurrency(product.avg_price)}</span>
                  </div>
                  {(product.min_price != null || product.max_price != null) && (
                    <div className="flex justify-between text-xs">
                      <span className="text-eaw-muted">Range</span>
                      <span className="text-eaw-font">
                        {formatCurrency(product.min_price)} - {formatCurrency(product.max_price)}
                      </span>
                    </div>
                  )}
                </div>

                {/* Part Numbers */}
                {product.known_part_numbers.length > 0 && (
                  <div className="mb-3">
                    <p className="text-xs text-eaw-muted mb-1">Part Numbers:</p>
                    <div className="flex flex-wrap gap-1">
                      {product.known_part_numbers.slice(0, 5).map((pn, idx) => (
                        <span key={idx} className="inline-flex items-center px-1.5 py-0.5 bg-gray-100 rounded text-xs text-eaw-font">
                          <Tag size={10} className="mr-0.5 text-gray-400" />
                          {pn}
                        </span>
                      ))}
                      {product.known_part_numbers.length > 5 && (
                        <span className="text-xs text-eaw-muted">
                          +{product.known_part_numbers.length - 5} more
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {/* Aliases */}
                {product.known_aliases.length > 0 && (
                  <div className="mb-3">
                    <p className="text-xs text-eaw-muted mb-1">Also known as:</p>
                    <div className="flex flex-wrap gap-1">
                      {product.known_aliases.slice(0, 3).map((alias, idx) => (
                        <span key={idx} className="px-1.5 py-0.5 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-800">
                          {alias}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* IGCE Button */}
                <button
                  className="btn-primary w-full justify-center !text-xs mt-2"
                  onClick={() => openIGCE(product.id)}
                >
                  <Calculator size={14} />
                  IGCE Estimate
                </button>

                {/* Expanded Detail */}
                {expandedId === product.id && (
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    {detailLoading ? (
                      <div className="flex items-center justify-center py-6">
                        <Loader2 size={16} className="animate-spin text-eaw-primary" />
                      </div>
                    ) : detailData ? (
                      <>
                        {/* Price History Chart */}
                        {detailData.price_history.length > 1 && (
                          <div className="mb-4">
                            <h4 className="text-xs font-semibold text-eaw-muted mb-2 flex items-center gap-1">
                              <TrendingUp size={12} />
                              Price History
                            </h4>
                            <ResponsiveContainer width="100%" height={140}>
                              <LineChart data={detailData.price_history}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                                <XAxis dataKey="date" tick={{ fontSize: 9, fill: '#999' }} />
                                <YAxis
                                  tick={{ fontSize: 9, fill: '#999' }}
                                  tickFormatter={(v) => `$${v.toLocaleString()}`}
                                />
                                <Tooltip
                                  formatter={(val: number) => formatCurrency(val)}
                                  labelFormatter={(label: string) => `Date: ${label}`}
                                />
                                <Line
                                  type="monotone"
                                  dataKey="price"
                                  stroke="#337ab7"
                                  strokeWidth={2}
                                  dot={{ fill: '#337ab7', r: 2 }}
                                />
                              </LineChart>
                            </ResponsiveContainer>
                          </div>
                        )}

                        {/* Related Line Items */}
                        {detailData.recent_line_items.length > 0 && (
                          <div>
                            <h4 className="text-xs font-semibold text-eaw-muted mb-2">
                              Related Line Items ({detailData.line_item_count})
                            </h4>
                            <div className="overflow-x-auto">
                              <table className="eaw-table text-xs">
                                <thead>
                                  <tr>
                                    <th>Vendor</th>
                                    <th>Qty</th>
                                    <th>Unit Price</th>
                                    <th>Date</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {detailData.recent_line_items.slice(0, 5).map((li: any) => (
                                    <tr
                                      key={li.id}
                                      className="cursor-pointer hover:bg-gray-50"
                                      onClick={() => navigate(`/documents/${li.document_id}`)}
                                    >
                                      <td>{li.vendor_name || '--'}</td>
                                      <td>{li.quantity ?? '--'}</td>
                                      <td>{formatCurrency(li.unit_price)}</td>
                                      <td className="text-eaw-muted">{formatDate(li.document_date)}</td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          </div>
                        )}
                      </>
                    ) : (
                      <p className="text-xs text-eaw-muted text-center py-4">
                        Failed to load product details.
                      </p>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Pagination */}
          {total > perPage && (
            <div className="flex items-center justify-between mb-6 pt-2">
              <span className="text-xs text-eaw-muted">
                Showing {(page - 1) * perPage + 1}--
                {Math.min(page * perPage, total)} of {total}
              </span>
              <div className="flex items-center gap-1">
                <button
                  className="btn-secondary !py-1 !px-2"
                  disabled={page <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                >
                  <ChevronLeft size={16} />
                </button>
                <span className="text-xs text-eaw-font px-2">
                  Page {page} of {totalPages}
                </span>
                <button
                  className="btn-secondary !py-1 !px-2"
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => p + 1)}
                >
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {/* IGCE Modal */}
      {igceProductId && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <h3 className="text-sm font-semibold text-eaw-font flex items-center gap-2">
                <Calculator size={16} className="text-eaw-primary" />
                IGCE Estimate
              </h3>
              <button className="text-gray-400 hover:text-gray-600" onClick={closeIGCE}>
                <X size={18} />
              </button>
            </div>
            <div className="p-4 space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-eaw-muted mb-1">Quantity</label>
                  <input
                    type="number"
                    min="1"
                    step="1"
                    value={igceQuantity}
                    onChange={(e) => setIgceQuantity(e.target.value)}
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-eaw-muted mb-1">Escalation Rate (%)</label>
                  <input
                    type="number"
                    min="0"
                    step="0.5"
                    value={igceEscalation}
                    onChange={(e) => setIgceEscalation(e.target.value)}
                    className="input-field"
                  />
                </div>
              </div>

              <button
                className="btn-primary w-full justify-center"
                onClick={calculateIGCE}
                disabled={igceLoading}
              >
                {igceLoading ? <Loader2 size={14} className="animate-spin" /> : <Calculator size={14} />}
                {igceLoading ? 'Calculating...' : 'Calculate'}
              </button>

              {/* IGCE Result */}
              {igceResult && (
                <div className="space-y-3 pt-3 border-t border-gray-100">
                  <h4 className="text-sm font-semibold text-eaw-font">
                    {igceResult.product_name}
                  </h4>
                  {igceResult.manufacturer && (
                    <p className="text-xs text-eaw-muted">{igceResult.manufacturer}</p>
                  )}

                  <div className="bg-blue-50 rounded-lg p-4 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-eaw-muted">Estimated Unit Price</span>
                      <span className="font-bold text-eaw-font">{formatCurrency(igceResult.estimated_unit_price)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-eaw-muted">Quantity</span>
                      <span className="font-medium text-eaw-font">{igceResult.quantity}</span>
                    </div>
                    <div className="flex justify-between text-sm border-t border-blue-200 pt-2">
                      <span className="font-semibold text-eaw-font">Estimated Total</span>
                      <span className="font-bold text-lg text-eaw-primary">{formatCurrency(igceResult.estimated_total)}</span>
                    </div>
                  </div>

                  <div className="text-xs text-eaw-muted space-y-1">
                    <p>Average historical price: {formatCurrency(igceResult.avg_unit_price)}</p>
                    {igceResult.min_price != null && igceResult.max_price != null && (
                      <p>Price range: {formatCurrency(igceResult.min_price)} -- {formatCurrency(igceResult.max_price)}</p>
                    )}
                    <p>Escalation rate: {(igceResult.escalation_rate * 100).toFixed(1)}%</p>
                    <p>Based on {igceResult.data_points} data point{igceResult.data_points !== 1 ? 's' : ''}</p>
                  </div>

                  {/* Price Sources */}
                  {igceResult.price_sources.length > 0 && (
                    <div className="pt-2">
                      <p className="text-xs font-medium text-eaw-muted mb-1">Source Data:</p>
                      <div className="overflow-x-auto">
                        <table className="eaw-table text-xs">
                          <thead>
                            <tr>
                              <th>Vendor</th>
                              <th>Price</th>
                              <th>Date</th>
                            </tr>
                          </thead>
                          <tbody>
                            {igceResult.price_sources.map((src, idx) => (
                              <tr key={idx}>
                                <td>{src.vendor || '--'}</td>
                                <td>{formatCurrency(src.price)}</td>
                                <td className="text-eaw-muted">{src.date || '--'}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
