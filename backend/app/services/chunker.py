import logging

logger = logging.getLogger(__name__)


class DocumentChunker:
    """Split document text into chunks for FTS5 search."""

    def chunk_text(self, full_text: str, chunk_size: int = 500,
                   overlap: int = 50) -> list:
        """
        Split text into overlapping chunks for search.
        Returns list of {'content': str, 'chunk_type': str, 'chunk_index': int}
        """
        if not full_text or not full_text.strip():
            return []

        paragraphs = full_text.split('\n\n')
        chunks = []
        current_chunk = ''
        chunk_idx = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_chunk) + len(para) + 1 > chunk_size and current_chunk:
                chunks.append({
                    'content': current_chunk.strip(),
                    'chunk_type': 'paragraph',
                    'chunk_index': chunk_idx,
                })
                chunk_idx += 1
                # Keep overlap from end of current chunk
                words = current_chunk.split()
                overlap_words = words[-overlap:] if len(words) > overlap else words
                current_chunk = ' '.join(overlap_words) + '\n\n' + para
            else:
                current_chunk = current_chunk + '\n\n' + para if current_chunk else para

        # Final chunk
        if current_chunk.strip():
            chunks.append({
                'content': current_chunk.strip(),
                'chunk_type': 'paragraph',
                'chunk_index': chunk_idx,
            })

        return chunks

    def chunk_line_items(self, line_items: list, document_metadata: dict) -> list:
        """Create searchable chunks from structured line item data."""
        if not line_items:
            return []

        chunks = []
        vendor = document_metadata.get('vendor_name', 'Unknown Vendor')
        doc_num = document_metadata.get('document_number', '')
        doc_type = document_metadata.get('document_type', '')
        doc_date = document_metadata.get('document_date', '')

        # Create one chunk per line item with full context
        for i, item in enumerate(line_items):
            parts = [
                f"Vendor: {vendor}",
                f"Document: {doc_num} ({doc_type})",
                f"Date: {doc_date}",
            ]
            if item.get('product_name'):
                parts.append(f"Product: {item['product_name']}")
            if item.get('part_number'):
                parts.append(f"Part Number: {item['part_number']}")
            if item.get('manufacturer'):
                parts.append(f"Manufacturer: {item['manufacturer']}")
            if item.get('quantity') is not None:
                parts.append(f"Quantity: {item['quantity']} {item.get('unit_of_issue', 'each')}")
            if item.get('unit_price') is not None:
                parts.append(f"Unit Price: ${item['unit_price']:,.2f}")
            if item.get('extended_price') is not None:
                parts.append(f"Extended Price: ${item['extended_price']:,.2f}")
            if item.get('category'):
                parts.append(f"Category: {item['category']}")
            if item.get('labor_category'):
                parts.append(f"Labor Category: {item['labor_category']}")

            chunks.append({
                'content': '\n'.join(parts),
                'chunk_type': 'table',
                'chunk_index': i,
            })

        return chunks
