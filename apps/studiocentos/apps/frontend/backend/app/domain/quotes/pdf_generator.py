"""
Quote PDF Generator - ReportLab Integration.

Generates professional PDF documents for quotes with company branding,
line items table, totals, and terms & conditions.
"""

from decimal import Decimal
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
)
from reportlab.pdfgen import canvas

from app.core.config import settings
from app.domain.quotes.models import Quote


class QuotePDFGenerator:
    """
    PDF generator for quotes using ReportLab.
    """

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.page_width, self.page_height = A4

        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
        )

        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#374151'),
            spaceBefore=20,
            spaceAfter=10,
        )

    def generate(self, quote: Quote, output_path: Optional[str] = None) -> str:
        """
        Generate PDF for a quote.

        Args:
            quote: Quote instance with line_items loaded
            output_path: Optional custom output path

        Returns:
            str: Path to generated PDF file
        """
        if output_path is None:
            # Default: save to media/quotes/
            pdf_dir = Path(settings.MEDIA_ROOT) / 'quotes'
            pdf_dir.mkdir(parents=True, exist_ok=True)
            output_path = str(pdf_dir / f"{quote.quote_number}.pdf")

        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
        )

        # Build content
        story = []

        # Header - Company info
        story.append(self._build_header())
        story.append(Spacer(1, 1*cm))

        # Title
        story.append(Paragraph(f"Quote {quote.quote_number}", self.title_style))
        story.append(Spacer(1, 0.5*cm))

        # Quote details
        story.append(self._build_quote_details(quote))
        story.append(Spacer(1, 0.7*cm))

        # Customer details
        story.append(self._build_customer_details(quote))
        story.append(Spacer(1, 1*cm))

        # Line items table
        story.append(Paragraph("Items", self.heading_style))
        story.append(self._build_line_items_table(quote))
        story.append(Spacer(1, 1*cm))

        # Totals
        story.append(self._build_totals_table(quote))
        story.append(Spacer(1, 1*cm))

        # Payment terms
        if quote.payment_terms:
            story.append(Paragraph("Payment Terms", self.heading_style))
            story.append(Paragraph(quote.payment_terms, self.styles['Normal']))
            story.append(Spacer(1, 0.5*cm))

        # Terms and conditions
        if quote.terms_and_conditions:
            story.append(Paragraph("Terms & Conditions", self.heading_style))
            story.append(Paragraph(quote.terms_and_conditions, self.styles['Normal']))
            story.append(Spacer(1, 0.5*cm))

        # Notes to customer
        if quote.notes_to_customer:
            story.append(Paragraph("Notes", self.heading_style))
            story.append(Paragraph(quote.notes_to_customer, self.styles['Normal']))

        # Footer
        story.append(Spacer(1, 1*cm))
        story.append(self._build_footer(quote))

        # Build PDF
        doc.build(story)

        # Save to file
        with open(output_path, 'wb') as f:
            f.write(buffer.getvalue())

        return output_path

    def _build_header(self):
        """Build company header."""
        # Company logo: Add from settings.COMPANY_LOGO_PATH if configured
        data = [
            ['StudioCentOS'],
            ['AI-Powered Development Platform'],
            ['info@studiocentos.it | +39 XXX XXX XXXX'],
        ]

        table = Table(data, colWidths=[self.page_width - 4*cm])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 16),
            ('TEXTCOLOR', (0, 0), (0, 0), colors.HexColor('#1e40af')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#6b7280')),
        ]))

        return table

    def _build_quote_details(self, quote: Quote):
        """Build quote details section."""
        data = [
            ['Issue Date:', quote.issue_date.strftime('%d/%m/%Y')],
            ['Valid Until:', quote.valid_until.strftime('%d/%m/%Y')],
            ['Payment Terms:', f'{quote.payment_terms_days} days'],
        ]

        if quote.delivery_date:
            data.append(['Delivery Date:', quote.delivery_date.strftime('%d/%m/%Y')])

        table = Table(data, colWidths=[4*cm, 8*cm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#374151')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        return table

    def _build_customer_details(self, quote: Quote):
        """Build customer details section."""
        customer = quote.customer

        data = [
            [Paragraph('<b>Bill To:</b>', self.styles['Normal'])],
            [customer.name],
            [customer.email],
        ]

        if customer.company_name:
            data.insert(1, [customer.company_name])

        if customer.phone:
            data.append([customer.phone])

        # Address
        address_parts = []
        if customer.address_line1:
            address_parts.append(customer.address_line1)
        if customer.address_line2:
            address_parts.append(customer.address_line2)
        if customer.city:
            city_line = customer.city
            if customer.postal_code:
                city_line = f"{customer.postal_code} {city_line}"
            address_parts.append(city_line)
        if customer.country and customer.country != 'IT':
            address_parts.append(customer.country)

        for line in address_parts:
            data.append([line])

        table = Table(data, colWidths=[self.page_width - 4*cm])
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#374151')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        return table

    def _build_line_items_table(self, quote: Quote):
        """Build line items table."""
        # Header
        data = [[
            'Item',
            'Quantity',
            'Unit Price',
            'Discount',
            'Subtotal'
        ]]

        # Line items
        for item in quote.line_items:
            data.append([
                f"{item.name}\n{item.description or ''}",
                f"{item.quantity:.2f}",
                f"€{item.unit_price:.2f}",
                f"{item.discount_percentage:.0f}%" if item.discount_percentage > 0 else '-',
                f"€{item.subtotal:.2f}"
            ])

        table = Table(
            data,
            colWidths=[7*cm, 2.5*cm, 2.5*cm, 2*cm, 3*cm]
        )

        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#374151')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1f2937')),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ]))

        return table

    def _build_totals_table(self, quote: Quote):
        """Build totals table."""
        data = [
            ['Subtotal:', f"€{quote.subtotal:.2f}"],
        ]

        if quote.discount_percentage > 0:
            data.append([
                f'Discount ({quote.discount_percentage:.0f}%):',
                f"-€{quote.discount_amount:.2f}"
            ])

        data.extend([
            [f'Tax ({quote.tax_rate:.0f}%):', f"€{quote.tax_amount:.2f}"],
            ['', ''],  # Separator
            ['Total:', f"€{quote.total:.2f}"],
        ])

        table = Table(data, colWidths=[14*cm, 3*cm])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -3), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -3), 10),
            ('TEXTCOLOR', (0, 0), (-1, -3), colors.HexColor('#6b7280')),

            # Total row
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#1e40af')),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#1e40af')),
            ('TOPPADDING', (0, -1), (-1, -1), 10),
        ]))

        return table

    def _build_footer(self, quote: Quote):
        """Build footer."""
        footer_text = f"Quote valid until {quote.valid_until.strftime('%d/%m/%Y')} | Generated on {datetime.now().strftime('%d/%m/%Y %H:%M')}"

        para = Paragraph(
            footer_text,
            ParagraphStyle(
                'Footer',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#9ca3af'),
                alignment=1,  # Center
            )
        )

        return para


# Singleton instance
pdf_generator = QuotePDFGenerator()


def generate_quote_pdf(quote: Quote) -> str:
    """
    Generate PDF for a quote.

    Args:
        quote: Quote instance

    Returns:
        str: Path to generated PDF file
    """
    return pdf_generator.generate(quote)
