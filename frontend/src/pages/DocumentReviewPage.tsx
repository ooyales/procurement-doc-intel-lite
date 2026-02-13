import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Save,
  CheckCircle,
  RotateCcw,
  Loader2,
  AlertCircle,
  FileText,
} from 'lucide-react';
import client from '@/api/client';

interface DocumentDetail {
  id: string;
  original_filename: string;
  file_format: string;
  document_type: string | null;
  vendor_name: string | null;
  document_number: string | null;
  document_date: string | null;
  contract_number: string | null;
  task_order_number: string | null;
  total_amount: number | null;
  processing_status: string;
  extraction_confidence: number | null;
  extraction_method: string | null;
  ai_model_used: string | null;
  reviewed_by: string | null;
  reviewed_at: string | null;
  review_notes: string | null;
  notes: string | null;
  chunk_count: number;
  line_items: LineItemDetail[];
  line_item_count: number;
  created_at: string;
}

interface LineItemDetail {
  id: string;
  document_id: string;
  line_number: number | null;
  product_name: string | null;
  part_number: string | null;
  category: string | null;
  quantity: number | null;
  unit_price: number | null;
  extended_price: number | null;
  mapping_confidence: number | null;
  human_verified: number;
  manufacturer: string | null;
  product_description: string | null;
  clin: string | null;
  labor_category: string | null;
  labor_hours: number | null;
  labor_rate: number | null;
}

const DOC_TYPE_OPTIONS = [
  { value: '', label: 'Select type...' },
  { value: 'vendor_quote', label: 'Vendor Quote' },
  { value: 'purchase_order', label: 'Purchase Order' },
  { value: 'invoice', label: 'Invoice' },
  { value: 'bom', label: 'BOM' },
  { value: 'contract_mod', label: 'Contract Mod' },
  { value: 'timesheet', label: 'Timesheet' },
  { value: 'other', label: 'Other' },
];

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

function formatCurrency(val: number | null | undefined): string {
  if (val == null) return '--';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);
}

function confidenceColor(conf: number | null | undefined): string {
  if (conf == null) return 'bg-gray-100';
  if (conf >= 0.9) return 'bg-green-100 text-green-800';
  if (conf >= 0.7) return 'bg-yellow-100 text-yellow-800';
  return 'bg-red-100 text-red-800';
}

function confidenceBarColor(conf: number | null | undefined): string {
  if (conf == null) return 'bg-gray-300';
  if (conf >= 0.9) return 'bg-green-500';
  if (conf >= 0.7) return 'bg-yellow-500';
  return 'bg-red-500';
}

