import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileBarChart,
  FileText,
  Search,
  Package,
  Clock,
  Loader2,
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import client from '@/api/client';

interface DashboardData {
  total_documents: number;
  documents_by_status: Record<string, number>;
  documents_by_type: Record<string, number>;
  total_line_items: number;
  total_products: number;
  total_spend: number;
  top_vendors: Array<{ vendor_name: string; document_count: number; total_spend: number }>;
  spend_by_category: Array<{ category: string; total: number }>;
  recent_documents: Array<any>;
  processing_queue: Array<any>;
}

const TYPE_COLORS = ['#337ab7', '#5cb85c', '#7c3aed', '#f0ad4e', '#d9534f', '#5bc0de', '#888'];

function formatCurrency(val: number | null | undefined): string {
  if (val == null) return '$0.00';
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

function formatDocType(type: string | null | undefined): string {
  if (!type) return 'Unknown';
  return type
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

function statusBadge(status: string): string {
  switch (status) {
    case 'uploaded': return 'badge-muted';
    case 'extracting':
    case 'mapping': return 'badge-info';
    case 'review': return 'badge-warning';
    case 'complete': return 'badge-success';
    case 'failed': return 'badge-danger';
    default: return 'badge-muted';
  }
}

export default function DashboardPage() {
  const navigate = useNavigate();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    client
      .get('/dashboard')
      .then((res) => {
        if (!cancelled) setData(res.data);
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 size={32} className="animate-spin text-eaw-primary" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center text-eaw-muted py-16">
        Failed to load dashboard data. Please try refreshing.
      </div>
    );
  }

  const pendingCount =
    (data.documents_by_status['uploaded'] || 0) +
    (data.documents_by_status['extracting'] || 0) +
    (data.documents_by_status['mapping'] || 0) +
    (data.documents_by_status['review'] || 0);

  const kpis = [
    {
      label: 'Total Documents',
      value: data.total_documents,
      icon: <FileText size={18} />,
      bg: 'bg-blue-50',
      color: 'text-eaw-primary',
    },
    {
      label: 'Line Items Extracted',
      value: data.total_line_items,
      icon: <Search size={18} />,
      bg: 'bg-green-50',
      color: 'text-eaw-success',
    },
    {
      label: 'Products Cataloged',
      value: data.total_products,
      icon: <Package size={18} />,
      bg: 'bg-purple-50',
      color: 'text-purple-600',
    },
    {
      label: 'Pending Review',
      value: pendingCount,
      icon: <Clock size={18} />,
      bg: 'bg-yellow-50',
      color: 'text-eaw-warning',
    },
  ];

  // Transform documents_by_type dict into array for PieChart
  const docTypeData = Object.entries(data.documents_by_type).map(([name, value], idx) => ({
    name: formatDocType(name),
    value,
    color: TYPE_COLORS[idx % TYPE_COLORS.length],
  }));

  // spend_by_category for horizontal BarChart
  const spendByCat = data.spend_by_category.map((c) => ({
    ...c,
    category: formatDocType(c.category),
  }));

  return (
    <div>
      {/* Page Header */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-1">
          <FileBarChart size={18} className="text-eaw-primary" />
          <h1 className="text-xl font-bold text-eaw-font">Dashboard</h1>
        </div>
        <p className="text-sm text-eaw-muted">
          Overview of your procurement document processing and spend intelligence.
        </p>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {kpis.map((kpi) => (
          <div key={kpi.label} className="kpi-card">
            <div className={`kpi-icon ${kpi.bg} ${kpi.color}`}>{kpi.icon}</div>
            <div>
              <div className="kpi-value">{kpi.value.toLocaleString()}</div>
              <div className="kpi-label">{kpi.label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        {/* Documents by Type */}
        <div className="eaw-card">
          <h3 className="text-sm font-semibold text-eaw-font mb-3">Documents by Type</h3>
          {docTypeData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={docTypeData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  dataKey="value"
                  nameKey="name"
                  paddingAngle={2}
                >
                  {docTypeData.map((entry, idx) => (
                    <Cell key={idx} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(val: number) => val.toLocaleString()} />
                <Legend
                  verticalAlign="bottom"
                  height={40}
                  formatter={(value: string) => (
                    <span className="text-xs text-eaw-font">{value}</span>
                  )}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center text-eaw-muted py-12 text-sm">No documents yet.</div>
          )}
        </div>

        {/* Spend by Category */}
        <div className="eaw-card">
          <h3 className="text-sm font-semibold text-eaw-font mb-3">Spend by Category</h3>
          {spendByCat.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={spendByCat} layout="vertical" barSize={20}>
                <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                <XAxis
                  type="number"
                  tick={{ fontSize: 11, fill: '#777' }}
                  tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
                />
                <YAxis
                  type="category"
                  dataKey="category"
                  tick={{ fontSize: 11, fill: '#777' }}
                  width={100}
                />
                <Tooltip formatter={(val: number) => formatCurrency(val)} />
                <Bar dataKey="total" fill="#337ab7" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center text-eaw-muted py-12 text-sm">
              No spend data available.
            </div>
          )}
        </div>
      </div>

      {/* Recent Documents */}
      <div className="eaw-card mb-6">
        <h3 className="text-sm font-semibold text-eaw-font mb-3">Recent Documents</h3>
        <div className="overflow-x-auto">
          <table className="eaw-table">
            <thead>
              <tr>
                <th>Filename</th>
                <th>Type</th>
                <th>Vendor</th>
                <th>Status</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {data.recent_documents.map((doc: any) => (
                <tr
                  key={doc.id}
                  className="cursor-pointer hover:bg-gray-50"
                  onClick={() => navigate(`/documents/${doc.id}`)}
                >
                  <td className="font-medium text-eaw-link hover:text-eaw-link-hover max-w-[200px] truncate">
                    {doc.original_filename}
                  </td>
                  <td>{formatDocType(doc.document_type)}</td>
                  <td>{doc.vendor_name || '--'}</td>
                  <td>
                    <span className={statusBadge(doc.processing_status)}>
                      {doc.processing_status}
                    </span>
                  </td>
                  <td className="text-eaw-muted whitespace-nowrap">
                    {formatDate(doc.created_at)}
                  </td>
                </tr>
              ))}
              {data.recent_documents.length === 0 && (
                <tr>
                  <td colSpan={5} className="text-center text-eaw-muted py-8">
                    No documents uploaded yet. Go to the Document Library to get started.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Processing Queue */}
      {data.processing_queue.length > 0 && (
        <div className="eaw-card">
          <h3 className="text-sm font-semibold text-eaw-font mb-3">Processing Queue</h3>
          <div className="overflow-x-auto">
            <table className="eaw-table">
              <thead>
                <tr>
                  <th>Filename</th>
                  <th>Status</th>
                  <th>Uploaded</th>
                </tr>
              </thead>
              <tbody>
                {data.processing_queue.map((doc: any) => (
                  <tr
                    key={doc.id}
                    className="cursor-pointer hover:bg-gray-50"
                    onClick={() => navigate(`/documents/${doc.id}`)}
                  >
                    <td className="font-medium text-eaw-link hover:text-eaw-link-hover max-w-[260px] truncate">
                      {doc.original_filename}
                    </td>
                    <td>
                      <span className={statusBadge(doc.processing_status)}>
                        {doc.processing_status}
                      </span>
                    </td>
                    <td className="text-eaw-muted whitespace-nowrap">
                      {formatDate(doc.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
