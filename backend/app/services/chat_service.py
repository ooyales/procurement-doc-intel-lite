import json
import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)

CHAT_SYSTEM_PROMPT = """You are a procurement document analyst assistant. You help users find information about their procurement documents, purchase orders, invoices, vendor quotes, and line items.

You have access to a database of procurement documents with extracted line items. When answering questions:
1. Be specific and cite source documents (document number, vendor, date)
2. Include prices, quantities, and other relevant numbers
3. If you're not sure about something, say so
4. Format currency values with $ and commas
5. Keep answers concise but complete

When search results are provided, base your answer ONLY on those results. Do not make up information."""

CHAT_QUERY_PROMPT = """Based on the user's question, I searched the procurement database and found these results:

{context}

User question: {question}

Please answer the question based on the search results above. Cite specific documents and line items. If the results don't contain enough information to answer, say so."""


class ChatService:
    """RAG-based chat service for procurement document Q&A."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def process_query(self, query: str, db_session, session_id: str = '__default__',
                      conversation_history: list = None) -> dict:
        """
        Process a chat query using hybrid SQL + FTS5 search.
        Returns {'answer': str, 'sources': [...], 'query_type': str}
        """
        # Step 1: Search line items (structured search)
        sql_results = self._sql_search(query, db_session, session_id)

        # Step 2: Search document chunks (FTS5 text search)
        fts_results = self._fts_search(query, db_session, session_id)

        # Step 3: Build context from results
        context = self._build_context(sql_results, fts_results)

        # Step 4: If no API key, return raw results
        if not self.api_key:
            return {
                'answer': f"Found {len(sql_results)} line items and {len(fts_results)} document passages matching your query. (AI synthesis requires ANTHROPIC_API_KEY)",
                'sources': self._format_sources(sql_results, fts_results),
                'query_type': 'search_only',
            }

        # Step 5: Synthesize with Claude
        answer = self._synthesize(query, context, conversation_history)

        return {
            'answer': answer,
            'sources': self._format_sources(sql_results, fts_results),
            'query_type': 'hybrid',
        }

    def _sql_search(self, query: str, db_session, session_id: str, limit: int = 20) -> list:
        """Search line items using LIKE matching on key fields."""
        from app.models.line_item import LineItem
        from app.models.document import Document

        # Extract search terms
        terms = [t.strip() for t in query.split() if len(t.strip()) > 2]
        if not terms:
            return []

        results = []
        q = db_session.query(LineItem).join(Document).filter(
            LineItem.session_id == session_id
        )

        # Build OR conditions across searchable fields
        from sqlalchemy import or_
        conditions = []
        for term in terms:
            like_term = f'%{term}%'
            conditions.extend([
                LineItem.product_name.ilike(like_term),
                LineItem.part_number.ilike(like_term),
                LineItem.manufacturer.ilike(like_term),
                LineItem.category.ilike(like_term),
                LineItem.labor_category.ilike(like_term),
                Document.vendor_name.ilike(like_term),
                Document.contract_number.ilike(like_term),
                Document.document_number.ilike(like_term),
            ])

        items = q.filter(or_(*conditions)).limit(limit).all()
        for item in items:
            results.append({
                'type': 'line_item',
                'product_name': item.product_name,
                'part_number': item.part_number,
                'manufacturer': item.manufacturer,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'extended_price': item.extended_price,
                'category': item.category,
                'vendor_name': item.document.vendor_name if item.document else None,
                'document_number': item.document.document_number if item.document else None,
                'document_date': item.document.document_date if item.document else None,
                'document_id': item.document_id,
                'document_type': item.document.document_type if item.document else None,
            })

        return results

    def _fts_search(self, query: str, db_session, session_id: str, limit: int = 10) -> list:
        """Full-text search on document chunks using FTS5."""
        from app.models.document_chunk import DocumentChunk
        from app.models.document import Document

        results = []
        try:
            # Use simple LIKE search as fallback (FTS5 may not be populated)
            terms = [t.strip() for t in query.split() if len(t.strip()) > 2]
            if not terms:
                return []

            from sqlalchemy import or_
            conditions = []
            for term in terms:
                conditions.append(DocumentChunk.content.ilike(f'%{term}%'))

            chunks = db_session.query(DocumentChunk).join(Document).filter(
                DocumentChunk.session_id == session_id,
                or_(*conditions)
            ).limit(limit).all()

            for chunk in chunks:
                results.append({
                    'type': 'chunk',
                    'content': chunk.content[:500],
                    'chunk_type': chunk.chunk_type,
                    'document_id': chunk.document_id,
                    'vendor_name': chunk.document.vendor_name if chunk.document else None,
                    'document_number': chunk.document.document_number if chunk.document else None,
                    'original_filename': chunk.document.original_filename if chunk.document else None,
                })
        except Exception as e:
            logger.error(f"FTS search error: {e}")

        return results

    def _build_context(self, sql_results: list, fts_results: list) -> str:
        """Build context string from search results for Claude."""
        parts = []

        if sql_results:
            parts.append("=== LINE ITEM SEARCH RESULTS ===")
            for r in sql_results[:15]:
                line = f"- {r.get('product_name', 'N/A')}"
                if r.get('part_number'):
                    line += f" (Part: {r['part_number']})"
                if r.get('manufacturer'):
                    line += f" by {r['manufacturer']}"
                if r.get('quantity') is not None and r.get('unit_price') is not None:
                    line += f" | Qty: {r['quantity']} @ ${r['unit_price']:,.2f}"
                if r.get('extended_price') is not None:
                    line += f" = ${r['extended_price']:,.2f}"
                line += f" | Vendor: {r.get('vendor_name', 'N/A')}"
                line += f" | Doc: {r.get('document_number', 'N/A')} ({r.get('document_type', '')})"
                line += f" | Date: {r.get('document_date', 'N/A')}"
                parts.append(line)

        if fts_results:
            parts.append("\n=== DOCUMENT TEXT SEARCH RESULTS ===")
            for r in fts_results[:10]:
                parts.append(f"[{r.get('document_number', r.get('original_filename', 'Unknown'))}] {r['content'][:300]}")

        return '\n'.join(parts) if parts else 'No results found matching the query.'

    def _format_sources(self, sql_results: list, fts_results: list) -> list:
        """Format source citations for the response."""
        seen = set()
        sources = []
        for r in sql_results + fts_results:
            doc_id = r.get('document_id')
            if doc_id and doc_id not in seen:
                seen.add(doc_id)
                sources.append({
                    'document_id': doc_id,
                    'document_number': r.get('document_number'),
                    'vendor_name': r.get('vendor_name'),
                    'original_filename': r.get('original_filename'),
                })
        return sources

    def _synthesize(self, query: str, context: str, history: list = None) -> str:
        """Send results to Claude for natural language synthesis."""
        import anthropic
        client = anthropic.Anthropic(api_key=self.api_key)

        messages = []
        if history:
            for msg in history[-6:]:  # Last 3 turns
                messages.append({"role": msg['role'], "content": msg['content']})

        messages.append({
            "role": "user",
            "content": CHAT_QUERY_PROMPT.format(context=context, question=query),
        })

        try:
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1024,
                system=CHAT_SYSTEM_PROMPT,
                messages=messages,
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude synthesis error: {e}")
            return f"I found relevant results but couldn't generate a summary. Error: {str(e)}\n\nRaw context:\n{context[:1000]}"
