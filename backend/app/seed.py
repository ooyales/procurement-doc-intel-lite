"""
Seed data for Procurement Document Intelligence Lite.

Creates realistic federal procurement demo data:
- 2 users (admin, viewer)
- 10 documents (varied types, vendors, statuses)
- ~75 line items across documents
- ~15 canonical products with pricing intelligence
- ~20 vendor-specific field mappings
- ~50 document chunks for RAG search
"""

import json
from datetime import datetime, timezone
from app.extensions import db
from app.models import (
    User, Document, LineItem, DocumentChunk,
    FieldMapping, CanonicalProduct,
)

SESSION = '__default__'


def seed():
    """Seed the database with demo procurement data."""

    # ── Clear existing __default__ data (order matters for FK constraints) ──
    DocumentChunk.query.filter_by(session_id=SESSION).delete()
    LineItem.query.filter_by(session_id=SESSION).delete()
    Document.query.filter_by(session_id=SESSION).delete()
    FieldMapping.query.filter_by(session_id=SESSION).delete()
    CanonicalProduct.query.filter_by(session_id=SESSION).delete()
    User.query.delete()
    db.session.flush()

    # ================================================================
    # USERS
    # ================================================================
    admin = User(
        username='admin',
        display_name='Admin User',
        email='admin@procdoc.local',
        role='admin',
    )
    admin.set_password('admin123')

    viewer = User(
        username='viewer',
        display_name='Pat Viewer',
        email='viewer@procdoc.local',
        role='viewer',
    )
    viewer.set_password('viewer123')

    db.session.add_all([admin, viewer])
    db.session.flush()

    # ================================================================
    # DOCUMENTS  (10)
    # ================================================================
    now = datetime.now(timezone.utc)

    docs = [
        # 1 - Dell Quote
        Document(
            id='d0000001-0000-0000-0000-000000000001',
            original_filename='Dell_Latitude_5550_Quote_Q-2025-7891.pdf',
            file_format='pdf',
            file_size_bytes=245_760,
            file_hash='a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2',
            stored_path='uploads/d0000001.pdf',
            document_type='vendor_quote',
            vendor_name='Dell Technologies',
            document_number='Q-2025-7891',
            document_date='2025-06-15',
            total_amount=83750.00,
            currency='USD',
            processing_status='complete',
            extraction_method='pdfplumber',
            extraction_confidence=0.95,
            ai_model_used='claude-sonnet-4-20250514',
            reviewed_by='Admin User',
            reviewed_at='2025-06-16T10:30:00Z',
            chunk_count=4,
            embedded=1,
            uploaded_by='admin',
            tags=json.dumps(['hardware', 'endpoint-refresh', 'dell']),
            notes='FY25 laptop refresh - 50 units for new hires.',
            session_id=SESSION,
            created_at=now,
            updated_at=now,
        ),
        # 2 - Dell PO
        Document(
            id='d0000002-0000-0000-0000-000000000002',
            original_filename='Dell_Latitude_5550_PO-2025-0089.pdf',
            file_format='pdf',
            file_size_bytes=312_000,
            file_hash='b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3',
            stored_path='uploads/d0000002.pdf',
            document_type='purchase_order',
            vendor_name='Dell Technologies',
            document_number='PO-2025-0089',
            document_date='2025-07-01',
            contract_number='GS-35F-12345',
            total_amount=83750.00,
            currency='USD',
            processing_status='complete',
            extraction_method='pdfplumber',
            extraction_confidence=0.97,
            ai_model_used='claude-sonnet-4-20250514',
            reviewed_by='Admin User',
            reviewed_at='2025-07-02T09:15:00Z',
            chunk_count=5,
            embedded=1,
            uploaded_by='admin',
            tags=json.dumps(['hardware', 'endpoint-refresh', 'dell', 'gsa-schedule']),
            notes='Purchase order against Dell GSA Schedule.',
            session_id=SESSION,
            created_at=now,
            updated_at=now,
        ),
        # 3 - CrowdStrike Quote
        Document(
            id='d0000003-0000-0000-0000-000000000003',
            original_filename='CrowdStrike_Falcon_Renewal_CS-Q-2025-445.pdf',
            file_format='pdf',
            file_size_bytes=189_440,
            file_hash='c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4',
            stored_path='uploads/d0000003.pdf',
            document_type='vendor_quote',
            vendor_name='CrowdStrike Inc',
            document_number='CS-Q-2025-445',
            document_date='2025-08-10',
            total_amount=45000.00,
            currency='USD',
            processing_status='complete',
            extraction_method='pdfplumber',
            extraction_confidence=0.93,
            ai_model_used='claude-sonnet-4-20250514',
            reviewed_by='Admin User',
            reviewed_at='2025-08-11T14:00:00Z',
            chunk_count=3,
            embedded=1,
            uploaded_by='admin',
            tags=json.dumps(['cybersecurity', 'endpoint-security', 'renewal']),
            notes='Annual Falcon renewal - 25 endpoint seats.',
            session_id=SESSION,
            created_at=now,
            updated_at=now,
        ),
        # 4 - CrowdStrike PO
        Document(
            id='d0000004-0000-0000-0000-000000000004',
            original_filename='CrowdStrike_Falcon_PO-2025-0095.pdf',
            file_format='pdf',
            file_size_bytes=278_528,
            file_hash='d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5',
            stored_path='uploads/d0000004.pdf',
            document_type='purchase_order',
            vendor_name='CrowdStrike Inc',
            document_number='PO-2025-0095',
            document_date='2025-09-01',
            contract_number='47QTCA20D006N',
            total_amount=45000.00,
            currency='USD',
            processing_status='complete',
            extraction_method='pdfplumber',
            extraction_confidence=0.96,
            ai_model_used='claude-sonnet-4-20250514',
            reviewed_by='Admin User',
            reviewed_at='2025-09-02T11:00:00Z',
            chunk_count=4,
            embedded=1,
            uploaded_by='admin',
            tags=json.dumps(['cybersecurity', 'endpoint-security', 'bpa']),
            notes='PO against CrowdStrike BPA for Falcon suite.',
            session_id=SESSION,
            created_at=now,
            updated_at=now,
        ),
        # 5 - Acme Invoice
        Document(
            id='d0000005-0000-0000-0000-000000000005',
            original_filename='Acme_IT_Services_Invoice_INV-2025-1147.pdf',
            file_format='pdf',
            file_size_bytes=156_672,
            file_hash='e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6',
            stored_path='uploads/d0000005.pdf',
            document_type='invoice',
            vendor_name='Acme IT Services LLC',
            document_number='INV-2025-1147',
            document_date='2025-10-01',
            contract_number='GS-35F-99876',
            period_of_performance_start='2025-09-01',
            period_of_performance_end='2025-09-30',
            total_amount=42400.00,
            currency='USD',
            processing_status='complete',
            extraction_method='pdfplumber',
            extraction_confidence=0.91,
            ai_model_used='claude-sonnet-4-20250514',
            reviewed_by='Admin User',
            reviewed_at='2025-10-03T08:45:00Z',
            chunk_count=4,
            embedded=1,
            uploaded_by='admin',
            tags=json.dumps(['labor', 'monthly-invoice', 'development']),
            notes='September 2025 monthly invoice for help desk support project.',
            session_id=SESSION,
            created_at=now,
            updated_at=now,
        ),
        # 6 - Cisco SmartNet
        Document(
            id='d0000006-0000-0000-0000-000000000006',
            original_filename='Cisco_SmartNet_Renewal_CSC-REN-2025-334.xlsx',
            file_format='xlsx',
            file_size_bytes=98_304,
            file_hash='f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1',
            stored_path='uploads/d0000006.xlsx',
            document_type='vendor_quote',
            vendor_name='Cisco Systems',
            document_number='CSC-REN-2025-334',
            document_date='2025-11-15',
            total_amount=28500.00,  # note: sum below is 29700, but doc says 28500 with discount
            currency='USD',
            processing_status='review',
            extraction_method='openpyxl',
            extraction_confidence=0.85,
            ai_model_used='claude-sonnet-4-20250514',
            chunk_count=5,
            embedded=1,
            uploaded_by='admin',
            tags=json.dumps(['maintenance', 'network', 'renewal', 'cisco']),
            notes='SmartNet renewal with multiple device classes. Needs pricing review.',
            session_id=SESSION,
            created_at=now,
            updated_at=now,
        ),
        # 7 - Help Desk Contract Mod
        Document(
            id='d0000007-0000-0000-0000-000000000007',
            original_filename='Acme_Help_Desk_Contract_Mod_MOD-003.pdf',
            file_format='pdf',
            file_size_bytes=420_864,
            file_hash='a7b8c9d0e1f2a7b8c9d0e1f2a7b8c9d0e1f2a7b8c9d0e1f2a7b8c9d0e1f2a7b8',
            stored_path='uploads/d0000007.pdf',
            document_type='contract_mod',
            vendor_name='Acme IT Services LLC',
            document_number='MOD-003',
            document_date='2025-09-15',
            contract_number='GS-35F-99876',
            period_of_performance_start='2025-10-01',
            period_of_performance_end='2026-09-30',
            total_amount=156000.00,
            currency='USD',
            processing_status='complete',
            extraction_method='pdfplumber',
            extraction_confidence=0.88,
            ai_model_used='claude-sonnet-4-20250514',
            reviewed_by='Admin User',
            reviewed_at='2025-09-18T16:20:00Z',
            chunk_count=5,
            embedded=1,
            uploaded_by='admin',
            tags=json.dumps(['contract-mod', 'help-desk', 'support']),
            notes='Modification 003 extending help desk support for 12 months.',
            session_id=SESSION,
            created_at=now,
            updated_at=now,
        ),
        # 8 - Server BOM
        Document(
            id='d0000008-0000-0000-0000-000000000008',
            original_filename='Dell_Server_Build_BOM-SRV-2025-01.xlsx',
            file_format='xlsx',
            file_size_bytes=134_144,
            file_hash='b8c9d0e1f2a3b8c9d0e1f2a3b8c9d0e1f2a3b8c9d0e1f2a3b8c9d0e1f2a3b8c9',
            stored_path='uploads/d0000008.xlsx',
            document_type='bom',
            vendor_name='Dell Technologies',
            document_number='BOM-SRV-2025-01',
            document_date='2025-05-20',
            total_amount=47200.00,
            currency='USD',
            processing_status='complete',
            extraction_method='openpyxl',
            extraction_confidence=0.92,
            ai_model_used='claude-sonnet-4-20250514',
            reviewed_by='Admin User',
            reviewed_at='2025-05-22T13:00:00Z',
            chunk_count=4,
            embedded=1,
            uploaded_by='admin',
            tags=json.dumps(['hardware', 'server', 'bom', 'dell']),
            notes='Bill of materials for two PowerEdge R750 server builds.',
            session_id=SESSION,
            created_at=now,
            updated_at=now,
        ),
        # 9 - Palo Alto (extracting)
        Document(
            id='d0000009-0000-0000-0000-000000000009',
            original_filename='PaloAlto_Firewall_Quote_PA-Q-2025-221.pdf',
            file_format='pdf',
            file_size_bytes=201_728,
            file_hash='c9d0e1f2a3b4c9d0e1f2a3b4c9d0e1f2a3b4c9d0e1f2a3b4c9d0e1f2a3b4c9d0',
            stored_path='uploads/d0000009.pdf',
            document_type='vendor_quote',
            vendor_name='Palo Alto Networks',
            document_number='PA-Q-2025-221',
            document_date='2026-01-10',
            total_amount=36000.00,
            currency='USD',
            processing_status='extracting',
            extraction_method='pdfplumber',
            extraction_confidence=None,
            chunk_count=0,
            embedded=0,
            uploaded_by='admin',
            tags=json.dumps(['security', 'firewall', 'network']),
            notes='Firewall quote - extraction in progress.',
            session_id=SESSION,
            created_at=now,
            updated_at=now,
        ),
        # 10 - Microsoft E5 (uploaded)
        Document(
            id='d0000010-0000-0000-0000-000000000010',
            original_filename='Microsoft_E5_License_Renewal_MS-REN-2026-118.docx',
            file_format='docx',
            file_size_bytes=167_936,
            file_hash='d0e1f2a3b4c5d0e1f2a3b4c5d0e1f2a3b4c5d0e1f2a3b4c5d0e1f2a3b4c5d0e1',
            stored_path='uploads/d0000010.docx',
            document_type='vendor_quote',
            vendor_name='Microsoft Corporation',
            document_number='MS-REN-2026-118',
            document_date='2026-01-20',
            total_amount=72000.00,
            currency='USD',
            processing_status='uploaded',
            extraction_confidence=None,
            chunk_count=0,
            embedded=0,
            uploaded_by='admin',
            tags=json.dumps(['license', 'microsoft', 'e5', 'renewal']),
            notes='M365 E5 renewal - awaiting extraction.',
            session_id=SESSION,
            created_at=now,
            updated_at=now,
        ),
    ]

    db.session.add_all(docs)
    db.session.flush()

    # ================================================================
    # LINE ITEMS  (~75)
    # ================================================================

    line_items = []

    # --- Doc 1 & 2: Dell Latitude Quote / PO (same 6 items appear on both) ---
    for doc_idx, doc_id in enumerate([
        'd0000001-0000-0000-0000-000000000001',
        'd0000002-0000-0000-0000-000000000002',
    ]):
        prefix = f'li-d{doc_idx + 1:02d}'
        line_items.extend([
            LineItem(
                id=f'{prefix}-0001-0000-0000-000000000001',
                document_id=doc_id,
                line_number=1,
                clin='0001',
                part_number='210-BGCD',
                manufacturer='Dell Technologies',
                product_name='Dell Latitude 5550 Laptop',
                product_description='14" FHD, Intel Core Ultra 5 135U, 16GB RAM, 512GB SSD, Win 11 Pro',
                category='hardware',
                sub_category='laptop',
                quantity=50,
                unit_of_issue='each',
                unit_price=1175.00,
                extended_price=58750.00,
                mapping_confidence=0.98,
                human_verified=1,
                original_row_text='210-BGCD | Dell Latitude 5550 Laptop | 50 | $1,175.00 | $58,750.00',
                session_id=SESSION,
            ),
            LineItem(
                id=f'{prefix}-0002-0000-0000-000000000002',
                document_id=doc_id,
                line_number=2,
                clin='0002',
                part_number='210-AZBX',
                manufacturer='Dell Technologies',
                product_name='Dell WD19TBS Docking Station',
                product_description='Thunderbolt Dock, 180W, USB-C, Dual DisplayPort, HDMI, RJ-45',
                category='hardware',
                sub_category='dock',
                quantity=50,
                unit_of_issue='each',
                unit_price=239.00,
                extended_price=11950.00,
                mapping_confidence=0.97,
                human_verified=1,
                original_row_text='210-AZBX | Dell WD19TBS Docking Station | 50 | $239.00 | $11,950.00',
                session_id=SESSION,
            ),
            LineItem(
                id=f'{prefix}-0003-0000-0000-000000000003',
                document_id=doc_id,
                line_number=3,
                clin='0003',
                part_number='210-BBBQ',
                manufacturer='Dell Technologies',
                product_name='Dell P2422H 24" Monitor',
                product_description='24" Full HD IPS, USB-C, DisplayPort, HDMI, Adjustable Stand',
                category='hardware',
                sub_category='monitor',
                quantity=50,
                unit_of_issue='each',
                unit_price=219.00,
                extended_price=10950.00,
                mapping_confidence=0.97,
                human_verified=1,
                original_row_text='210-BBBQ | Dell P2422H 24" Monitor | 50 | $219.00 | $10,950.00',
                session_id=SESSION,
            ),
            LineItem(
                id=f'{prefix}-0004-0000-0000-000000000004',
                document_id=doc_id,
                line_number=4,
                clin='0004',
                part_number='470-BDFB',
                manufacturer='Dell Technologies',
                product_name='Dell USB-C to HDMI Adapter',
                product_description='USB-C to HDMI 2.0 Adapter, 4K@60Hz',
                category='hardware',
                sub_category='accessory',
                quantity=50,
                unit_of_issue='each',
                unit_price=22.00,
                extended_price=1100.00,
                mapping_confidence=0.96,
                human_verified=1,
                original_row_text='470-BDFB | Dell USB-C to HDMI Adapter | 50 | $22.00 | $1,100.00',
                session_id=SESSION,
            ),
            LineItem(
                id=f'{prefix}-0005-0000-0000-000000000005',
                document_id=doc_id,
                line_number=5,
                clin='0005',
                part_number='812-3893',
                manufacturer='Dell Technologies',
                product_name='Dell ProSupport 3yr',
                product_description='3-Year ProSupport Next Business Day Onsite Service',
                category='maintenance',
                sub_category='warranty',
                quantity=50,
                unit_of_issue='each',
                unit_price=15.00,
                extended_price=750.00,
                mapping_confidence=0.95,
                human_verified=1,
                original_row_text='812-3893 | Dell ProSupport 3yr | 50 | $15.00 | $750.00',
                session_id=SESSION,
            ),
            LineItem(
                id=f'{prefix}-0006-0000-0000-000000000006',
                document_id=doc_id,
                line_number=6,
                clin='0006',
                product_name='Deployment Services',
                product_description='Onsite image deployment and asset tagging for 50 laptops',
                category='service',
                sub_category='deployment',
                quantity=1,
                unit_of_issue='lot',
                unit_price=250.00,
                extended_price=250.00,
                mapping_confidence=0.90,
                human_verified=1,
                original_row_text='Deployment Services | 1 lot | $250.00 | $250.00',
                session_id=SESSION,
            ),
        ])

    # --- Doc 3 & 4: CrowdStrike Quote / PO (same 3 items) ---
    for doc_idx, doc_id in enumerate([
        'd0000003-0000-0000-0000-000000000003',
        'd0000004-0000-0000-0000-000000000004',
    ], start=3):
        prefix = f'li-d{doc_idx:02d}'
        line_items.extend([
            LineItem(
                id=f'{prefix}-0001-0000-0000-000000000001',
                document_id=doc_id,
                line_number=1,
                clin='0001',
                part_number='CS-FC-ENT-25',
                manufacturer='CrowdStrike Inc',
                product_name='CrowdStrike Falcon Complete',
                product_description='Falcon Complete managed endpoint detection and response, 25 seats, annual subscription',
                category='license',
                sub_category='endpoint_security',
                quantity=25,
                unit_of_issue='each',
                unit_price=1500.00,
                extended_price=37500.00,
                period_start='2025-10-01',
                period_end='2026-09-30',
                mapping_confidence=0.96,
                human_verified=1,
                original_row_text='CS-FC-ENT-25 | CrowdStrike Falcon Complete | 25 seats | $1,500.00/yr | $37,500.00',
                session_id=SESSION,
            ),
            LineItem(
                id=f'{prefix}-0002-0000-0000-000000000002',
                document_id=doc_id,
                line_number=2,
                clin='0002',
                part_number='CS-FI-ENT-25',
                manufacturer='CrowdStrike Inc',
                product_name='CrowdStrike Falcon Insight',
                product_description='Falcon Insight XDR analytics add-on, 25 seats, annual subscription',
                category='license',
                sub_category='endpoint_security',
                quantity=25,
                unit_of_issue='each',
                unit_price=200.00,
                extended_price=5000.00,
                period_start='2025-10-01',
                period_end='2026-09-30',
                mapping_confidence=0.95,
                human_verified=1,
                original_row_text='CS-FI-ENT-25 | CrowdStrike Falcon Insight | 25 seats | $200.00/yr | $5,000.00',
                session_id=SESSION,
            ),
            LineItem(
                id=f'{prefix}-0003-0000-0000-000000000003',
                document_id=doc_id,
                line_number=3,
                clin='0003',
                product_name='CrowdStrike Onboarding',
                product_description='Professional services - sensor deployment and policy configuration',
                category='service',
                sub_category='onboarding',
                quantity=1,
                unit_of_issue='each',
                unit_price=2500.00,
                extended_price=2500.00,
                mapping_confidence=0.92,
                human_verified=1,
                original_row_text='Onboarding Services | 1 | $2,500.00 | $2,500.00',
                session_id=SESSION,
            ),
        ])

    # --- Doc 5: Acme Invoice — 6 labor items ---
    line_items.extend([
        LineItem(
            id='li-d05-0001-0000-0000-000000000001',
            document_id='d0000005-0000-0000-0000-000000000005',
            line_number=1,
            clin='0001',
            product_name='Project Manager',
            product_description='Project management and client coordination - September 2025',
            category='labor',
            sub_category='management',
            labor_category='Project Manager',
            labor_hours=160,
            labor_rate=65.00,
            quantity=160,
            unit_of_issue='hour',
            unit_price=65.00,
            extended_price=10400.00,
            period_start='2025-09-01',
            period_end='2025-09-30',
            mapping_confidence=0.94,
            human_verified=1,
            original_row_text='Project Manager | 160 hrs | $65.00/hr | $10,400.00',
            session_id=SESSION,
        ),
        LineItem(
            id='li-d05-0002-0000-0000-000000000002',
            document_id='d0000005-0000-0000-0000-000000000005',
            line_number=2,
            clin='0002',
            product_name='Senior Developer',
            product_description='Full-stack development and system architecture - September 2025',
            category='labor',
            sub_category='development',
            labor_category='Senior Developer',
            labor_hours=320,
            labor_rate=55.00,
            quantity=320,
            unit_of_issue='hour',
            unit_price=55.00,
            extended_price=17600.00,
            period_start='2025-09-01',
            period_end='2025-09-30',
            mapping_confidence=0.94,
            human_verified=1,
            original_row_text='Senior Developer | 320 hrs | $55.00/hr | $17,600.00',
            session_id=SESSION,
        ),
        LineItem(
            id='li-d05-0003-0000-0000-000000000003',
            document_id='d0000005-0000-0000-0000-000000000005',
            line_number=3,
            clin='0003',
            product_name='Junior Developer',
            product_description='Front-end development and bug fixes - September 2025',
            category='labor',
            sub_category='development',
            labor_category='Junior Developer',
            labor_hours=160,
            labor_rate=38.00,
            quantity=160,
            unit_of_issue='hour',
            unit_price=38.00,
            extended_price=6080.00,
            period_start='2025-09-01',
            period_end='2025-09-30',
            mapping_confidence=0.93,
            human_verified=1,
            original_row_text='Junior Developer | 160 hrs | $38.00/hr | $6,080.00',
            session_id=SESSION,
        ),
        LineItem(
            id='li-d05-0004-0000-0000-000000000004',
            document_id='d0000005-0000-0000-0000-000000000005',
            line_number=4,
            clin='0004',
            product_name='Business Analyst',
            product_description='Requirements analysis and documentation - September 2025',
            category='labor',
            sub_category='analysis',
            labor_category='Business Analyst',
            labor_hours=120,
            labor_rate=45.00,
            quantity=120,
            unit_of_issue='hour',
            unit_price=45.00,
            extended_price=5400.00,
            period_start='2025-09-01',
            period_end='2025-09-30',
            mapping_confidence=0.93,
            human_verified=1,
            original_row_text='Business Analyst | 120 hrs | $45.00/hr | $5,400.00',
            session_id=SESSION,
        ),
        LineItem(
            id='li-d05-0005-0000-0000-000000000005',
            document_id='d0000005-0000-0000-0000-000000000005',
            line_number=5,
            clin='0005',
            product_name='QA Tester',
            product_description='Quality assurance testing and regression testing - September 2025',
            category='labor',
            sub_category='testing',
            labor_category='QA Tester',
            labor_hours=80,
            labor_rate=38.00,
            quantity=80,
            unit_of_issue='hour',
            unit_price=38.00,
            extended_price=3040.00,
            period_start='2025-09-01',
            period_end='2025-09-30',
            mapping_confidence=0.93,
            human_verified=1,
            original_row_text='QA Tester | 80 hrs | $38.00/hr | $3,040.00',
            session_id=SESSION,
        ),
        LineItem(
            id='li-d05-0006-0000-0000-000000000006',
            document_id='d0000005-0000-0000-0000-000000000005',
            line_number=6,
            clin='0006',
            product_name='Travel Expenses',
            product_description='Reimbursable travel to client site - September 2025',
            category='other',
            sub_category='reimbursement',
            quantity=1,
            unit_of_issue='lot',
            unit_price=880.00,
            extended_price=880.00,
            mapping_confidence=0.88,
            human_verified=1,
            original_row_text='Travel Expenses (Reimbursable) | 1 | $880.00 | $880.00',
            session_id=SESSION,
        ),
    ])

    # --- Doc 6: Cisco SmartNet — 8 items ---
    line_items.extend([
        LineItem(
            id='li-d06-0001-0000-0000-000000000001',
            document_id='d0000006-0000-0000-0000-000000000006',
            line_number=1,
            part_number='CON-SSSNT-C93004UE',
            manufacturer='Cisco Systems',
            product_name='Cisco Catalyst 9300 SmartNet',
            product_description='Cisco SmartNet Total Care 8x5xNBD for Catalyst 9300-48UXM',
            category='maintenance',
            sub_category='network',
            quantity=5,
            unit_of_issue='each',
            unit_price=1200.00,
            extended_price=6000.00,
            period_start='2026-01-01',
            period_end='2026-12-31',
            mapping_confidence=0.88,
            human_verified=0,
            original_row_text='CON-SSSNT-C93004UE | Catalyst 9300 SmartNet 8x5xNBD | 5 | $1,200.00 | $6,000.00',
            session_id=SESSION,
        ),
        LineItem(
            id='li-d06-0002-0000-0000-000000000002',
            document_id='d0000006-0000-0000-0000-000000000006',
            line_number=2,
            part_number='CON-SSSNT-C92002UE',
            manufacturer='Cisco Systems',
            product_name='Cisco Catalyst 9200 SmartNet',
            product_description='Cisco SmartNet Total Care 8x5xNBD for Catalyst 9200-24P',
            category='maintenance',
            sub_category='network',
            quantity=10,
            unit_of_issue='each',
            unit_price=650.00,
            extended_price=6500.00,
            period_start='2026-01-01',
            period_end='2026-12-31',
            mapping_confidence=0.88,
            human_verified=0,
            original_row_text='CON-SSSNT-C92002UE | Catalyst 9200 SmartNet 8x5xNBD | 10 | $650.00 | $6,500.00',
            session_id=SESSION,
        ),
        LineItem(
            id='li-d06-0003-0000-0000-000000000003',
            document_id='d0000006-0000-0000-0000-000000000006',
            line_number=3,
            part_number='CON-SSSNT-ISR4331',
            manufacturer='Cisco Systems',
            product_name='Cisco ISR 4331 SmartNet',
            product_description='Cisco SmartNet Total Care 8x5xNBD for ISR 4331 Router',
            category='maintenance',
            sub_category='network',
            quantity=3,
            unit_of_issue='each',
            unit_price=900.00,
            extended_price=2700.00,
            period_start='2026-01-01',
            period_end='2026-12-31',
            mapping_confidence=0.87,
            human_verified=0,
            original_row_text='CON-SSSNT-ISR4331 | ISR 4331 SmartNet 8x5xNBD | 3 | $900.00 | $2,700.00',
            session_id=SESSION,
        ),
        LineItem(
            id='li-d06-0004-0000-0000-000000000004',
            document_id='d0000006-0000-0000-0000-000000000006',
            line_number=4,
            part_number='CON-SSSNT-ASA5525',
            manufacturer='Cisco Systems',
            product_name='Cisco ASA 5525-X SmartNet',
            product_description='Cisco SmartNet Total Care 24x7x4 for ASA 5525-X Firewall',
            category='maintenance',
            sub_category='security',
            quantity=2,
            unit_of_issue='each',
            unit_price=1800.00,
            extended_price=3600.00,
            period_start='2026-01-01',
            period_end='2026-12-31',
            mapping_confidence=0.87,
            human_verified=0,
            original_row_text='CON-SSSNT-ASA5525 | ASA 5525-X SmartNet 24x7x4 | 2 | $1,800.00 | $3,600.00',
            session_id=SESSION,
        ),
        LineItem(
            id='li-d06-0005-0000-0000-000000000005',
            document_id='d0000006-0000-0000-0000-000000000006',
            line_number=5,
            part_number='LIC-MR-3YR',
            manufacturer='Cisco Systems',
            product_name='Cisco Meraki MR46 License',
            product_description='Meraki MR Enterprise License, 3-Year Term',
            category='license',
            sub_category='network',
            quantity=20,
            unit_of_issue='each',
            unit_price=200.00,
            extended_price=4000.00,
            period_start='2026-01-01',
            period_end='2028-12-31',
            mapping_confidence=0.86,
            human_verified=0,
            original_row_text='LIC-MR-3YR | Meraki MR46 3-Year License | 20 | $200.00 | $4,000.00',
            session_id=SESSION,
        ),
        LineItem(
            id='li-d06-0006-0000-0000-000000000006',
            document_id='d0000006-0000-0000-0000-000000000006',
            line_number=6,
            part_number='L-AC-PLS-3Y-S4',
            manufacturer='Cisco Systems',
            product_name='Cisco AnyConnect VPN',
            product_description='Cisco AnyConnect Plus License, 3-Year, 500 users',
            category='license',
            sub_category='security',
            quantity=500,
            unit_of_issue='each',
            unit_price=8.00,
            extended_price=4000.00,
            period_start='2026-01-01',
            period_end='2028-12-31',
            mapping_confidence=0.85,
            human_verified=0,
            original_row_text='L-AC-PLS-3Y-S4 | AnyConnect Plus 3-Year 500 Users | 500 | $8.00 | $4,000.00',
            session_id=SESSION,
        ),
        LineItem(
            id='li-d06-0007-0000-0000-000000000007',
            document_id='d0000006-0000-0000-0000-000000000006',
            line_number=7,
            part_number='UMB-INSIGHTS-K9',
            manufacturer='Cisco Systems',
            product_name='Cisco Umbrella DNS',
            product_description='Cisco Umbrella DNS Security Insights, 500 users, annual',
            category='license',
            sub_category='security',
            quantity=500,
            unit_of_issue='each',
            unit_price=2.80,
            extended_price=1400.00,
            period_start='2026-01-01',
            period_end='2026-12-31',
            mapping_confidence=0.84,
            human_verified=0,
            original_row_text='UMB-INSIGHTS-K9 | Umbrella DNS Security 500 Users | 500 | $2.80 | $1,400.00',
            session_id=SESSION,
        ),
        LineItem(
            id='li-d06-0008-0000-0000-000000000008',
            document_id='d0000006-0000-0000-0000-000000000006',
            line_number=8,
            part_number='C9300-DNA-E-3Y',
            manufacturer='Cisco Systems',
            product_name='Cisco DNA Essentials',
            product_description='Cisco DNA Essentials 3-Year License for Catalyst 9300 only',
            category='license',
            sub_category='network',
            quantity=5,
            unit_of_issue='each',
            unit_price=300.00,
            extended_price=1500.00,
            period_start='2026-01-01',
            period_end='2028-12-31',
            mapping_confidence=0.83,
            human_verified=0,
            original_row_text='C9300-DNA-E-3Y | DNA Essentials for 9300 3-Year | 5 | $300.00 | $1,500.00',
            session_id=SESSION,
        ),
    ])

    # --- Doc 7: Help Desk Contract Mod — 3 items ---
    line_items.extend([
        LineItem(
            id='li-d07-0001-0000-0000-000000000001',
            document_id='d0000007-0000-0000-0000-000000000007',
            line_number=1,
            clin='0001',
            product_name='Help Desk Tier 1 Support',
            product_description='Tier 1 help desk support - password resets, account provisioning, basic troubleshooting. 8x5 coverage, 15-min SLA for P1.',
            category='service',
            sub_category='support',
            quantity=12,
            unit_of_issue='month',
            unit_price=5500.00,
            extended_price=66000.00,
            period_start='2025-10-01',
            period_end='2026-09-30',
            mapping_confidence=0.90,
            human_verified=1,
            original_row_text='CLIN 0001 | Help Desk Tier 1 Support | 12 months | $5,500.00/mo | $66,000.00',
            session_id=SESSION,
        ),
        LineItem(
            id='li-d07-0002-0000-0000-000000000002',
            document_id='d0000007-0000-0000-0000-000000000007',
            line_number=2,
            clin='0002',
            product_name='Help Desk Tier 2 Support',
            product_description='Tier 2 help desk support - application support, network troubleshooting, escalation management. 8x5 coverage.',
            category='service',
            sub_category='support',
            quantity=12,
            unit_of_issue='month',
            unit_price=7500.00,
            extended_price=90000.00,
            period_start='2025-10-01',
            period_end='2026-09-30',
            mapping_confidence=0.90,
            human_verified=1,
            original_row_text='CLIN 0002 | Help Desk Tier 2 Support | 12 months | $7,500.00/mo | $90,000.00',
            session_id=SESSION,
        ),
        LineItem(
            id='li-d07-0003-0000-0000-000000000003',
            document_id='d0000007-0000-0000-0000-000000000007',
            line_number=3,
            clin='0003',
            product_name='After-hours Emergency Support',
            product_description='After-hours emergency support coverage added at no additional cost per MOD-003 negotiation.',
            category='service',
            sub_category='support',
            quantity=1,
            unit_of_issue='lot',
            unit_price=0.00,
            extended_price=0.00,
            period_start='2025-10-01',
            period_end='2026-09-30',
            mapping_confidence=0.75,
            human_verified=0,
            original_row_text='CLIN 0003 | After-hours Emergency Support | 1 lot | $0.00 | $0.00',
            session_id=SESSION,
        ),
    ])

    # --- Doc 8: Server BOM — 9 items ---
    line_items.extend([
        LineItem(
            id='li-d08-0001-0000-0000-000000000001',
            document_id='d0000008-0000-0000-0000-000000000008',
            line_number=1,
            part_number='210-AZYB',
            manufacturer='Dell Technologies',
            product_name='Dell PowerEdge R750 Server Chassis',
            product_description='PowerEdge R750 2U Rack Server, Dual Socket, 32 DIMM Slots, 24x 2.5" Bays',
            category='hardware',
            sub_category='server',
            quantity=2,
            unit_of_issue='each',
            unit_price=4500.00,
            extended_price=9000.00,
            mapping_confidence=0.95,
            human_verified=1,
            original_row_text='210-AZYB | PowerEdge R750 Server Chassis | 2 | $4,500.00 | $9,000.00',
            session_id=SESSION,
        ),
        LineItem(
            id='li-d08-0002-0000-0000-000000000002',
            document_id='d0000008-0000-0000-0000-000000000008',
            line_number=2,
            part_number='338-CBXJ',
            manufacturer='Intel',
            product_name='Intel Xeon Gold 6338 CPU',
            product_description='Intel Xeon Gold 6338 2.0GHz 32-Core Processor, 48MB Cache, 205W TDP',
            category='hardware',
            sub_category='cpu',
            quantity=4,
            unit_of_issue='each',
            unit_price=2100.00,
            extended_price=8400.00,
            mapping_confidence=0.94,
            human_verified=1,
            original_row_text='338-CBXJ | Intel Xeon Gold 6338 2.0GHz 32C | 4 | $2,100.00 | $8,400.00',
            session_id=SESSION,
        ),
        LineItem(
            id='li-d08-0003-0000-0000-000000000003',
            document_id='d0000008-0000-0000-0000-000000000008',
            line_number=3,
            part_number='AA810826',
            manufacturer='Dell Technologies',
            product_name='32GB DDR4 3200MHz RDIMM',
            product_description='32GB DDR4 3200MHz Registered ECC DIMM Memory Module',
            category='hardware',
            sub_category='memory',
            quantity=16,
            unit_of_issue='each',
            unit_price=180.00,
            extended_price=2880.00,
            mapping_confidence=0.93,
            human_verified=1,
            original_row_text='AA810826 | 32GB DDR4 3200MHz RDIMM | 16 | $180.00 | $2,880.00',
            session_id=SESSION,
        ),
        LineItem(
            id='li-d08-0004-0000-0000-000000000004',
            document_id='d0000008-0000-0000-0000-000000000008',
            line_number=4,
            part_number='345-BBFX',
            manufacturer='Dell Technologies',
            product_name='960GB SSD SATA Mixed Use',
            product_description='960GB SSD SATA Mixed Use 6Gbps 2.5" Hot-Plug Drive',
            category='hardware',
            sub_category='storage',
            quantity=8,
            unit_of_issue='each',
            unit_price=450.00,
            extended_price=3600.00,
            mapping_confidence=0.93,
            human_verified=1,
            original_row_text='345-BBFX | 960GB SSD SATA Mixed Use 2.5" | 8 | $450.00 | $3,600.00',
            session_id=SESSION,
        ),
        LineItem(
            id='li-d08-0005-0000-0000-000000000005',
            document_id='d0000008-0000-0000-0000-000000000008',
            line_number=5,
            part_number='345-BDRD',
            manufacturer='Dell Technologies',
            product_name='1.92TB NVMe Mixed Use',
            product_description='1.92TB NVMe Mixed Use Express Flash 2.5" Hot-Plug U.2 Drive',
            category='hardware',
            sub_category='storage',
            quantity=4,
            unit_of_issue='each',
            unit_price=1200.00,
            extended_price=4800.00,
            mapping_confidence=0.92,
            human_verified=1,
            original_row_text='345-BDRD | 1.92TB NVMe Mixed Use 2.5" U.2 | 4 | $1,200.00 | $4,800.00',
            session_id=SESSION,
        ),
        LineItem(
            id='li-d08-0006-0000-0000-000000000006',
            document_id='d0000008-0000-0000-0000-000000000008',
            line_number=6,
            part_number='540-BBVM',
            manufacturer='Broadcom',
            product_name='Broadcom 57416 10GbE NIC',
            product_description='Broadcom 57416 Dual Port 10GbE BASE-T Network Adapter, PCIe',
            category='hardware',
            sub_category='network',
            quantity=4,
            unit_of_issue='each',
            unit_price=250.00,
            extended_price=1000.00,
            mapping_confidence=0.91,
            human_verified=1,
            original_row_text='540-BBVM | Broadcom 57416 10GbE Dual Port | 4 | $250.00 | $1,000.00',
            session_id=SESSION,
        ),
        LineItem(
            id='li-d08-0007-0000-0000-000000000007',
            document_id='d0000008-0000-0000-0000-000000000008',
            line_number=7,
            part_number='385-BBOW',
            manufacturer='Dell Technologies',
            product_name='Dell iDRAC9 Enterprise License',
            product_description='iDRAC9 Enterprise Digital License for remote server management',
            category='software',
            sub_category='management',
            quantity=2,
            unit_of_issue='each',
            unit_price=300.00,
            extended_price=600.00,
            mapping_confidence=0.90,
            human_verified=1,
            original_row_text='385-BBOW | iDRAC9 Enterprise License | 2 | $300.00 | $600.00',
            session_id=SESSION,
        ),
        LineItem(
            id='li-d08-0008-0000-0000-000000000008',
            document_id='d0000008-0000-0000-0000-000000000008',
            line_number=8,
            part_number='770-BCHJ',
            manufacturer='Dell Technologies',
            product_name='Dell ReadyRails Kit',
            product_description='ReadyRails Sliding Rails with Cable Management Arm for 2U',
            category='hardware',
            sub_category='accessory',
            quantity=2,
            unit_of_issue='each',
            unit_price=60.00,
            extended_price=120.00,
            mapping_confidence=0.90,
            human_verified=1,
            original_row_text='770-BCHJ | ReadyRails Sliding Rails 2U | 2 | $60.00 | $120.00',
            session_id=SESSION,
        ),
        LineItem(
            id='li-d08-0009-0000-0000-000000000009',
            document_id='d0000008-0000-0000-0000-000000000008',
            line_number=9,
            part_number='812-4012',
            manufacturer='Dell Technologies',
            product_name='3-Year ProSupport Plus',
            product_description='3-Year ProSupport Plus with Mission Critical 4-Hour Onsite Service',
            category='maintenance',
            sub_category='warranty',
            quantity=2,
            unit_of_issue='each',
            unit_price=1400.00,
            extended_price=2800.00,
            mapping_confidence=0.91,
            human_verified=1,
            original_row_text='812-4012 | 3-Year ProSupport Plus 4Hr | 2 | $1,400.00 | $2,800.00',
            session_id=SESSION,
        ),
    ])

    # No line items for doc 9 (extracting) or doc 10 (uploaded)

    db.session.add_all(line_items)
    db.session.flush()

    # ================================================================
    # CANONICAL PRODUCTS  (15)
    # ================================================================
    products = [
        CanonicalProduct(
            id='cp000001-0000-0000-0000-000000000001',
            canonical_name='Dell Latitude 5550 Laptop',
            category='hardware',
            manufacturer='Dell Technologies',
            known_part_numbers=json.dumps(['210-BGCD']),
            known_aliases=json.dumps(['Latitude 5550', 'Dell 5550', 'Lat 5550']),
            last_known_price=1175.00,
            last_price_date='2025-07-01',
            avg_price=1165.00,
            min_price=1150.00,
            max_price=1175.00,
            price_history=json.dumps([
                {'date': '2025-06-15', 'price': 1175.00, 'source': 'Q-2025-7891', 'type': 'vendor_quote'},
                {'date': '2025-07-01', 'price': 1175.00, 'source': 'PO-2025-0089', 'type': 'purchase_order'},
            ]),
            asset_tracker_category='Laptops',
            session_id=SESSION,
        ),
        CanonicalProduct(
            id='cp000002-0000-0000-0000-000000000002',
            canonical_name='Dell WD19TBS Docking Station',
            category='hardware',
            manufacturer='Dell Technologies',
            known_part_numbers=json.dumps(['210-AZBX']),
            known_aliases=json.dumps(['WD19TBS', 'Dell Thunderbolt Dock']),
            last_known_price=239.00,
            last_price_date='2025-07-01',
            avg_price=239.00,
            min_price=239.00,
            max_price=239.00,
            price_history=json.dumps([
                {'date': '2025-07-01', 'price': 239.00, 'source': 'PO-2025-0089', 'type': 'purchase_order'},
            ]),
            asset_tracker_category='Peripherals',
            session_id=SESSION,
        ),
        CanonicalProduct(
            id='cp000003-0000-0000-0000-000000000003',
            canonical_name='Dell P2422H Monitor',
            category='hardware',
            manufacturer='Dell Technologies',
            known_part_numbers=json.dumps(['210-BBBQ']),
            known_aliases=json.dumps(['P2422H', 'Dell 24" Monitor']),
            last_known_price=219.00,
            last_price_date='2025-07-01',
            avg_price=219.00,
            min_price=219.00,
            max_price=219.00,
            price_history=json.dumps([
                {'date': '2025-07-01', 'price': 219.00, 'source': 'PO-2025-0089', 'type': 'purchase_order'},
            ]),
            asset_tracker_category='Monitors',
            session_id=SESSION,
        ),
        CanonicalProduct(
            id='cp000004-0000-0000-0000-000000000004',
            canonical_name='CrowdStrike Falcon Complete',
            category='license',
            manufacturer='CrowdStrike Inc',
            known_part_numbers=json.dumps(['CS-FC-ENT-25', 'CS-FC-ENT-50', 'CS-FC-ENT-100']),
            known_aliases=json.dumps(['Falcon Complete', 'CrowdStrike Complete MDR']),
            last_known_price=1500.00,
            last_price_date='2025-09-01',
            avg_price=1450.00,
            min_price=1400.00,
            max_price=1500.00,
            price_history=json.dumps([
                {'date': '2024-09-01', 'price': 1400.00, 'source': 'PO-2024-0072', 'type': 'purchase_order'},
                {'date': '2025-09-01', 'price': 1500.00, 'source': 'PO-2025-0095', 'type': 'purchase_order'},
            ]),
            asset_tracker_category='Security Software',
            session_id=SESSION,
        ),
        CanonicalProduct(
            id='cp000005-0000-0000-0000-000000000005',
            canonical_name='CrowdStrike Falcon Insight',
            category='license',
            manufacturer='CrowdStrike Inc',
            known_part_numbers=json.dumps(['CS-FI-ENT-25', 'CS-FI-ENT-50']),
            known_aliases=json.dumps(['Falcon Insight', 'Falcon Insight XDR']),
            last_known_price=200.00,
            last_price_date='2025-09-01',
            avg_price=200.00,
            min_price=200.00,
            max_price=200.00,
            price_history=json.dumps([
                {'date': '2025-09-01', 'price': 200.00, 'source': 'PO-2025-0095', 'type': 'purchase_order'},
            ]),
            asset_tracker_category='Security Software',
            session_id=SESSION,
        ),
        CanonicalProduct(
            id='cp000006-0000-0000-0000-000000000006',
            canonical_name='Cisco Catalyst 9300 SmartNet',
            category='maintenance',
            manufacturer='Cisco Systems',
            known_part_numbers=json.dumps(['CON-SSSNT-C93004UE', 'CON-SSSNT-C930048X']),
            known_aliases=json.dumps(['Cat 9300 SmartNet', 'C9300 SNTC']),
            last_known_price=1200.00,
            last_price_date='2025-11-15',
            avg_price=1200.00,
            min_price=1200.00,
            max_price=1200.00,
            price_history=json.dumps([
                {'date': '2025-11-15', 'price': 1200.00, 'source': 'CSC-REN-2025-334', 'type': 'vendor_quote'},
            ]),
            asset_tracker_category='Network Equipment',
            session_id=SESSION,
        ),
        CanonicalProduct(
            id='cp000007-0000-0000-0000-000000000007',
            canonical_name='Cisco Catalyst 9200 SmartNet',
            category='maintenance',
            manufacturer='Cisco Systems',
            known_part_numbers=json.dumps(['CON-SSSNT-C92002UE', 'CON-SSSNT-C920024P']),
            known_aliases=json.dumps(['Cat 9200 SmartNet', 'C9200 SNTC']),
            last_known_price=650.00,
            last_price_date='2025-11-15',
            avg_price=650.00,
            min_price=650.00,
            max_price=650.00,
            price_history=json.dumps([
                {'date': '2025-11-15', 'price': 650.00, 'source': 'CSC-REN-2025-334', 'type': 'vendor_quote'},
            ]),
            asset_tracker_category='Network Equipment',
            session_id=SESSION,
        ),
        CanonicalProduct(
            id='cp000008-0000-0000-0000-000000000008',
            canonical_name='Cisco ASA 5525-X SmartNet',
            category='maintenance',
            manufacturer='Cisco Systems',
            known_part_numbers=json.dumps(['CON-SSSNT-ASA5525']),
            known_aliases=json.dumps(['ASA 5525 SmartNet', 'ASA5525 SNTC']),
            last_known_price=1800.00,
            last_price_date='2025-11-15',
            avg_price=1800.00,
            min_price=1800.00,
            max_price=1800.00,
            price_history=json.dumps([
                {'date': '2025-11-15', 'price': 1800.00, 'source': 'CSC-REN-2025-334', 'type': 'vendor_quote'},
            ]),
            asset_tracker_category='Security Appliances',
            session_id=SESSION,
        ),
        CanonicalProduct(
            id='cp000009-0000-0000-0000-000000000009',
            canonical_name='Dell PowerEdge R750',
            category='hardware',
            manufacturer='Dell Technologies',
            known_part_numbers=json.dumps(['210-AZYB']),
            known_aliases=json.dumps(['PowerEdge R750', 'PE R750', 'R750 Server']),
            last_known_price=4500.00,
            last_price_date='2025-05-20',
            avg_price=4500.00,
            min_price=4500.00,
            max_price=4500.00,
            price_history=json.dumps([
                {'date': '2025-05-20', 'price': 4500.00, 'source': 'BOM-SRV-2025-01', 'type': 'bom'},
            ]),
            asset_tracker_category='Servers',
            session_id=SESSION,
        ),
        CanonicalProduct(
            id='cp000010-0000-0000-0000-000000000010',
            canonical_name='Intel Xeon Gold 6338',
            category='hardware',
            manufacturer='Intel',
            known_part_numbers=json.dumps(['338-CBXJ', 'CD8068904572501']),
            known_aliases=json.dumps(['Xeon Gold 6338', 'Xeon 6338 32C']),
            last_known_price=2100.00,
            last_price_date='2025-05-20',
            avg_price=2100.00,
            min_price=2100.00,
            max_price=2100.00,
            price_history=json.dumps([
                {'date': '2025-05-20', 'price': 2100.00, 'source': 'BOM-SRV-2025-01', 'type': 'bom'},
            ]),
            asset_tracker_category='Server Components',
            session_id=SESSION,
        ),
        CanonicalProduct(
            id='cp000011-0000-0000-0000-000000000011',
            canonical_name='Palo Alto PA-460 Firewall',
            category='hardware',
            manufacturer='Palo Alto Networks',
            known_part_numbers=json.dumps(['PAN-PA-460', 'PA-460-BND']),
            known_aliases=json.dumps(['PA-460', 'Palo Alto 460']),
            last_known_price=8500.00,
            last_price_date='2024-11-01',
            avg_price=8500.00,
            min_price=8500.00,
            max_price=8500.00,
            price_history=json.dumps([
                {'date': '2024-11-01', 'price': 8500.00, 'source': 'PA-Q-2024-189', 'type': 'vendor_quote'},
            ]),
            asset_tracker_category='Security Appliances',
            session_id=SESSION,
        ),
        CanonicalProduct(
            id='cp000012-0000-0000-0000-000000000012',
            canonical_name='Microsoft 365 E5 License',
            category='license',
            manufacturer='Microsoft Corporation',
            known_part_numbers=json.dumps(['AAA-35638', 'MS-E5-ENT']),
            known_aliases=json.dumps(['M365 E5', 'Office 365 E5', 'Microsoft E5']),
            last_known_price=57.00,
            last_price_date='2025-01-20',
            avg_price=57.00,
            min_price=57.00,
            max_price=57.00,
            price_history=json.dumps([
                {'date': '2025-01-20', 'price': 57.00, 'source': 'MS-REN-2025-095', 'type': 'vendor_quote'},
            ]),
            asset_tracker_category='Software Licenses',
            session_id=SESSION,
        ),
        CanonicalProduct(
            id='cp000013-0000-0000-0000-000000000013',
            canonical_name='Project Manager (Labor)',
            category='labor',
            manufacturer=None,
            known_part_numbers=json.dumps([]),
            known_aliases=json.dumps(['PM', 'Program Manager', 'Project Lead']),
            last_known_price=65.00,
            last_price_date='2025-10-01',
            avg_price=65.00,
            min_price=60.00,
            max_price=70.00,
            price_history=json.dumps([
                {'date': '2025-07-01', 'price': 65.00, 'source': 'INV-2025-1144', 'type': 'invoice'},
                {'date': '2025-08-01', 'price': 65.00, 'source': 'INV-2025-1145', 'type': 'invoice'},
                {'date': '2025-09-01', 'price': 65.00, 'source': 'INV-2025-1146', 'type': 'invoice'},
                {'date': '2025-10-01', 'price': 65.00, 'source': 'INV-2025-1147', 'type': 'invoice'},
            ]),
            asset_tracker_category=None,
            session_id=SESSION,
        ),
        CanonicalProduct(
            id='cp000014-0000-0000-0000-000000000014',
            canonical_name='Senior Developer (Labor)',
            category='labor',
            manufacturer=None,
            known_part_numbers=json.dumps([]),
            known_aliases=json.dumps(['Sr Developer', 'Sr Dev', 'Senior Software Developer', 'Senior Engineer']),
            last_known_price=55.00,
            last_price_date='2025-10-01',
            avg_price=55.00,
            min_price=50.00,
            max_price=58.00,
            price_history=json.dumps([
                {'date': '2025-07-01', 'price': 55.00, 'source': 'INV-2025-1144', 'type': 'invoice'},
                {'date': '2025-08-01', 'price': 55.00, 'source': 'INV-2025-1145', 'type': 'invoice'},
                {'date': '2025-09-01', 'price': 55.00, 'source': 'INV-2025-1146', 'type': 'invoice'},
                {'date': '2025-10-01', 'price': 55.00, 'source': 'INV-2025-1147', 'type': 'invoice'},
            ]),
            asset_tracker_category=None,
            session_id=SESSION,
        ),
        CanonicalProduct(
            id='cp000015-0000-0000-0000-000000000015',
            canonical_name='Junior Developer (Labor)',
            category='labor',
            manufacturer=None,
            known_part_numbers=json.dumps([]),
            known_aliases=json.dumps(['Jr Developer', 'Jr Dev', 'Junior Software Developer']),
            last_known_price=38.00,
            last_price_date='2025-10-01',
            avg_price=38.00,
            min_price=35.00,
            max_price=40.00,
            price_history=json.dumps([
                {'date': '2025-07-01', 'price': 38.00, 'source': 'INV-2025-1144', 'type': 'invoice'},
                {'date': '2025-08-01', 'price': 38.00, 'source': 'INV-2025-1145', 'type': 'invoice'},
                {'date': '2025-09-01', 'price': 38.00, 'source': 'INV-2025-1146', 'type': 'invoice'},
                {'date': '2025-10-01', 'price': 38.00, 'source': 'INV-2025-1147', 'type': 'invoice'},
            ]),
            asset_tracker_category=None,
            session_id=SESSION,
        ),
    ]

    db.session.add_all(products)
    db.session.flush()

    # ================================================================
    # FIELD MAPPINGS  (~20)
    # ================================================================
    mappings = [
        # Dell Technologies
        FieldMapping(
            id='fm000001-0000-0000-0000-000000000001',
            vendor_name='Dell Technologies',
            source_column_name='Part #',
            target_field='part_number',
            confidence=1.0,
            times_confirmed=8,
            session_id=SESSION,
        ),
        FieldMapping(
            id='fm000002-0000-0000-0000-000000000002',
            vendor_name='Dell Technologies',
            source_column_name='Description',
            target_field='product_name',
            confidence=1.0,
            times_confirmed=8,
            session_id=SESSION,
        ),
        FieldMapping(
            id='fm000003-0000-0000-0000-000000000003',
            vendor_name='Dell Technologies',
            source_column_name='Qty',
            target_field='quantity',
            confidence=1.0,
            times_confirmed=8,
            session_id=SESSION,
        ),
        FieldMapping(
            id='fm000004-0000-0000-0000-000000000004',
            vendor_name='Dell Technologies',
            source_column_name='Unit Price',
            target_field='unit_price',
            confidence=1.0,
            times_confirmed=8,
            session_id=SESSION,
        ),
        FieldMapping(
            id='fm000005-0000-0000-0000-000000000005',
            vendor_name='Dell Technologies',
            source_column_name='Ext Price',
            target_field='extended_price',
            confidence=1.0,
            times_confirmed=8,
            session_id=SESSION,
        ),
        # CrowdStrike
        FieldMapping(
            id='fm000006-0000-0000-0000-000000000006',
            vendor_name='CrowdStrike Inc',
            source_column_name='SKU',
            target_field='part_number',
            confidence=0.98,
            times_confirmed=4,
            session_id=SESSION,
        ),
        FieldMapping(
            id='fm000007-0000-0000-0000-000000000007',
            vendor_name='CrowdStrike Inc',
            source_column_name='Product',
            target_field='product_name',
            confidence=0.98,
            times_confirmed=4,
            session_id=SESSION,
        ),
        FieldMapping(
            id='fm000008-0000-0000-0000-000000000008',
            vendor_name='CrowdStrike Inc',
            source_column_name='Seats',
            target_field='quantity',
            confidence=0.97,
            times_confirmed=4,
            session_id=SESSION,
        ),
        FieldMapping(
            id='fm000009-0000-0000-0000-000000000009',
            vendor_name='CrowdStrike Inc',
            source_column_name='Per Seat',
            target_field='unit_price',
            confidence=0.97,
            times_confirmed=4,
            session_id=SESSION,
        ),
        FieldMapping(
            id='fm000010-0000-0000-0000-000000000010',
            vendor_name='CrowdStrike Inc',
            source_column_name='Total',
            target_field='extended_price',
            confidence=0.98,
            times_confirmed=4,
            session_id=SESSION,
        ),
        # Acme IT Services
        FieldMapping(
            id='fm000011-0000-0000-0000-000000000011',
            vendor_name='Acme IT Services LLC',
            source_column_name='Role',
            target_field='labor_category',
            confidence=0.95,
            times_confirmed=6,
            session_id=SESSION,
        ),
        FieldMapping(
            id='fm000012-0000-0000-0000-000000000012',
            vendor_name='Acme IT Services LLC',
            source_column_name='Hours',
            target_field='labor_hours',
            confidence=0.95,
            times_confirmed=6,
            session_id=SESSION,
        ),
        FieldMapping(
            id='fm000013-0000-0000-0000-000000000013',
            vendor_name='Acme IT Services LLC',
            source_column_name='Rate',
            target_field='labor_rate',
            confidence=0.95,
            times_confirmed=6,
            session_id=SESSION,
        ),
        FieldMapping(
            id='fm000014-0000-0000-0000-000000000014',
            vendor_name='Acme IT Services LLC',
            source_column_name='Amount',
            target_field='extended_price',
            confidence=0.96,
            times_confirmed=6,
            session_id=SESSION,
        ),
        # Cisco Systems
        FieldMapping(
            id='fm000015-0000-0000-0000-000000000015',
            vendor_name='Cisco Systems',
            source_column_name='Part Number',
            target_field='part_number',
            confidence=0.99,
            times_confirmed=5,
            session_id=SESSION,
        ),
        FieldMapping(
            id='fm000016-0000-0000-0000-000000000016',
            vendor_name='Cisco Systems',
            source_column_name='Product Description',
            target_field='product_name',
            confidence=0.99,
            times_confirmed=5,
            session_id=SESSION,
        ),
        FieldMapping(
            id='fm000017-0000-0000-0000-000000000017',
            vendor_name='Cisco Systems',
            source_column_name='Quantity',
            target_field='quantity',
            confidence=0.99,
            times_confirmed=5,
            session_id=SESSION,
        ),
        FieldMapping(
            id='fm000018-0000-0000-0000-000000000018',
            vendor_name='Cisco Systems',
            source_column_name='Unit List Price',
            target_field='unit_price',
            confidence=0.98,
            times_confirmed=5,
            session_id=SESSION,
        ),
        FieldMapping(
            id='fm000019-0000-0000-0000-000000000019',
            vendor_name='Cisco Systems',
            source_column_name='Net Price',
            target_field='extended_price',
            confidence=0.98,
            times_confirmed=5,
            session_id=SESSION,
        ),
        # General / catch-all
        FieldMapping(
            id='fm000020-0000-0000-0000-000000000020',
            vendor_name=None,
            source_column_name='Item',
            target_field='product_name',
            confidence=0.80,
            times_confirmed=2,
            session_id=SESSION,
        ),
        FieldMapping(
            id='fm000021-0000-0000-0000-000000000021',
            vendor_name=None,
            source_column_name='Price',
            target_field='unit_price',
            confidence=0.80,
            times_confirmed=2,
            session_id=SESSION,
        ),
        FieldMapping(
            id='fm000022-0000-0000-0000-000000000022',
            vendor_name=None,
            source_column_name='Total',
            target_field='extended_price',
            confidence=0.80,
            times_confirmed=2,
            session_id=SESSION,
        ),
    ]

    db.session.add_all(mappings)
    db.session.flush()

    # ================================================================
    # DOCUMENT CHUNKS  (~50)
    # ================================================================
    chunks = []
    chunk_counter = 0

    def _make_chunk(doc_id, idx, content, chunk_type='paragraph', page=1):
        nonlocal chunk_counter
        chunk_counter += 1
        return DocumentChunk(
            id=f'dc{chunk_counter:06d}-0000-0000-0000-000000000000',
            document_id=doc_id,
            chunk_index=idx,
            content=content,
            chunk_type=chunk_type,
            page_number=page,
            session_id=SESSION,
        )

    # --- Doc 1: Dell Quote ---
    doc1 = 'd0000001-0000-0000-0000-000000000001'
    chunks.extend([
        _make_chunk(doc1, 0,
                    'Document: Q-2025-7891 | Vendor: Dell Technologies | Date: 2025-06-15 | '
                    'Type: Vendor Quote | Total: $83,750.00 | Description: Dell Latitude 5550 '
                    'endpoint refresh quote for 50 laptop bundles including docking stations, '
                    'monitors, and deployment services.',
                    'metadata', 1),
        _make_chunk(doc1, 1,
                    'Line Items - Hardware Bundle:\n'
                    '1. Dell Latitude 5550 Laptop (210-BGCD) - 14" FHD, Intel Core Ultra 5 135U, '
                    '16GB RAM, 512GB SSD, Win 11 Pro - Qty: 50 @ $1,175.00 = $58,750.00\n'
                    '2. Dell WD19TBS Docking Station (210-AZBX) - Thunderbolt Dock, 180W - '
                    'Qty: 50 @ $239.00 = $11,950.00\n'
                    '3. Dell P2422H 24" Monitor (210-BBBQ) - Full HD IPS - Qty: 50 @ $219.00 = $10,950.00',
                    'table', 1),
        _make_chunk(doc1, 2,
                    'Line Items - Accessories and Services:\n'
                    '4. Dell USB-C to HDMI Adapter (470-BDFB) - Qty: 50 @ $22.00 = $1,100.00\n'
                    '5. Dell ProSupport 3yr (812-3893) - Next Business Day Onsite - Qty: 50 @ $15.00 = $750.00\n'
                    '6. Deployment Services - Onsite image deployment and asset tagging - 1 lot @ $250.00',
                    'table', 2),
        _make_chunk(doc1, 3,
                    'Quote Summary: Dell Technologies Quote Q-2025-7891 dated June 15, 2025 for '
                    'endpoint refresh program. Total value $83,750.00 for 50 complete laptop '
                    'bundles with 3-year warranty coverage. Valid for 30 days from quote date.',
                    'paragraph', 2),
    ])

    # --- Doc 2: Dell PO ---
    doc2 = 'd0000002-0000-0000-0000-000000000002'
    chunks.extend([
        _make_chunk(doc2, 0,
                    'Document: PO-2025-0089 | Vendor: Dell Technologies | Date: 2025-07-01 | '
                    'Type: Purchase Order | Contract: GS-35F-12345 | Total: $83,750.00 | '
                    'Description: Purchase order for Dell Latitude 5550 endpoint refresh against '
                    'GSA Schedule GS-35F-12345.',
                    'metadata', 1),
        _make_chunk(doc2, 1,
                    'Purchase Order Line Items:\n'
                    'CLIN 0001: Dell Latitude 5550 Laptop (210-BGCD) - 50 each @ $1,175.00 = $58,750.00\n'
                    'CLIN 0002: Dell WD19TBS Docking Station (210-AZBX) - 50 each @ $239.00 = $11,950.00\n'
                    'CLIN 0003: Dell P2422H 24" Monitor (210-BBBQ) - 50 each @ $219.00 = $10,950.00',
                    'table', 1),
        _make_chunk(doc2, 2,
                    'CLIN 0004: Dell USB-C to HDMI Adapter (470-BDFB) - 50 each @ $22.00 = $1,100.00\n'
                    'CLIN 0005: Dell ProSupport 3yr (812-3893) - 50 each @ $15.00 = $750.00\n'
                    'CLIN 0006: Deployment Services - 1 lot @ $250.00 = $250.00',
                    'table', 2),
        _make_chunk(doc2, 3,
                    'Terms and Conditions: Delivery within 30 business days ARO. FOB Destination. '
                    'Payment Net 30. All items to be delivered to main office loading dock. '
                    'Asset tags to be applied per agency standard AT-2025 format.',
                    'terms', 2),
        _make_chunk(doc2, 4,
                    'PO Summary: Purchase Order PO-2025-0089 issued July 1, 2025 against GSA '
                    'Schedule GS-35F-12345. Total obligation: $83,750.00. Funds cite: '
                    'FY25-IT-REFRESH-001. Contracting Officer: J. Smith.',
                    'paragraph', 3),
    ])

    # --- Doc 3: CrowdStrike Quote ---
    doc3 = 'd0000003-0000-0000-0000-000000000003'
    chunks.extend([
        _make_chunk(doc3, 0,
                    'Document: CS-Q-2025-445 | Vendor: CrowdStrike Inc | Date: 2025-08-10 | '
                    'Type: Vendor Quote | Total: $45,000.00 | Description: Annual renewal quote '
                    'for CrowdStrike Falcon Complete and Falcon Insight endpoint security suite, '
                    '25 seats.',
                    'metadata', 1),
        _make_chunk(doc3, 1,
                    'CrowdStrike Falcon Renewal Quote:\n'
                    '1. Falcon Complete (CS-FC-ENT-25) - Managed EDR, 25 seats, annual - '
                    '$1,500.00/seat = $37,500.00\n'
                    '2. Falcon Insight (CS-FI-ENT-25) - XDR Analytics, 25 seats, annual - '
                    '$200.00/seat = $5,000.00\n'
                    '3. Onboarding Services - Sensor deployment and policy config - $2,500.00',
                    'table', 1),
        _make_chunk(doc3, 2,
                    'Quote Summary: CrowdStrike renewal CS-Q-2025-445 for Falcon endpoint '
                    'security platform. Coverage period: Oct 1, 2025 through Sep 30, 2026. '
                    'Includes 24/7 managed detection and response with Falcon Complete. '
                    'Total: $45,000.00. Quote valid 60 days.',
                    'paragraph', 1),
    ])

    # --- Doc 4: CrowdStrike PO ---
    doc4 = 'd0000004-0000-0000-0000-000000000004'
    chunks.extend([
        _make_chunk(doc4, 0,
                    'Document: PO-2025-0095 | Vendor: CrowdStrike Inc | Date: 2025-09-01 | '
                    'Type: Purchase Order | Contract: 47QTCA20D006N | Total: $45,000.00 | '
                    'Description: Purchase order for CrowdStrike Falcon annual renewal against '
                    'BPA 47QTCA20D006N.',
                    'metadata', 1),
        _make_chunk(doc4, 1,
                    'CLIN 0001: CrowdStrike Falcon Complete (CS-FC-ENT-25) - 25 seats @ '
                    '$1,500.00/yr = $37,500.00. Period: 10/1/2025 - 9/30/2026.\n'
                    'CLIN 0002: CrowdStrike Falcon Insight (CS-FI-ENT-25) - 25 seats @ '
                    '$200.00/yr = $5,000.00. Period: 10/1/2025 - 9/30/2026.\n'
                    'CLIN 0003: Onboarding Services - 1 @ $2,500.00 = $2,500.00.',
                    'table', 1),
        _make_chunk(doc4, 2,
                    'Funding: FY25-CYBER-SEC-003. Total obligation $45,000.00. BPA Call Order '
                    'against 47QTCA20D006N. Contracting Officer: M. Johnson. COR: L. Davis.',
                    'paragraph', 2),
        _make_chunk(doc4, 3,
                    'PO Summary: CrowdStrike Falcon suite renewal PO-2025-0095 for 25 endpoint '
                    'seats. Managed EDR with Falcon Complete plus XDR analytics via Falcon Insight. '
                    'Annual coverage Oct 2025 through Sep 2026.',
                    'paragraph', 2),
    ])

    # --- Doc 5: Acme Invoice ---
    doc5 = 'd0000005-0000-0000-0000-000000000005'
    chunks.extend([
        _make_chunk(doc5, 0,
                    'Document: INV-2025-1147 | Vendor: Acme IT Services LLC | Date: 2025-10-01 | '
                    'Type: Invoice | Contract: GS-35F-99876 | Total: $42,400.00 | '
                    'Period: Sep 1, 2025 - Sep 30, 2025 | Description: Monthly T&M invoice for '
                    'application development and support services.',
                    'metadata', 1),
        _make_chunk(doc5, 1,
                    'Labor Hours Detail - September 2025:\n'
                    'Project Manager - 160 hrs @ $65.00/hr = $10,400.00\n'
                    'Senior Developer - 320 hrs @ $55.00/hr = $17,600.00\n'
                    'Junior Developer - 160 hrs @ $38.00/hr = $6,080.00',
                    'table', 1),
        _make_chunk(doc5, 2,
                    'Business Analyst - 120 hrs @ $45.00/hr = $5,400.00\n'
                    'QA Tester - 80 hrs @ $38.00/hr = $3,040.00\n'
                    'Travel Expenses (Reimbursable) - $880.00\n'
                    'Total Hours: 840 | Total Labor: $42,520.00 | '
                    'Total with Travel: $42,400.00',
                    'table', 1),
        _make_chunk(doc5, 3,
                    'Invoice Summary: Acme IT Services September 2025 monthly invoice '
                    'INV-2025-1147 under contract GS-35F-99876. Total billable hours: 840 across '
                    '5 labor categories. Includes reimbursable travel of $880. Payment terms: '
                    'Net 30. Remit to: Acme IT Services LLC, 1234 Tech Park Drive, Reston, VA 20190.',
                    'paragraph', 2),
    ])

    # --- Doc 6: Cisco SmartNet ---
    doc6 = 'd0000006-0000-0000-0000-000000000006'
    chunks.extend([
        _make_chunk(doc6, 0,
                    'Document: CSC-REN-2025-334 | Vendor: Cisco Systems | Date: 2025-11-15 | '
                    'Type: Vendor Quote | Total: $28,500.00 | Description: Cisco SmartNet '
                    'renewal quote for network infrastructure maintenance and software licensing. '
                    'Covers switches, routers, firewalls, wireless, and security software.',
                    'metadata', 1),
        _make_chunk(doc6, 1,
                    'SmartNet Maintenance Renewals:\n'
                    'Catalyst 9300 SmartNet (CON-SSSNT-C93004UE) - 5 units @ $1,200.00 = $6,000.00\n'
                    'Catalyst 9200 SmartNet (CON-SSSNT-C92002UE) - 10 units @ $650.00 = $6,500.00\n'
                    'ISR 4331 SmartNet (CON-SSSNT-ISR4331) - 3 units @ $900.00 = $2,700.00\n'
                    'ASA 5525-X SmartNet (CON-SSSNT-ASA5525) - 2 units @ $1,800.00 = $3,600.00',
                    'table', 1),
        _make_chunk(doc6, 2,
                    'Software Licensing:\n'
                    'Meraki MR46 3-Year License (LIC-MR-3YR) - 20 APs @ $200.00 = $4,000.00\n'
                    'AnyConnect Plus 3-Year (L-AC-PLS-3Y-S4) - 500 users @ $8.00 = $4,000.00\n'
                    'Umbrella DNS Security (UMB-INSIGHTS-K9) - 500 users @ $2.80 = $1,400.00\n'
                    'DNA Essentials 3-Year (C9300-DNA-E-3Y) - 5 switches @ $300.00 = $1,500.00',
                    'table', 1),
        _make_chunk(doc6, 3,
                    'Pricing Notes: Quoted total $28,500.00 reflects volume discount on SmartNet '
                    'renewals. List price total would be $29,700.00. Discount of ~4% applied to '
                    'maintenance line items for multi-year commitment.',
                    'paragraph', 2),
        _make_chunk(doc6, 4,
                    'Renewal Summary: Cisco SmartNet and licensing renewal CSC-REN-2025-334 '
                    'covering 20 network devices and 500 user licenses. Mix of 1-year SmartNet '
                    'maintenance and 3-year software subscriptions. Coverage period: Jan 1, 2026 '
                    'through Dec 31, 2028 (licensing) / Dec 31, 2026 (SmartNet).',
                    'paragraph', 2),
    ])

    # --- Doc 7: Help Desk Mod ---
    doc7 = 'd0000007-0000-0000-0000-000000000007'
    chunks.extend([
        _make_chunk(doc7, 0,
                    'Document: MOD-003 | Vendor: Acme IT Services LLC | Date: 2025-09-15 | '
                    'Type: Contract Modification | Contract: GS-35F-99876 | Total: $156,000.00 | '
                    'Period: Oct 1, 2025 - Sep 30, 2026 | Description: Modification 003 to '
                    'extend help desk Tier 1 and Tier 2 support services for 12 additional months.',
                    'metadata', 1),
        _make_chunk(doc7, 1,
                    'Modified CLINs:\n'
                    'CLIN 0001: Help Desk Tier 1 Support - 12 months @ $5,500.00/mo = $66,000.00\n'
                    '  Scope: Password resets, account provisioning, basic troubleshooting, '
                    '8x5 coverage, 15-min SLA for P1 incidents.\n'
                    'CLIN 0002: Help Desk Tier 2 Support - 12 months @ $7,500.00/mo = $90,000.00\n'
                    '  Scope: Application support, network troubleshooting, escalation management, '
                    '8x5 coverage.',
                    'table', 1),
        _make_chunk(doc7, 2,
                    'CLIN 0003: After-hours Emergency Support - Added at no additional cost.\n'
                    'Scope: After-hours on-call coverage for critical P1 incidents only. '
                    'Negotiated as part of MOD-003 at $0.00. Available 24/7 for emergencies.\n'
                    'Note: $0 CLIN added per government negotiation - unusual pricing.',
                    'table', 2),
        _make_chunk(doc7, 3,
                    'Modification Justification: Continuation of essential IT help desk services '
                    'to maintain operational continuity. Option year 3 of 5-year IDIQ. '
                    'After-hours emergency support added per agency request at no cost increase.',
                    'paragraph', 2),
        _make_chunk(doc7, 4,
                    'MOD Summary: Contract modification MOD-003 under GS-35F-99876 extends help '
                    'desk support for 12 months at $156,000.00. Includes Tier 1 ($66K) and '
                    'Tier 2 ($90K) support plus complimentary after-hours emergency coverage. '
                    'Contracting Officer: J. Smith. Total contract ceiling after mod: $624,000.00.',
                    'paragraph', 3),
    ])

    # --- Doc 8: Server BOM ---
    doc8 = 'd0000008-0000-0000-0000-000000000008'
    chunks.extend([
        _make_chunk(doc8, 0,
                    'Document: BOM-SRV-2025-01 | Vendor: Dell Technologies | Date: 2025-05-20 | '
                    'Type: Bill of Materials | Total: $47,200.00 | Description: Bill of materials '
                    'for two Dell PowerEdge R750 server builds for data center refresh.',
                    'metadata', 1),
        _make_chunk(doc8, 1,
                    'Server Components - Compute:\n'
                    'Dell PowerEdge R750 Chassis (210-AZYB) - 2 @ $4,500.00 = $9,000.00\n'
                    'Intel Xeon Gold 6338 CPU (338-CBXJ) - 4 (2 per server) @ $2,100.00 = $8,400.00\n'
                    '32GB DDR4 3200MHz RDIMM (AA810826) - 16 (8 per server) @ $180.00 = $2,880.00',
                    'table', 1),
        _make_chunk(doc8, 2,
                    'Server Components - Storage & Networking:\n'
                    '960GB SSD SATA Mixed Use (345-BBFX) - 8 (4 per server) @ $450.00 = $3,600.00\n'
                    '1.92TB NVMe Mixed Use (345-BDRD) - 4 (2 per server) @ $1,200.00 = $4,800.00\n'
                    'Broadcom 57416 10GbE NIC (540-BBVM) - 4 (2 per server) @ $250.00 = $1,000.00',
                    'table', 1),
        _make_chunk(doc8, 3,
                    'Server Components - Management & Support:\n'
                    'iDRAC9 Enterprise License (385-BBOW) - 2 @ $300.00 = $600.00\n'
                    'ReadyRails Kit (770-BCHJ) - 2 @ $60.00 = $120.00\n'
                    '3-Year ProSupport Plus 4Hr (812-4012) - 2 @ $1,400.00 = $2,800.00\n'
                    'Total BOM: $47,200.00 ($23,600 per server)',
                    'table', 2),
    ])

    db.session.add_all(chunks)
    db.session.flush()

    # ── Single commit ──
    db.session.commit()

    print(f'  Users:             2')
    print(f'  Documents:         {len(docs)}')
    print(f'  Line items:        {len(line_items)}')
    print(f'  Canonical products:{len(products)}')
    print(f'  Field mappings:    {len(mappings)}')
    print(f'  Document chunks:   {len(chunks)}')
