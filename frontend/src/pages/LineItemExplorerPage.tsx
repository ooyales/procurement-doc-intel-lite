import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  Download,
  ChevronLeft,
  ChevronRight,
  ChevronUp,
  ChevronDown,
  Loader2,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import client from '@/api/client';

interface LineItem {
  id: string;
  document_id: string;
  product_name: string | null;
  part_number: string | null;
  category: string | null;
  quantity: number | null;
  unit_price: number | null;
  extended_price: number | null;
  vendor_name: string | null;
  document_number: string | null;
  document_date: string | null;
  manufacturer: string | null;
}

interface SpendAnalysis {
  spend_by_vendor: Array<{ vendor: string; total: number }>;
  spend_by_category: Array<{ category: string; total: number }>;
  spend_over_time: Array<{ month: string; total: number }>;
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

const PIE_COLORS = ['#337ab7', '#5cb85c', '#7c3aed', '#f0ad4e', '#d9534f', '#5bc0de', '#888', '#e83e8c'];

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

export default function LineItemExplorerPage() {
  const navigate = useNavigate();

  // Filters
  const [search, setSearch] = useState('');
  const [vendor, setVendor] = useState('');
  const [category, setCategory] = useState('');
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const perPage = 25;

  // Data
  const [items, setItems] = useState<LineItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [spendData, setSpendData] = useState<SpendAnalysis | null>(null);
  const [vendorOptions, setVendorOptions] = useState<string[]>([]);

  const fetchItems = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string | number> = {
        page,
        per_page: perPage,
        sort_by: sortBy,
        sort_order: sortOrder,
      };
      if (search) params.search = search;
      if (vendor) params.vendor = vendor;
      if (category) params.category = category;
      if (minPrice) params.min_price = parseFloat(minPrice);
      if (maxPrice) params.max_price = parseFloat(maxPrice);

      const res = await client.get('/line-items', { params });
      setItems(res.data.items);
      setTotal(res.data.total);

      // Collect unique vendors from data for the dropdown
      const vendors = new Set<string>();
      res.data.items.forEach((i: LineItem) => {
        if (i.vendor_name) vendors.add(i.vendor_name);
      });
      setVendorOptions((prev) => {
        const combined = new Set([...prev, ...vendors]);
        return Array.from(combined).sort();
      });
    } catch {
      // Silent fail
    } finally {
      setLoading(false);
    }
  }, [page, search, vendor, category, minPrice, maxPrice, sortBy, sortOrder]);

  const fetchSpendAnalysis = useCallback(async () => {
    try {
      const res = await client.get('/line-items/spend-analysis');
      setSpendData(res.data);

      // Extract vendors from spend data for dropdown
      const vNames = res.data.spend_by_vendor.map((v: any) => v.vendor);
      setVendorOptions((prev) => {
        const combined = new Set([...prev, ...vNames]);
        return Array.from(combined).sort();
      });
    } catch {
      // Silent fail
    }
  }, []);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  useEffect(() => {
    fetchSpendAnalysis();
  }, [fetchSpendAnalysis]);

  useEffect(() => {
    setPage(1);
  }, [search, vendor, category, minPrice, maxPrice]);

  const handleSort = (field: string) => {
    if (sortBy === field) {
      setSortOrder((o) => (o === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
  };

  const SortIcon = ({ field }: { field: string }) => {
    if (sortBy !== field) return null;
    return sortOrder === 'asc' ? (
      <ChevronUp size={12} className="inline ml-0.5" />
    ) : (
      <ChevronDown size={12} className="inline ml-0.5" />
    );
  };

  const handleExport = async (format: 'csv' | 'xlsx') => {
    try {
      const params: Record<string, string | number> = { format };
      if (search) params.search = search;
      if (vendor) params.vendor = vendor;
      if (category) params.category = category;
      if (minPrice) params.min_price = parseFloat(minPrice);
      if (maxPrice) params.max_price = parseFloat(maxPrice);

      const res = await client.get('/line-items/export', {
        params,
        responseType: 'blob',
      });

      const blob = new Blob([res.data]);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `line_items_export.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      // Silent fail
    }
  };

  const totalPages = Math.ceil(total / perPage);

  return (
    <div>
      {/* Page Header */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-1">
          <Search size={18} className="text-eaw-primary" />
          <h1 className="text-xl font-bold text-eaw-font">Line Item Explorer</h1>
        </div>
        <p className="text-sm text-eaw-muted">
          Search, filter, and analyze extracted line items across all documents.
        </p>
      </div>

      {/* Filter Bar */}
      <div className="eaw-card mb-4">
        <div className="flex flex-wrap gap-3 items-end">
          <div className="flex-1 min-w-[180px]">
            <label className="block text-xs font-medium text-eaw-muted mb-1">Search</label>
            <div className="relative">
              <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="input-field pl-8"
                placeholder="Product name, part #, manufacturer..."
              />
            </div>
          </div>
          <div className="min-w-[150px]">
            <label className="block text-xs font-medium text-eaw-muted mb-1">Vendor</label>
            <select
              value={vendor}
              onChange={(e) => setVendor(e.target.value)}
              className="select-field"
            >
              <option value="">All Vendors</option>
              {vendorOptions.map((v) => (
                <option key={v} value={v}>{v}</option>
              ))}
            </select>
          </div>
          <div className="min-w-[140px]">
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
          <div className="min-w-[100px]">
            <label className="block text-xs font-medium text-eaw-muted mb-1">Min Price</label>
            <input
              type="number"
              value={minPrice}
              onChange={(e) => setMinPrice(e.target.value)}
              className="input-field"
              placeholder="$0"
              step="0.01"
            />
          </div>
          <div className="min-w-[100px]">
            <label className="block text-xs font-medium text-eaw-muted mb-1">Max Price</label>
            <input
              type="number"
              value={maxPrice}
              onChange={(e) => setMaxPrice(e.target.value)}
              className="input-field"
              placeholder="$999,999"
              step="0.01"
            />
          </div>
          <div className="flex gap-1.5">
            <button className="btn-secondary !text-xs" onClick={() => handleExport('csv')}>
              <Download size={14} />
              CSV
            </button>
            <button className="btn-secondary !text-xs" onClick={() => handleExport('xlsx')}>
              <Download size={14} />
              XLSX
            </button>
          </div>
        </div>
      </div>

      {/* Results Table */}
      <div className="eaw-card mb-6">
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 size={24} className="animate-spin text-eaw-primary" />
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="eaw-table">
                <thead>
                  <tr>
                    <th className="cursor-pointer select-none" onClick={() => handleSort('product_name')}>
                      Product Name <SortIcon field="product_name" />
                    </th>
                    <th className="cursor-pointer select-none" onClick={() => handleSort('part_number')}>
                      Part # <SortIcon field="part_number" />
                    </th>
                    <th>Vendor</th>
                    <th className="cursor-pointer select-none" onClick={() => handleSort('category')}>
                      Category <SortIcon field="category" />
                    </th>
                    <th className="cursor-pointer select-none text-right" onClick={() => handleSort('quantity')}>
                      Qty <SortIcon field="quantity" />
                    </th>
                    <th className="cursor-pointer select-none text-right" onClick={() => handleSort('unit_price')}>
                      Unit Price <SortIcon field="unit_price" />
                    </th>
                    <th className="cursor-pointer select-none text-right" onClick={() => handleSort('extended_price')}>
                      Ext Price <SortIcon field="extended_price" />
                    </th>
                    <th>Document #</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((item) => (
                    <tr
                      key={item.id}
                      className="cursor-pointer hover:bg-gray-50"
                      onClick={() => navigate(`/documents/${item.document_id}`)}
                    >
                      <td className="font-medium text-eaw-font max-w-[200px] truncate" title={item.product_name || ''}>
                        {item.product_name || '--'}
                      </td>
                      <td className="text-eaw-muted">{item.part_number || '--'}</td>
                      <td>{item.vendor_name || '--'}</td>
                      <td>
                        {item.category ? (
                          <span className="badge-info">{item.category}</span>
                        ) : (
                          '--'
                        )}
                      </td>
                      <td className="text-right">{item.quantity ?? '--'}</td>
                      <td className="text-right whitespace-nowrap">{formatCurrency(item.unit_price)}</td>
                      <td className="text-right whitespace-nowrap">{formatCurrency(item.extended_price)}</td>
                      <td className="text-eaw-muted">{item.document_number || '--'}</td>
                      <td className="text-eaw-muted whitespace-nowrap">{formatDate(item.document_date)}</td>
                    </tr>
                  ))}
                  {items.length === 0 && (
                    <tr>
                      <td colSpan={9} className="text-center text-eaw-muted py-12">
                        No line items found matching your criteria.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {total > perPage && (
              <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
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
      </div>

      {/* Spend Analysis Charts */}
      {spendData && (
        <div>
          <h2 className="text-sm font-semibold text-eaw-font mb-4">Spend Analysis</h2>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Spend by Vendor */}
            <div className="eaw-card">
              <h3 className="text-xs font-semibold text-eaw-muted mb-3">Spend by Vendor</h3>
              {spendData.spend_by_vendor.length > 0 ? (
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={spendData.spend_by_vendor.slice(0, 8)} layout="vertical" barSize={18}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                    <XAxis
                      type="number"
                      tick={{ fontSize: 10, fill: '#777' }}
                      tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
                    />
                    <YAxis
                      type="category"
                      dataKey="vendor"
                      tick={{ fontSize: 10, fill: '#777' }}
                      width={90}
                    />
                    <Tooltip formatter={(val: number) => formatCurrency(val)} />
                    <Bar dataKey="total" fill="#337ab7" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-xs text-eaw-muted text-center py-8">No data</p>
              )}
            </div>

            {/* Spend by Category */}
            <div className="eaw-card">
              <h3 className="text-xs font-semibold text-eaw-muted mb-3">Spend by Category</h3>
              {spendData.spend_by_category.length > 0 ? (
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie
                      data={spendData.spend_by_category}
                      cx="50%"
                      cy="50%"
                      innerRadius={45}
                      outerRadius={70}
                      dataKey="total"
                      nameKey="category"
                      paddingAngle={2}
                    >
                      {spendData.spend_by_category.map((_, idx) => (
                        <Cell key={idx} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(val: number) => formatCurrency(val)} />
                    <Legend
                      verticalAlign="bottom"
                      height={36}
                      formatter={(value: string) => (
                        <span className="text-xs text-eaw-font">{value}</span>
                      )}
                    />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-xs text-eaw-muted text-center py-8">No data</p>
              )}
            </div>

            {/* Spend over Time */}
            <div className="eaw-card">
              <h3 className="text-xs font-semibold text-eaw-muted mb-3">Spend over Time</h3>
              {spendData.spend_over_time.length > 0 ? (
                <ResponsiveContainer width="100%" height={220}>
                  <LineChart data={spendData.spend_over_time}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                    <XAxis dataKey="month" tick={{ fontSize: 10, fill: '#777' }} />
                    <YAxis
                      tick={{ fontSize: 10, fill: '#777' }}
                      tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
                    />
                    <Tooltip formatter={(val: number) => formatCurrency(val)} />
                    <Line
                      type="monotone"
                      dataKey="total"
                      stroke="#337ab7"
                      strokeWidth={2}
                      dot={{ fill: '#337ab7', r: 3 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-xs text-eaw-muted text-center py-8">No data</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
