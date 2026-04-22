"""Utility functions for WAU State portal."""

from io import BytesIO
from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from datetime import datetime


def generate_investment_brief_pdf():
    """Generate investment brief PDF with sectors, opportunities, and incentives."""
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0f3f66'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#0f3f66'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=10,
        leading=14
    )
    
    # Title
    story.append(Paragraph('INVESTMENT BRIEF', title_style))
    story.append(Paragraph('Western Bahr el Ghazal State', heading_style))
    story.append(Paragraph(f'<b>Prepared:</b> {datetime.now().strftime("%B %d, %Y")}', body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Executive Summary
    story.append(Paragraph('EXECUTIVE SUMMARY', heading_style))
    story.append(Paragraph(
        'Western Bahr el Ghazal (WAU) State represents a strategic investment destination in Central Africa. '
        'With government commitment to sustainable development, transparent policies, and competitive incentives, '
        'WAU State offers high-return opportunities across key sectors including agriculture, renewable energy, '
        'infrastructure, technology, manufacturing, and healthcare.',
        body_style
    ))
    story.append(Spacer(1, 0.15*inch))
    
    # Investment Highlights
    story.append(Paragraph('INVESTMENT HIGHLIGHTS', heading_style))
    highlights = [
        'Strategic location bridging Central and East Africa',
        'Emerging market with high growth potential',
        'Government backing with transparent legal framework',
        'Competitive tax incentives for priority sectors',
        'Growing private sector ecosystem',
        'Skilled workforce and market demand',
    ]
    for highlight in highlights:
        story.append(Paragraph(f'• {highlight}', body_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Investment Sectors
    story.append(Paragraph('KEY INVESTMENT SECTORS', heading_style))
    
    sectors_data = [
        ('AGRICULTURE', 'Modern farming, processing, value-added products', 'High'),
        ('RENEWABLE ENERGY', 'Solar, wind, hydroelectric power projects', 'High'),
        ('INFRASTRUCTURE', 'Roads, water systems, connectivity', 'Medium'),
        ('TECHNOLOGY', 'Digital transformation, fintech, telecom', 'High'),
        ('MANUFACTURING', 'Light manufacturing, food processing', 'Medium'),
        ('HEALTHCARE', 'Medical facilities, pharmaceutical distribution', 'Medium'),
    ]
    
    sector_table_data = [['Sector', 'Focus Areas', 'Growth Potential']]
    for sector, focus, potential in sectors_data:
        sector_table_data.append([sector, focus, potential])
    
    sector_table = Table(sector_table_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch])
    sector_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f3f66')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d4af37')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
    ]))
    story.append(sector_table)
    story.append(Spacer(1, 0.15*inch))
    
    # Government Incentives
    story.append(PageBreak())
    story.append(Paragraph('GOVERNMENT INCENTIVES', heading_style))
    
    incentives = [
        'Tax holidays for priority sectors (3-7 years)',
        'Priority access to government procurement tenders',
        'Facilitated land and natural resource access',
        'Infrastructure guarantees and support',
        'Workforce training and capacity building programs',
        'Customs duty exemptions for equipment imports',
        'Accelerated business registration processes',
        'Foreign investor protection under legal framework',
    ]
    
    for incentive in incentives:
        story.append(Paragraph(f'✓ {incentive}', body_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Investment Process
    story.append(Paragraph('INVESTMENT PROCESS', heading_style))
    
    process_steps = [
        ('Step 1: Inquiry', 'Submit initial interest in opportunities of choice'),
        ('Step 2: Review', 'We evaluate investment fit and compatibility'),
        ('Step 3: Discussion', 'Detailed conversations on project specifics'),
        ('Step 4: Due Diligence', 'Comprehensive project and financial review'),
        ('Step 5: Partnership', 'Execute investment agreement and commence'),
    ]
    
    for step, description in process_steps:
        story.append(Paragraph(f'<b>{step}:</b> {description}', body_style))
        story.append(Spacer(1, 0.08*inch))
    story.append(Spacer(1, 0.15*inch))
    
    # Risk Management
    story.append(Paragraph('RISK MANAGEMENT & GOVERNANCE', heading_style))
    story.append(Paragraph(
        'All investment opportunities undergo rigorous due diligence. Investment agreements include: '
        'comprehensive risk mitigation clauses, government guarantees for certain sectors, dispute resolution mechanisms, '
        'and transparent financial reporting requirements. Our investment support team provides ongoing assistance '
        'to ensure project success.',
        body_style
    ))
    story.append(Spacer(1, 0.15*inch))
    
    # Contact Information
    story.append(PageBreak())
    story.append(Paragraph('CONTACT & NEXT STEPS', heading_style))
    story.append(Paragraph(
        'Interested in learning more? Visit our investment portal to explore current opportunities, '
        'filter by sector, and submit your inquiry directly. Our team will review and contact you within 24-48 hours.',
        body_style
    ))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph('Website: <b>Investment Portal</b>', body_style))
    story.append(Paragraph('Email: <b>investment@waustate.gov</b>', body_style))
    story.append(Paragraph('Phone: <b>+211 (0) XXX XXX XXX</b>', body_style))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph(
        '<i>This document is intended for potential investors. Please contact us for sector-specific briefs and detailed opportunity documents.</i>',
        body_style
    ))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def get_investment_brief_file_response():
    """Generate and return investment brief PDF as file response."""
    pdf_buffer = generate_investment_brief_pdf()
    return FileResponse(
        pdf_buffer,
        as_attachment=True,
        filename='WAU_Investment_Brief.pdf',
        content_type='application/pdf'
    )
