import { useEffect, useState, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileText,
  Upload,
  Search,
  Eye,
  Play,
  Trash2,
  Loader2,
  CheckCircle,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  File,
  FileSpreadsheet,
} from 'lucide-react';
import client from '@/api/client';

interface DocumentItem {
  id: string;
  original_filename: string;
  file_format: string;
  document_type: string | null;
  vendor_name: string | null;
  document_number: string | null;
  total_amount: number | null;
  processing_status: string;
  line_item_count: number;
  created_at: string;
}

interface ListResponse {
  items: DocumentItem[];
  total: number;
  page: number;
  per_page: number;
}

const DOC_TYPES = [
  { value: '', label: 'All Types' },
  { value: 'vendor_quote', label: 'Vendor Quote' },
  { value: 'purchase_order', label: 'Purchase Order' },
  { value: 'invoice', label: 'Invoice' },
  { value: 'bom', label: 'BOM' },
  { value: 'contract_mod', label: 'Contract Mod' },
  { value: 'timesheet', label: 'Timesheet' },
  { value: 'other', label: 'Other' },
];

const STATUSES = [
  { value: '', label: 'All Statuses' },
  { value: 'uploaded', label: 'Uploaded' },
  { value: 'extracting', label: 'Extracting' },
  { value: 'mapping', label: 'Mapping' },
  { value: 'review', label: 'Review' },
  { value: 'complete', label: 'Complete' },
  { value: 'failed', label: 'Failed' },
];

function formatCurrency(val: number | null | undefined): string {
  if (val == null) return '--';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);
}

