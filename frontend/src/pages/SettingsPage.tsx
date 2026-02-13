import { useEffect, useState } from 'react';
import {
  Settings,
  CheckCircle,
  XCircle,
  Loader2,
  Shield,
  Database,
  Info,
  Brain,
  Zap,
} from 'lucide-react';
import client from '@/api/client';

interface HealthStatus {
  status: string;
  timestamp: string;
  app: string;
}

export default function SettingsPage() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [healthLoading, setHealthLoading] = useState(true);
  const [healthError, setHealthError] = useState(false);

  useEffect(() => {
    setHealthLoading(true);
    client
      .get('/health')
      .then((res) => {
        setHealth(res.data);
        setHealthError(false);
      })
      .catch(() => {
        setHealthError(true);
      })
      .finally(() => {
        setHealthLoading(false);
      });
  }, []);

  return (
    <div>
      {/* Page Header */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-1">
          <Settings size={18} className="text-eaw-primary" />
          <h1 className="text-xl font-bold text-eaw-font">Settings</h1>
        </div>
        <p className="text-sm text-eaw-muted">
          System configuration and field mapping management.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* API Status */}
        <div className="eaw-card">
          <div className="flex items-center gap-2 mb-4">
            <Zap size={16} className="text-eaw-primary" />
            <h3 className="text-sm font-semibold text-eaw-font">API Status</h3>
          </div>

          {healthLoading ? (
            <div className="flex items-center gap-2 py-4">
              <Loader2 size={16} className="animate-spin text-eaw-primary" />
              <span className="text-sm text-eaw-muted">Checking API health...</span>
            </div>
          ) : healthError ? (
            <div className="space-y-3">
              <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded">
                <XCircle size={16} className="text-red-500 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-red-700">API Unreachable</p>
                  <p className="text-xs text-red-600">
                    Could not connect to the backend API. Check that the server is running.
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded">
                <CheckCircle size={16} className="text-green-500 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-green-700">API Healthy</p>
                  <p className="text-xs text-green-600">
                    Backend is running and responding to requests.
                  </p>
                </div>
              </div>

              <div className="space-y-2 pt-2">
                <div className="flex justify-between text-xs">
                  <span className="text-eaw-muted">Application</span>
                  <span className="text-eaw-font font-medium">{health?.app || '--'}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-eaw-muted">Status</span>
                  <span className="text-eaw-font font-medium">{health?.status || '--'}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-eaw-muted">Last Check</span>
                  <span className="text-eaw-font">
                    {health?.timestamp
                      ? new Date(health.timestamp).toLocaleString()
                      : '--'}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* AI Configuration */}
        <div className="eaw-card">
          <div className="flex items-center gap-2 mb-4">
            <Brain size={16} className="text-eaw-primary" />
            <h3 className="text-sm font-semibold text-eaw-font">AI Configuration</h3>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
              <div className="flex items-center gap-2">
                <Shield size={14} className="text-gray-500" />
                <span className="text-sm text-eaw-font">ANTHROPIC_API_KEY</span>
              </div>
              <span className="badge-muted">
                Server-side
              </span>
            </div>
            <p className="text-xs text-eaw-muted">
              The Claude API key is configured server-side via the ANTHROPIC_API_KEY environment
              variable. Document processing and chat features require a valid API key.
            </p>

            <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
              <div className="flex items-center gap-2">
                <Database size={14} className="text-gray-500" />
                <span className="text-sm text-eaw-font">Model</span>
              </div>
              <span className="text-xs text-eaw-font font-medium">claude-sonnet-4-5-20250929</span>
            </div>
            <p className="text-xs text-eaw-muted">
              Used for document field mapping, line item extraction, and procurement chat.
            </p>
          </div>
        </div>

        {/* Field Mappings */}
        <div className="eaw-card lg:col-span-2">
          <div className="flex items-center gap-2 mb-4">
            <Database size={16} className="text-eaw-primary" />
            <h3 className="text-sm font-semibold text-eaw-font">Field Mappings</h3>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded p-4 mb-4">
            <div className="flex items-start gap-2">
              <Info size={16} className="text-blue-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm text-blue-800 font-medium">Automatic Learning</p>
                <p className="text-xs text-blue-700 mt-1">
                  Field mappings are learned automatically as you review and correct extracted
                  data in the Document Review page. When you correct a field value for a line
                  item, the system remembers the mapping for that vendor&apos;s column format.
                  Over time, this improves extraction accuracy for repeat vendors.
                </p>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <h4 className="text-xs font-semibold text-eaw-muted uppercase tracking-wide">
              How Field Mapping Works
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-3 bg-gray-50 rounded">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-6 h-6 bg-eaw-primary text-white rounded-full flex items-center justify-center text-xs font-bold">
                    1
                  </div>
                  <span className="text-sm font-medium text-eaw-font">Upload</span>
                </div>
                <p className="text-xs text-eaw-muted">
                  Upload a vendor quote, invoice, or purchase order. The system extracts raw
                  tabular data and text.
                </p>
              </div>
              <div className="p-3 bg-gray-50 rounded">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-6 h-6 bg-eaw-primary text-white rounded-full flex items-center justify-center text-xs font-bold">
                    2
                  </div>
                  <span className="text-sm font-medium text-eaw-font">AI Mapping</span>
                </div>
                <p className="text-xs text-eaw-muted">
                  Claude analyzes column headers and data to map vendor-specific columns to
                  standard fields (product name, part number, price, etc.).
                </p>
              </div>
              <div className="p-3 bg-gray-50 rounded">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-6 h-6 bg-eaw-primary text-white rounded-full flex items-center justify-center text-xs font-bold">
                    3
                  </div>
                  <span className="text-sm font-medium text-eaw-font">Learn &amp; Improve</span>
                </div>
                <p className="text-xs text-eaw-muted">
                  When you correct a mapping during review, the system stores the correction.
                  Next time, the same vendor&apos;s format is recognized automatically with
                  higher confidence.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* About Section */}
        <div className="eaw-card lg:col-span-2">
          <div className="flex items-center gap-2 mb-4">
            <Info size={16} className="text-eaw-primary" />
            <h3 className="text-sm font-semibold text-eaw-font">About</h3>
          </div>

          <div className="space-y-3">
            <p className="text-sm text-eaw-font leading-relaxed">
              <strong>Procurement Doc Intel Lite</strong> is a document intelligence platform
              for federal IT procurement. It uses AI to extract, normalize, and analyze
              procurement documents including vendor quotes, purchase orders, invoices, and
              bills of materials.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4">
              <div>
                <h4 className="text-xs font-semibold text-eaw-muted uppercase tracking-wide mb-2">
                  Key Features
                </h4>
                <ul className="text-xs text-eaw-font space-y-1.5">
                  <li className="flex items-start gap-1.5">
                    <CheckCircle size={12} className="text-green-500 mt-0.5 flex-shrink-0" />
                    Multi-format document upload (PDF, XLSX, DOCX, CSV)
                  </li>
                  <li className="flex items-start gap-1.5">
                    <CheckCircle size={12} className="text-green-500 mt-0.5 flex-shrink-0" />
                    AI-powered field extraction and mapping
                  </li>
                  <li className="flex items-start gap-1.5">
                    <CheckCircle size={12} className="text-green-500 mt-0.5 flex-shrink-0" />
                    Human-in-the-loop review with inline editing
                  </li>
                  <li className="flex items-start gap-1.5">
                    <CheckCircle size={12} className="text-green-500 mt-0.5 flex-shrink-0" />
                    Canonical product catalog with price intelligence
                  </li>
                  <li className="flex items-start gap-1.5">
                    <CheckCircle size={12} className="text-green-500 mt-0.5 flex-shrink-0" />
                    IGCE (Independent Government Cost Estimate) generation
                  </li>
                  <li className="flex items-start gap-1.5">
                    <CheckCircle size={12} className="text-green-500 mt-0.5 flex-shrink-0" />
                    RAG-powered procurement chat assistant
                  </li>
                  <li className="flex items-start gap-1.5">
                    <CheckCircle size={12} className="text-green-500 mt-0.5 flex-shrink-0" />
                    Export to CSV/XLSX for further analysis
                  </li>
                </ul>
              </div>
              <div>
                <h4 className="text-xs font-semibold text-eaw-muted uppercase tracking-wide mb-2">
                  Technology Stack
                </h4>
                <ul className="text-xs text-eaw-font space-y-1.5">
                  <li className="flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 bg-blue-500 rounded-full flex-shrink-0" />
                    Flask + SQLAlchemy (Backend)
                  </li>
                  <li className="flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 bg-blue-500 rounded-full flex-shrink-0" />
                    React + TypeScript + Vite (Frontend)
                  </li>
                  <li className="flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 bg-blue-500 rounded-full flex-shrink-0" />
                    SQLite + FTS5 (Database)
                  </li>
                  <li className="flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 bg-blue-500 rounded-full flex-shrink-0" />
                    Anthropic Claude API (AI)
                  </li>
                  <li className="flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 bg-blue-500 rounded-full flex-shrink-0" />
                    Recharts (Data Visualization)
                  </li>
                  <li className="flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 bg-blue-500 rounded-full flex-shrink-0" />
                    Tailwind CSS (Styling)
                  </li>
                  <li className="flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 bg-blue-500 rounded-full flex-shrink-0" />
                    Docker Compose (Deployment)
                  </li>
                </ul>
              </div>
            </div>

            <div className="pt-3 border-t border-gray-100 mt-4">
              <p className="text-xs text-eaw-muted">
                Version 1.0.0 &mdash; Built for federal IT acquisition and contracting teams.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
