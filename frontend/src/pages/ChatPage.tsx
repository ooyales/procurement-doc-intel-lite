import { useEffect, useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  MessageSquare,
  Send,
  RotateCcw,
  Loader2,
  FileText,
  User,
  Bot,
} from 'lucide-react';
import client from '@/api/client';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sources?: Array<{
    document_number: string | null;
    document_id: string;
    original_filename?: string;
  }>;
}

export default function ChatPage() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Scroll to bottom on new message
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Load suggestions on mount
  useEffect(() => {
    setLoadingSuggestions(true);
    client
      .get('/chat/suggestions')
      .then((res) => {
        setSuggestions(res.data.suggestions || []);
      })
      .catch(() => {
        setSuggestions([
          'What is our total spend across all documents?',
          'Which vendors have the highest total spend?',
          'Show me a breakdown of spend by category.',
        ]);
      })
      .finally(() => {
        setLoadingSuggestions(false);
      });
  }, []);

  const sendMessage = async (text: string) => {
    if (!text.trim() || sending) return;

    const userMessage: ChatMessage = { role: 'user', content: text.trim() };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput('');
    setSending(true);

    // Build history for API (excluding the current message)
    const history = messages.map((m) => ({
      role: m.role,
      content: m.content,
    }));

    try {
      const res = await client.post('/chat', {
        message: text.trim(),
        history,
      });

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: res.data.answer || 'I could not generate a response.',
        sources: res.data.sources || [],
      };

      setMessages([...updatedMessages, assistantMessage]);
    } catch (err: any) {
      const errMsg =
        err?.response?.data?.answer ||
        err?.response?.data?.error ||
        'An error occurred while processing your question. Please try again.';
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: errMsg,
        sources: [],
      };
      setMessages([...updatedMessages, errorMessage]);
    } finally {
      setSending(false);
      inputRef.current?.focus();
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    sendMessage(suggestion);
  };

  const handleNewChat = () => {
    setMessages([]);
    setInput('');
    inputRef.current?.focus();
  };

  return (
    <div className="flex flex-col" style={{ height: 'calc(100vh - 120px)' }}>
      {/* Page Header */}
      <div className="mb-4 flex items-center justify-between flex-shrink-0">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <MessageSquare size={18} className="text-eaw-primary" />
            <h1 className="text-xl font-bold text-eaw-font">Procurement Chat</h1>
          </div>
          <p className="text-sm text-eaw-muted">
            Ask questions about your procurement documents
          </p>
        </div>
        {messages.length > 0 && (
          <button className="btn-secondary !text-xs" onClick={handleNewChat}>
            <RotateCcw size={14} />
            New Chat
          </button>
        )}
      </div>

      {/* Chat Container */}
      <div className="flex-1 flex flex-col bg-white rounded shadow-eaw overflow-hidden">
        {/* Message List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            /* Empty State: Show suggestions */
            <div className="flex flex-col items-center justify-center h-full">
              <MessageSquare size={48} className="text-gray-200 mb-4" />
              <h3 className="text-sm font-semibold text-eaw-font mb-2">
                What would you like to know?
              </h3>
              <p className="text-xs text-eaw-muted mb-6 text-center max-w-md">
                Ask questions about your procurement documents, spending, vendors, or line items.
                The AI will search your uploaded documents to provide answers.
              </p>

              {loadingSuggestions ? (
                <Loader2 size={16} className="animate-spin text-eaw-muted" />
              ) : (
                <div className="flex flex-wrap justify-center gap-2 max-w-xl">
                  {suggestions.map((s, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSuggestionClick(s)}
                      className="px-3 py-2 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-full text-xs text-eaw-primary transition-colors text-left"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ) : (
            /* Message Bubbles */
            <>
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {msg.role === 'assistant' && (
                    <div className="flex-shrink-0 w-7 h-7 bg-eaw-primary rounded-full flex items-center justify-center">
                      <Bot size={14} className="text-white" />
                    </div>
                  )}

                  <div
                    className={`max-w-[75%] ${
                      msg.role === 'user'
                        ? 'bg-blue-50 rounded-2xl rounded-tr-sm px-4 py-3'
                        : 'eaw-card !shadow-sm'
                    }`}
                  >
                    {/* Message content */}
                    <div className="text-sm text-eaw-font whitespace-pre-wrap leading-relaxed">
                      {msg.content.split('\n').map((paragraph, pIdx) => (
                        <p key={pIdx} className={pIdx > 0 ? 'mt-2' : ''}>
                          {paragraph}
                        </p>
                      ))}
                    </div>

                    {/* Sources */}
                    {msg.role === 'assistant' && msg.sources && msg.sources.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-gray-100">
                        <p className="text-xs font-medium text-eaw-muted mb-1.5">Sources:</p>
                        <div className="flex flex-wrap gap-1.5">
                          {msg.sources.map((source, sIdx) => (
                            <button
                              key={sIdx}
                              onClick={() => navigate(`/documents/${source.document_id}`)}
                              className="inline-flex items-center gap-1 px-2 py-0.5 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded text-xs text-eaw-primary transition-colors"
                            >
                              <FileText size={10} />
                              {source.document_number || source.original_filename || `Doc ${sIdx + 1}`}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {msg.role === 'user' && (
                    <div className="flex-shrink-0 w-7 h-7 bg-gray-200 rounded-full flex items-center justify-center">
                      <User size={14} className="text-gray-600" />
                    </div>
                  )}
                </div>
              ))}

              {/* Thinking indicator */}
              {sending && (
                <div className="flex gap-3 justify-start">
                  <div className="flex-shrink-0 w-7 h-7 bg-eaw-primary rounded-full flex items-center justify-center">
                    <Bot size={14} className="text-white" />
                  </div>
                  <div className="eaw-card !shadow-sm">
                    <div className="flex items-center gap-2 text-sm text-eaw-muted">
                      <Loader2 size={14} className="animate-spin" />
                      <span>
                        Thinking
                        <span className="inline-block animate-pulse">.</span>
                        <span className="inline-block animate-pulse" style={{ animationDelay: '0.2s' }}>.</span>
                        <span className="inline-block animate-pulse" style={{ animationDelay: '0.4s' }}>.</span>
                      </span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 p-4 bg-gray-50 flex-shrink-0">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              className="input-field flex-1 resize-none"
              placeholder="Ask about your procurement documents..."
              rows={1}
              style={{ minHeight: '40px', maxHeight: '120px' }}
              disabled={sending}
            />
            <button
              type="submit"
              disabled={sending || !input.trim()}
              className="btn-primary !px-4 self-end"
            >
              {sending ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <Send size={16} />
              )}
            </button>
          </form>
          <p className="text-xs text-eaw-muted mt-2">
            Press Enter to send, Shift+Enter for new line.
          </p>
        </div>
      </div>
    </div>
  );
}