function formatDocType(type: string | null | undefined): string {
  if (!type) return '--';
  return type
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
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

function FileFormatIcon({ format }: { format: string }) {
  switch (format) {
    case 'pdf':
      return <File size={16} className="text-red-500" />;
    case 'xlsx':
    case 'xls':
    case 'csv':
      return <FileSpreadsheet size={16} className="text-green-600" />;
    case 'docx':
    case 'doc':
      return <FileText size={16} className="text-blue-600" />;
    default:
      return <File size={16} className="text-gray-400" />;
  }
}

export default function DocumentLibraryPage() {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Upload state
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadMessage, setUploadMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [dragOver, setDragOver] = useState(false);

  // Filters
  const [search, setSearch] = useState('');
  const [docType, setDocType] = useState('');
  const [status, setStatus] = useState('');
  const [vendor, setVendor] = useState('');
  const [page, setPage] = useState(1);
  const perPage = 25;

  // Data
  const [data, setData] = useState<ListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [processingIds, setProcessingIds] = useState<Set<string>>(new Set());

  const fetchDocuments = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string | number> = { page, per_page: perPage };
      if (search) params.search = search;
      if (docType) params.document_type = docType;
      if (status) params.processing_status = status;
      if (vendor) params.vendor_name = vendor;

      const res = await client.get('/documents', { params });
      setData(res.data);
    } catch {
      // Silently fail
    } finally {
      setLoading(false);
    }
  }, [page, search, docType, status, vendor]);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  // Reset page when filters change
  useEffect(() => {
    setPage(1);
  }, [search, docType, status, vendor]);

  const handleUpload = async (file: File) => {
    const ext = file.name.split('.').pop()?.toLowerCase() || '';
    const allowed = ['pdf', 'xlsx', 'xls', 'docx', 'doc', 'csv'];
    if (!allowed.includes(ext)) {
      setUploadMessage({ type: 'error', text: `Unsupported format: .${ext}. Accepted: ${allowed.join(', ')}` });
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setUploadMessage(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      await client.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) => {
          if (e.total) {
            setUploadProgress(Math.round((e.loaded / e.total) * 100));
          }
        },
      });
      setUploadMessage({ type: 'success', text: `"${file.name}" uploaded successfully.` });
      fetchDocuments();
    } catch (err: any) {
      const msg = err?.response?.data?.error || 'Upload failed. Please try again.';
      setUploadMessage({ type: 'error', text: msg });
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) handleUpload(files[0]);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => setDragOver(false);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) handleUpload(files[0]);
    e.target.value = '';
  };

  const handleProcess = async (docId: string) => {
    setProcessingIds((prev) => new Set(prev).add(docId));
    try {
      await client.post(`/documents/${docId}/process`);
      fetchDocuments();
    } catch (err: any) {
      const msg = err?.response?.data?.error || 'Processing failed.';
      setUploadMessage({ type: 'error', text: msg });
    } finally {
      setProcessingIds((prev) => {
        const next = new Set(prev);
        next.delete(docId);
        return next;
      });
    }
  };

  const handleDelete = async (docId: string, filename: string) => {
    if (!confirm(`Delete "${filename}"? This cannot be undone.`)) return;
    try {
      await client.delete(`/documents/${docId}`);
      fetchDocuments();
    } catch {
      setUploadMessage({ type: 'error', text: 'Delete failed.' });
    }
  };

  const totalPages = data ? Math.ceil(data.total / perPage) : 1;

  return (
    <div>
      {/* Page Header */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-1">
          <FileText size={18} className="text-eaw-primary" />
          <h1 className="text-xl font-bold text-eaw-font">Document Library</h1>
        </div>
        <p className="text-sm text-eaw-muted">
          Upload procurement documents and manage processing.
        </p>
      </div>

      {/* Upload Zone */}
      <div className="eaw-card mb-6">
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragOver ? 'border-eaw-primary bg-blue-50' : 'border-gray-300 hover:border-gray-400'
          }`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        >
          <Upload size={32} className="mx-auto mb-3 text-gray-400" />
          <p className="text-sm text-eaw-font mb-2">
            Drag and drop a file here, or{' '}
            <button
              onClick={() => fileInputRef.current?.click()}
              className="text-eaw-link hover:text-eaw-link-hover font-medium"
              disabled={uploading}
            >
              Browse Files
            </button>
          </p>
          <p className="text-xs text-eaw-muted">
            Accepted formats: PDF, XLSX, DOCX, CSV
          </p>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.xlsx,.xls,.docx,.doc,.csv"
            onChange={handleFileSelect}
            className="hidden"
          />

          {/* Upload Progress */}
          {uploading && (
            <div className="mt-4 max-w-xs mx-auto">
              <div className="flex items-center gap-2 mb-1">
                <Loader2 size={14} className="animate-spin text-eaw-primary" />
                <span className="text-xs text-eaw-font">Uploading... {uploadProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-1.5">
                <div
                  className="bg-eaw-primary rounded-full h-1.5 transition-all"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Upload messages */}
        {uploadMessage && (
          <div
            className={`mt-3 flex items-center gap-2 p-3 rounded text-sm ${
              uploadMessage.type === 'success'
                ? 'bg-green-50 border border-green-200 text-green-700'
                : 'bg-red-50 border border-red-200 text-red-700'
            }`}
          >
            {uploadMessage.type === 'success' ? (
              <CheckCircle size={16} className="flex-shrink-0" />
            ) : (
              <AlertCircle size={16} className="flex-shrink-0" />
            )}
            <span>{uploadMessage.text}</span>
            <button
              className="ml-auto text-xs underline"
              onClick={() => setUploadMessage(null)}
            >
              dismiss
            </button>
          </div>
        )}
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
                placeholder="Search filename, vendor, doc #..."
              />
            </div>
          </div>
          <div className="min-w-[150px]">
            <label className="block text-xs font-medium text-eaw-muted mb-1">Document Type</label>
            <select
              value={docType}
              onChange={(e) => setDocType(e.target.value)}
              className="select-field"
            >
              {DOC_TYPES.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>
          <div className="min-w-[140px]">
            <label className="block text-xs font-medium text-eaw-muted mb-1">Status</label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="select-field"
            >
              {STATUSES.map((s) => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </select>
          </div>
          <div className="min-w-[150px]">
            <label className="block text-xs font-medium text-eaw-muted mb-1">Vendor</label>
            <input
              type="text"
              value={vendor}
              onChange={(e) => setVendor(e.target.value)}
              className="input-field"
              placeholder="Filter by vendor"
            />
          </div>
        </div>
      </div>

      {/* Document Table */}
      <div className="eaw-card">
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
                    <th>Filename</th>
                    <th>Type</th>
                    <th>Vendor</th>
                    <th>Doc #</th>
                    <th>Amount</th>
                    <th>Status</th>
                    <th>Items</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data?.items.map((doc) => (
                    <tr key={doc.id}>
                      <td>
                        <div className="flex items-center gap-2 max-w-[220px]">
                          <FileFormatIcon format={doc.file_format} />
                          <span className="truncate font-medium text-eaw-font" title={doc.original_filename}>
                            {doc.original_filename}
                          </span>
                        </div>
                      </td>
                      <td>{formatDocType(doc.document_type)}</td>
                      <td>{doc.vendor_name || '--'}</td>
                      <td className="text-eaw-muted">{doc.document_number || '--'}</td>
                      <td className="whitespace-nowrap">{formatCurrency(doc.total_amount)}</td>
                      <td>
                        <span className={statusBadge(doc.processing_status)}>
                          {doc.processing_status}
                        </span>
                      </td>
                      <td className="text-center">{doc.line_item_count}</td>
                      <td>
                        <div className="flex items-center gap-1.5">
                          <button
                            className="btn-secondary !py-1 !px-2 !text-xs"
                            onClick={() => navigate(`/documents/${doc.id}`)}
                            title="View"
                          >
                            <Eye size={14} />
                          </button>
                          {doc.processing_status === 'uploaded' && (
                            <button
                              className="btn-primary !py-1 !px-2 !text-xs"
                              onClick={() => handleProcess(doc.id)}
                              disabled={processingIds.has(doc.id)}
                              title="Process with AI"
                            >
                              {processingIds.has(doc.id) ? (
                                <Loader2 size={14} className="animate-spin" />
                              ) : (
                                <Play size={14} />
                              )}
                            </button>
                          )}
                          <button
                            className="btn-secondary !py-1 !px-2 !text-xs text-red-500 hover:text-red-700"
                            onClick={() => handleDelete(doc.id, doc.original_filename)}
                            title="Delete"
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {(!data || data.items.length === 0) && (
                    <tr>
                      <td colSpan={8} className="text-center text-eaw-muted py-12">
                        No documents found. Upload a file above to get started.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {data && data.total > perPage && (
              <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
                <span className="text-xs text-eaw-muted">
                  Showing {(page - 1) * perPage + 1}--
                  {Math.min(page * perPage, data.total)} of {data.total}
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
    </div>
  );
}
