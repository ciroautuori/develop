"""
Quote Email Service - Send quotes via email with PDF attachment.

Handles email sending for quotes using SMTP or SendGrid/SES.
"""

import os
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import List, Optional
import smtplib

from jinja2 import Template

from app.core.config import settings
from app.domain.quotes.models import Quote
from app.domain.quotes.pdf_generator import generate_quote_pdf


class QuoteEmailService:
    """Service for sending quote emails."""

    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', 'info@studiocentos.it')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', 'info@studiocentos.it')
        self.from_name = os.getenv('FROM_NAME', 'StudioCentOS')

    def send_quote(
        self,
        quote: Quote,
        to_email: str,
        cc_emails: Optional[List[str]] = None,
        custom_message: Optional[str] = None
    ) -> bool:
        """
        Send quote via email with PDF attachment.

        Args:
            quote: Quote instance
            to_email: Recipient email address
            cc_emails: Optional list of CC email addresses
            custom_message: Optional custom message to include

        Returns:
            bool: True if sent successfully
        """
        try:
            # Generate PDF
            pdf_path = generate_quote_pdf(quote)

            # Create email message
            msg = MIMEMultipart()
            msg['From'] = f'{self.from_name} <{self.from_email}>'
            msg['To'] = to_email
            msg['Subject'] = f'Quote {quote.quote_number} - {quote.title}'

            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)

            # Email body
            body = self._render_email_body(quote, custom_message)
            msg.attach(MIMEText(body, 'html'))

            # Attach PDF
            with open(pdf_path, 'rb') as f:
                pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
                pdf_attachment.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=f'{quote.quote_number}.pdf'
                )
                msg.attach(pdf_attachment)

            # Send email
            recipients = [to_email]
            if cc_emails:
                recipients.extend(cc_emails)

            self._send_smtp(msg, recipients)

            return True

        except Exception as e:
            print(f"Error sending quote email: {e}")
            return False

    def _render_email_body(self, quote: Quote, custom_message: Optional[str] = None) -> str:
        """Render HTML email body."""
        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #1e40af; color: white; padding: 30px; text-align: center; }
        .header h1 { margin: 0; font-size: 24px; }
        .content { padding: 30px; background: #f9fafb; }
        .quote-details { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .quote-details table { width: 100%; }
        .quote-details td { padding: 8px 0; }
        .quote-details td:first-child { font-weight: bold; color: #6b7280; }
        .total { font-size: 24px; color: #1e40af; font-weight: bold; }
        .cta { text-align: center; margin: 30px 0; }
        .cta a { background: #1e40af; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; }
        .footer { text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>StudioCentOS</h1>
            <p>AI-Powered Development Platform</p>
        </div>

        <div class="content">
            <h2>Dear {{ customer_name }},</h2>

            {% if custom_message %}
            <p>{{ custom_message }}</p>
            {% else %}
            <p>Thank you for your interest in our services. Please find attached our quote for your project.</p>
            {% endif %}

            <div class="quote-details">
                <table>
                    <tr>
                        <td>Quote Number:</td>
                        <td>{{ quote_number }}</td>
                    </tr>
                    <tr>
                        <td>Project:</td>
                        <td>{{ title }}</td>
                    </tr>
                    <tr>
                        <td>Valid Until:</td>
                        <td>{{ valid_until }}</td>
                    </tr>
                    <tr>
                        <td>Total Amount:</td>
                        <td class="total">€{{ total }}</td>
                    </tr>
                </table>
            </div>

            <p>The detailed quote is attached to this email as a PDF document.</p>

            <p>If you have any questions or would like to discuss the quote, please don't hesitate to contact us.</p>

            <div class="cta">
                <a href="mailto:{{ from_email }}">Contact Us</a>
            </div>
        </div>

        <div class="footer">
            <p>StudioCentOS | info@studiocentos.it | www.studiocentos.it</p>
            <p>This quote is valid until {{ valid_until }}</p>
        </div>
    </div>
</body>
</html>
        """)

        return template.render(
            customer_name=quote.customer.name,
            quote_number=quote.quote_number,
            title=quote.title,
            valid_until=quote.valid_until.strftime('%d/%m/%Y'),
            total=f"{quote.total:,.2f}",
            from_email=self.from_email,
            custom_message=custom_message,
        )

    def _send_smtp(self, msg: MIMEMultipart, recipients: List[str]):
        """Send email via SMTP."""
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg, to_addrs=recipients)


# Singleton instance
email_service = QuoteEmailService()


def send_quote_email(
    quote: Quote,
    to_email: str,
    cc_emails: Optional[List[str]] = None,
    custom_message: Optional[str] = None
) -> bool:
    """
    Send quote email.

    Args:
        quote: Quote instance
        to_email: Recipient email
        cc_emails: Optional CC emails
        custom_message: Optional custom message

    Returns:
        bool: True if sent successfully
    """
    return email_service.send_quote(quote, to_email, cc_emails, custom_message)
