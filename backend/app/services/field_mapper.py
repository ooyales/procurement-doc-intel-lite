import json
import logging

logger = logging.getLogger(__name__)

MAPPING_PROMPT = """You are analyzing a procurement document. Given the following raw table data extracted from a {file_format} file, please:

1. Identify the document type. Choose one of: vendor_quote, purchase_order, invoice, bom, contract_mod, timesheet, obligation, delivery_receipt, other

2. Extract header/metadata:
   - vendor_name, document_number, document_date
   - contract_number, task_order_number
   - total_amount, period_of_performance_start, period_of_performance_end

3. Map each row to our canonical schema with these fields:
   - line_number (sequential)
   - part_number (SKU, Part #, Item Code, Catalog #, Product ID)
   - product_name (Description, Item, Product, Title)
   - product_description (extended description if available)
   - manufacturer (Mfr, Brand, Make)
   - category: one of hardware, software, service, license, maintenance, labor, other
   - sub_category (e.g., laptop, server, endpoint_security, etc.)
   - quantity (Qty, Count, Units)
   - unit_of_issue (UOI, Unit — e.g., each, lot, month, year, hour)
   - unit_price (Unit $, Price, Rate, Unit Cost)
   - extended_price (Ext Price, Total, Amount, Line Total)
   - clin (CLIN, Line Item #)
   - labor_category (LCAT, Role, Position — for labor items)
   - labor_hours (Hours, Hrs)
   - labor_rate (Rate, Hourly Rate)
   - mapping_confidence: 0.0 to 1.0 for each row

Return ONLY valid JSON with this structure (no markdown, no explanation):
{{
  "document_type": "...",
  "metadata": {{
    "vendor_name": "...",
    "document_number": "...",
    "document_date": "...",
    "contract_number": "...",
    "task_order_number": "...",
    "total_amount": null or number,
    "period_of_performance_start": "...",
    "period_of_performance_end": "..."
  }},
  "line_items": [
    {{
      "line_number": 1,
      "part_number": "...",
      "product_name": "...",
      "product_description": "...",
      "manufacturer": "...",
      "category": "...",
      "sub_category": "...",
      "quantity": number or null,
      "unit_of_issue": "...",
      "unit_price": number or null,
      "extended_price": number or null,
      "clin": "...",
      "labor_category": "...",
      "labor_hours": number or null,
      "labor_rate": number or null,
      "mapping_confidence": 0.95
    }}
  ]
}}

Raw table data:
{raw_table}

Additional document text for context:
{document_text}"""


class FieldMapper:
    """Layer 2: Use Claude API to classify document and map fields."""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for document processing")
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)

    def map_document(self, raw_tables: list, document_text: str,
                     file_format: str, known_mappings: dict = None) -> dict:
        """
        Send extracted data to Claude API for classification and field mapping.
        Returns dict with document_type, metadata, and line_items.
        """
        # Truncate to fit context
        table_str = json.dumps(raw_tables[:50], indent=2)[:8000]
        text_snippet = (document_text or '')[:4000]

        prompt = MAPPING_PROMPT.format(
            file_format=file_format,
            raw_table=table_str,
            document_text=text_snippet,
        )

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.content[0].text.strip()
            # Remove markdown code fences if present
            if content.startswith('```'):
                content = content.split('\n', 1)[1]
                if content.endswith('```'):
                    content = content.rsplit('```', 1)[0]

            result = json.loads(content)
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {e}")
            return {
                'document_type': 'other',
                'metadata': {},
                'line_items': [],
                'error': f'JSON parse error: {str(e)}',
            }
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return {
                'document_type': 'other',
                'metadata': {},
                'line_items': [],
                'error': str(e),
            }