export default function DocumentReviewPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [doc, setDoc] = useState<DocumentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [approving, setApproving] = useState(false);
  const [reprocessing, setReprocessing] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Metadata form state
  const [metaForm, setMetaForm] = useState({
    vendor_name: '',
    document_number: '',
    document_date: '',
    document_type: '',
    contract_number: '',
    task_order_number: '',
    total_amount: '',
  });

  // Inline editing
  const [editingCell, setEditingCell] = useState<{ itemId: string; field: string } | null>(null);
  const [editValue, setEditValue] = useState('');

  const fetchDocument = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      const res = await client.get(`/documents/${id}`);
      const d = res.data;
      setDoc(d);
      setMetaForm({
        vendor_name: d.vendor_name || '',
        document_number: d.document_number || '',
        document_date: d.document_date || '',
        document_type: d.document_type || '',
        contract_number: d.contract_number || '',
        task_order_number: d.task_order_number || '',
        total_amount: d.total_amount != null ? String(d.total_amount) : '',
      });
    } catch {
      setMessage({ type: 'error', text: 'Failed to load document.' });
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchDocument();
  }, [fetchDocument]);

  const handleSaveMetadata = async () => {
    if (!id) return;
    setSaving(true);
    setMessage(null);
    try {
      const payload: any = { ...metaForm };
      payload.total_amount = metaForm.total_amount ? parseFloat(metaForm.total_amount) : null;
      await client.put(`/documents/${id}`, payload);
      setMessage({ type: 'success', text: 'Metadata saved.' });
      fetchDocument();
    } catch (err: any) {
      const msg = err?.response?.data?.error || 'Save failed.';
      setMessage({ type: 'error', text: msg });
    } finally {
      setSaving(false);
    }
  };

  const handleApprove = async () => {
    if (!id) return;
    setApproving(true);
    setMessage(null);
    try {
      await client.put(`/documents/${id}/approve`);
      setMessage({ type: 'success', text: 'Document approved and marked complete.' });
      fetchDocument();
    } catch (err: any) {
      const msg = err?.response?.data?.error || 'Approve failed.';
      setMessage({ type: 'error', text: msg });
    } finally {
      setApproving(false);
    }
  };

  const handleReprocess = async () => {
    if (!id) return;
    if (!confirm('This will clear all extracted data and re-process. Continue?')) return;
    setReprocessing(true);
    setMessage(null);
    try {
      await client.put(`/documents/${id}/reprocess`);
      setMessage({ type: 'success', text: 'Document reset. Run processing again from the library.' });
      fetchDocument();
    } catch (err: any) {
      const msg = err?.response?.data?.error || 'Reprocess failed.';
      setMessage({ type: 'error', text: msg });
    } finally {
      setReprocessing(false);
    }
  };

  const startCellEdit = (itemId: string, field: string, currentValue: any) => {
    setEditingCell({ itemId, field });
    setEditValue(currentValue != null ? String(currentValue) : '');
  };

  const saveCellEdit = async () => {
    if (!editingCell) return;
    const { itemId, field } = editingCell;

    let parsedValue: any = editValue;
    if (['quantity', 'unit_price', 'extended_price', 'mapping_confidence', 'labor_hours', 'labor_rate'].includes(field)) {
      parsedValue = editValue ? parseFloat(editValue) : null;
    }
    if (field === 'human_verified') {
      parsedValue = editValue === '1' || editValue === 'true' ? 1 : 0;
    }

    try {
      await client.put(`/line-items/${itemId}`, { [field]: parsedValue });
      fetchDocument();
    } catch {
      // Silent fail on inline edit
    }
    setEditingCell(null);
    setEditValue('');
  };

  const handleVerifyToggle = async (item: LineItemDetail) => {
    const newVal = item.human_verified ? 0 : 1;
    try {
      await client.put(`/line-items/${item.id}`, { human_verified: newVal });
      fetchDocument();
    } catch {
      // Silent fail
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 size={32} className="animate-spin text-eaw-primary" />
      </div>
    );
  }

  if (!doc) {
    return (
      <div className="text-center py-16">
        <AlertCircle size={32} className="mx-auto text-eaw-muted mb-2" />
        <p className="text-eaw-muted">Document not found.</p>
        <button className="btn-secondary mt-4" onClick={() => navigate('/documents')}>
          Back to Library
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* Back Button */}
      <button
        className="flex items-center gap-1 text-sm text-eaw-link hover:text-eaw-link-hover mb-4"
        onClick={() => navigate('/documents')}
      >
        <ArrowLeft size={16} />
        Back to Document Library
      </button>

      {/* Page Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <FileText size={18} className="text-eaw-primary" />
          <div>
            <h1 className="text-lg font-bold text-eaw-font">{doc.original_filename}</h1>
            <span className={`${statusBadge(doc.processing_status)} mt-1`}>
              {doc.processing_status}
            </span>
          </div>
        </div>
      </div>

      {/* Messages */}
      {message && (
        <div
          className={`mb-4 flex items-center gap-2 p-3 rounded text-sm ${
            message.type === 'success'
              ? 'bg-green-50 border border-green-200 text-green-700'
              : 'bg-red-50 border border-red-200 text-red-700'
          }`}
        >
          {message.type === 'success' ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
          <span>{message.text}</span>
        </div>
      )}

      {/* Two-Column Layout */}
      <div className="flex gap-6 flex-col lg:flex-row">
        {/* Left Panel: Metadata */}
        <div className="w-full lg:w-2/5 space-y-4">
          <div className="eaw-card">
            <h3 className="text-sm font-semibold text-eaw-font mb-4">Document Metadata</h3>
            <div className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-eaw-muted mb-1">Vendor</label>
                <input
                  type="text"
                  className="input-field"
                  value={metaForm.vendor_name}
                  onChange={(e) => setMetaForm((f) => ({ ...f, vendor_name: e.target.value }))}
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-eaw-muted mb-1">Document Number</label>
                <input
                  type="text"
                  className="input-field"
                  value={metaForm.document_number}
                  onChange={(e) => setMetaForm((f) => ({ ...f, document_number: e.target.value }))}
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-eaw-muted mb-1">Document Date</label>
                <input
                  type="text"
                  className="input-field"
                  value={metaForm.document_date}
                  onChange={(e) => setMetaForm((f) => ({ ...f, document_date: e.target.value }))}
                  placeholder="YYYY-MM-DD"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-eaw-muted mb-1">Document Type</label>
                <select
                  className="select-field"
                  value={metaForm.document_type}
                  onChange={(e) => setMetaForm((f) => ({ ...f, document_type: e.target.value }))}
                >
                  {DOC_TYPE_OPTIONS.map((o) => (
                    <option key={o.value} value={o.value}>{o.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-eaw-muted mb-1">Contract Number</label>
                <input
                  type="text"
                  className="input-field"
                  value={metaForm.contract_number}
                  onChange={(e) => setMetaForm((f) => ({ ...f, contract_number: e.target.value }))}
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-eaw-muted mb-1">Task Order Number</label>
                <input
                  type="text"
                  className="input-field"
                  value={metaForm.task_order_number}
                  onChange={(e) => setMetaForm((f) => ({ ...f, task_order_number: e.target.value }))}
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-eaw-muted mb-1">Total Amount</label>
                <input
                  type="number"
                  step="0.01"
                  className="input-field"
                  value={metaForm.total_amount}
                  onChange={(e) => setMetaForm((f) => ({ ...f, total_amount: e.target.value }))}
                />
              </div>

              <button
                className="btn-primary w-full justify-center mt-2"
                onClick={handleSaveMetadata}
                disabled={saving}
              >
                {saving ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />}
                {saving ? 'Saving...' : 'Save Metadata'}
              </button>
            </div>
          </div>

          {/* Extraction Confidence */}
          <div className="eaw-card">
            <h3 className="text-sm font-semibold text-eaw-font mb-3">Extraction Confidence</h3>
            {doc.extraction_confidence != null ? (
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-eaw-muted">Overall Confidence</span>
                  <span className="text-sm font-semibold text-eaw-font">
                    {(doc.extraction_confidence * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div
                    className={`${confidenceBarColor(doc.extraction_confidence)} rounded-full h-2.5 transition-all`}
                    style={{ width: `${doc.extraction_confidence * 100}%` }}
                  />
                </div>
                <div className="flex justify-between mt-2 text-xs text-eaw-muted">
                  <span>Method: {doc.extraction_method || 'Unknown'}</span>
                  <span>AI: {doc.ai_model_used || 'N/A'}</span>
                </div>
              </div>
            ) : (
              <p className="text-sm text-eaw-muted">Not yet processed.</p>
            )}
          </div>

          {/* Document Text / Notes */}
          <div className="eaw-card">
            <h3 className="text-sm font-semibold text-eaw-font mb-3">Document Text</h3>
            {doc.notes ? (
              <pre className="bg-gray-50 rounded p-3 text-xs text-eaw-font max-h-60 overflow-y-auto whitespace-pre-wrap font-mono">
                {doc.notes}
              </pre>
            ) : doc.chunk_count > 0 ? (
              <p className="text-sm text-eaw-muted">
                {doc.chunk_count} text chunks extracted. Full text available in RAG search.
              </p>
            ) : (
              <p className="text-sm text-eaw-muted">No text extracted yet.</p>
            )}
          </div>
        </div>

        {/* Right Panel: Line Items */}
        <div className="w-full lg:w-3/5">
          <div className="eaw-card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-eaw-font">
                Extracted Line Items ({doc.line_items?.length || 0})
              </h3>
            </div>

            {doc.line_items && doc.line_items.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="eaw-table text-xs">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Product Name</th>
                      <th>Part #</th>
                      <th>Category</th>
                      <th>Qty</th>
                      <th>Unit Price</th>
                      <th>Ext Price</th>
                      <th>Confidence</th>
                      <th>Verified</th>
                    </tr>
                  </thead>
                  <tbody>
                    {doc.line_items.map((item, idx) => (
                      <tr key={item.id}>
                        <td className="text-eaw-muted">{item.line_number || idx + 1}</td>

                        {/* Product Name - editable */}
                        <td
                          className="cursor-pointer hover:bg-blue-50 max-w-[180px] truncate"
                          onClick={() => startCellEdit(item.id, 'product_name', item.product_name)}
                          title={item.product_name || ''}
                        >
                          {editingCell?.itemId === item.id && editingCell?.field === 'product_name' ? (
                            <input
                              type="text"
                              className="input-field !py-0.5 !text-xs"
                              value={editValue}
                              onChange={(e) => setEditValue(e.target.value)}
                              onBlur={saveCellEdit}
                              onKeyDown={(e) => e.key === 'Enter' && saveCellEdit()}
                              autoFocus
                            />
                          ) : (
                            item.product_name || '--'
                          )}
                        </td>

                        {/* Part # - editable */}
                        <td
                          className="cursor-pointer hover:bg-blue-50"
                          onClick={() => startCellEdit(item.id, 'part_number', item.part_number)}
                        >
                          {editingCell?.itemId === item.id && editingCell?.field === 'part_number' ? (
                            <input
                              type="text"
                              className="input-field !py-0.5 !text-xs"
                              value={editValue}
                              onChange={(e) => setEditValue(e.target.value)}
                              onBlur={saveCellEdit}
                              onKeyDown={(e) => e.key === 'Enter' && saveCellEdit()}
                              autoFocus
                            />
                          ) : (
                            item.part_number || '--'
                          )}
                        </td>

                        {/* Category - editable */}
                        <td
                          className="cursor-pointer hover:bg-blue-50"
                          onClick={() => startCellEdit(item.id, 'category', item.category)}
                        >
                          {editingCell?.itemId === item.id && editingCell?.field === 'category' ? (
                            <input
                              type="text"
                              className="input-field !py-0.5 !text-xs"
                              value={editValue}
                              onChange={(e) => setEditValue(e.target.value)}
                              onBlur={saveCellEdit}
                              onKeyDown={(e) => e.key === 'Enter' && saveCellEdit()}
                              autoFocus
                            />
                          ) : (
                            item.category || '--'
                          )}
                        </td>

                        {/* Qty - editable */}
                        <td
                          className="cursor-pointer hover:bg-blue-50 text-right"
                          onClick={() => startCellEdit(item.id, 'quantity', item.quantity)}
                        >
                          {editingCell?.itemId === item.id && editingCell?.field === 'quantity' ? (
                            <input
                              type="number"
                              className="input-field !py-0.5 !text-xs w-16"
                              value={editValue}
                              onChange={(e) => setEditValue(e.target.value)}
                              onBlur={saveCellEdit}
                              onKeyDown={(e) => e.key === 'Enter' && saveCellEdit()}
                              autoFocus
                            />
                          ) : (
                            item.quantity ?? '--'
                          )}
                        </td>

                        {/* Unit Price - editable */}
                        <td
                          className="cursor-pointer hover:bg-blue-50 text-right whitespace-nowrap"
                          onClick={() => startCellEdit(item.id, 'unit_price', item.unit_price)}
                        >
                          {editingCell?.itemId === item.id && editingCell?.field === 'unit_price' ? (
                            <input
                              type="number"
                              step="0.01"
                              className="input-field !py-0.5 !text-xs w-20"
                              value={editValue}
                              onChange={(e) => setEditValue(e.target.value)}
                              onBlur={saveCellEdit}
                              onKeyDown={(e) => e.key === 'Enter' && saveCellEdit()}
                              autoFocus
                            />
                          ) : (
                            formatCurrency(item.unit_price)
                          )}
                        </td>

                        {/* Ext Price - editable */}
                        <td
                          className="cursor-pointer hover:bg-blue-50 text-right whitespace-nowrap"
                          onClick={() => startCellEdit(item.id, 'extended_price', item.extended_price)}
                        >
                          {editingCell?.itemId === item.id && editingCell?.field === 'extended_price' ? (
                            <input
                              type="number"
                              step="0.01"
                              className="input-field !py-0.5 !text-xs w-20"
                              value={editValue}
                              onChange={(e) => setEditValue(e.target.value)}
                              onBlur={saveCellEdit}
                              onKeyDown={(e) => e.key === 'Enter' && saveCellEdit()}
                              autoFocus
                            />
                          ) : (
                            formatCurrency(item.extended_price)
                          )}
                        </td>

                        {/* Confidence */}
                        <td className="text-center">
                          <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${confidenceColor(item.mapping_confidence)}`}>
                            {item.mapping_confidence != null
                              ? `${(item.mapping_confidence * 100).toFixed(0)}%`
                              : '--'}
                          </span>
                        </td>

                        {/* Human Verified */}
                        <td className="text-center">
                          <input
                            type="checkbox"
                            checked={!!item.human_verified}
                            onChange={() => handleVerifyToggle(item)}
                            className="h-4 w-4 rounded border-gray-300 text-eaw-primary focus:ring-eaw-primary cursor-pointer"
                          />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-center text-eaw-muted py-8">
                No line items extracted yet. Process the document to extract data.
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Action Bar */}
      <div className="mt-6 flex items-center gap-3 justify-end border-t border-gray-100 pt-4">
        <button
          className="btn-secondary"
          onClick={handleReprocess}
          disabled={reprocessing}
        >
          {reprocessing ? <Loader2 size={14} className="animate-spin" /> : <RotateCcw size={14} />}
          {reprocessing ? 'Resetting...' : 'Re-process'}
        </button>
        <button
          className="btn-success"
          onClick={handleApprove}
          disabled={approving || doc.processing_status === 'complete'}
        >
          {approving ? <Loader2 size={14} className="animate-spin" /> : <CheckCircle size={14} />}
          {approving ? 'Approving...' : doc.processing_status === 'complete' ? 'Approved' : 'Approve'}
        </button>
      </div>
    </div>
  );
}
