"""
Email Templates - HTML email templates for markettina.
Brand colors: Black #0a0a0a, Gold #D4AF37, White #ffffff
"""



def email_wrapper(content: str, preheader: str = "") -> str:
    """
    Email HTML wrapper con styling markettina.

    Args:
        content: HTML content del body
        preheader: Testo preview email
    """
    return f"""
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <!--[if mso]>
    <style type="text/css">
        body, table, td {{font-family: Arial, sans-serif !important;}}
    </style>
    <![endif]-->
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background-color: #f3f4f6;
        }}
        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
        }}
        .header {{
            background-color: #0a0a0a;
            padding: 32px 24px;
            text-align: center;
        }}
        .logo {{
            font-size: 28px;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: -0.5px;
        }}
        .logo-gold {{
            color: #D4AF37;
        }}
        .content {{
            padding: 40px 24px;
        }}
        .button {{
            display: inline-block;
            padding: 14px 32px;
            background-color: #D4AF37;
            color: #0a0a0a;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 16px;
        }}
        .footer {{
            background-color: #f9fafb;
            padding: 24px;
            text-align: center;
            font-size: 14px;
            color: #6b7280;
        }}
        h1 {{
            font-size: 28px;
            font-weight: 700;
            color: #0a0a0a;
            margin: 0 0 16px 0;
        }}
        p {{
            font-size: 16px;
            line-height: 1.6;
            color: #374151;
            margin: 0 0 16px 0;
        }}
        .preheader {{
            display: none;
            font-size: 1px;
            color: #ffffff;
            line-height: 1px;
            max-height: 0px;
            max-width: 0px;
            opacity: 0;
            overflow: hidden;
        }}
    </style>
</head>
<body>
    <span class="preheader">{preheader}</span>

    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #f3f4f6;">
        <tr>
            <td align="center" style="padding: 24px 16px;">
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" class="email-container">
                    <!-- Header -->
                    <tr>
                        <td class="header">
                            <div class="logo">
                                <span class="logo-gold">MARKETTINA</span>
                            </div>
                        </td>
                    </tr>

                    <!-- Content -->
                    <tr>
                        <td class="content">
                            {content}
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td class="footer">
                            <p style="margin: 0 0 8px 0;">© 2024 MARKETTINA. Tutti i diritti riservati.</p>
                            <p style="margin: 0;">
                                <a href="https://markettina.it" style="color: #D4AF37; text-decoration: none;">markettina.it</a>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
    """


def welcome_email(name: str, login_url: str = "https://markettina.it/admin/login") -> str:
    """Welcome email for new admin."""
    content = f"""
        <h1>Benvenuto in MARKETTINA! 👋</h1>
        <p>Ciao <strong>{name}</strong>,</p>
        <p>Il tuo account amministratore è stato creato con successo. Sei pronto a gestire i tuoi progetti AI-powered!</p>

        <p style="margin: 32px 0;">
            <a href="{login_url}" class="button">Accedi al Dashboard</a>
        </p>

        <p>Se hai domande, siamo qui per aiutarti.</p>
        <p>A presto,<br><strong>Team MARKETTINA</strong></p>
    """
    return email_wrapper(content, f"Benvenuto in MARKETTINA, {name}!")


def booking_confirmation_email(
    name: str,
    service_type: str,
    preferred_date: str,
    budget_range: str,
    booking_id: int
) -> str:
    """Booking confirmation email."""
    content = f"""
        <h1>Prenotazione Ricevuta! ✅</h1>
        <p>Ciao <strong>{name}</strong>,</p>
        <p>Abbiamo ricevuto la tua richiesta di consulenza. Ti risponderemo entro 24 ore!</p>

        <table style="width: 100%; margin: 24px 0; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;">
            <tr style="background-color: #f9fafb;">
                <td style="padding: 12px; font-weight: 600; border-bottom: 1px solid #e5e7eb;">Dettagli Prenotazione #{booking_id}</td>
            </tr>
            <tr>
                <td style="padding: 12px;">
                    <p style="margin: 8px 0;"><strong>Servizio:</strong> {service_type}</p>
                    <p style="margin: 8px 0;"><strong>Data preferita:</strong> {preferred_date or 'Da concordare'}</p>
                    <p style="margin: 8px 0;"><strong>Budget:</strong> {budget_range}</p>
                </td>
            </tr>
        </table>

        <p>Nel frattempo, puoi esplorare i nostri progetti sul portfolio.</p>

        <p style="margin: 32px 0;">
            <a href="https://markettina.it/#portfolio" class="button">Vedi Portfolio</a>
        </p>

        <p>Grazie per aver scelto MARKETTINA!<br><strong>Team MARKETTINA</strong></p>
    """
    return email_wrapper(content, f"Prenotazione #{booking_id} confermata!")


def contact_confirmation_email(name: str, subject: str) -> str:
    """Contact form confirmation email."""
    content = f"""
        <h1>Messaggio Ricevuto! 📬</h1>
        <p>Ciao <strong>{name}</strong>,</p>
        <p>Abbiamo ricevuto il tuo messaggio riguardo: <em>{subject}</em></p>
        <p>Ti risponderemo al più presto, solitamente entro 24 ore lavorative.</p>

        <p style="margin: 32px 0;">
            <a href="https://markettina.it" class="button">Visita il Sito</a>
        </p>

        <p>Grazie per averci contattato!<br><strong>Team MARKETTINA</strong></p>
    """
    return email_wrapper(content, f"Messaggio ricevuto: {subject}")


def password_reset_email(name: str, reset_token: str, reset_url: str) -> str:
    """Password reset email."""
    full_reset_url = f"{reset_url}?token={reset_token}"

    content = f"""
        <h1>Reset Password 🔐</h1>
        <p>Ciao <strong>{name}</strong>,</p>
        <p>Abbiamo ricevuto una richiesta di reset della tua password.</p>
        <p>Clicca sul pulsante qui sotto per impostare una nuova password:</p>

        <p style="margin: 32px 0;">
            <a href="{full_reset_url}" class="button">Reset Password</a>
        </p>

        <p style="font-size: 14px; color: #6b7280;">
            <strong>Nota:</strong> Questo link scadrà tra 1 ora per motivi di sicurezza.
        </p>

        <p style="font-size: 14px; color: #6b7280;">
            Se non hai richiesto questo reset, ignora questa email. La tua password rimarrà invariata.
        </p>

        <p>Cordiali saluti,<br><strong>Team MARKETTINA</strong></p>
    """
    return email_wrapper(content, "Reset della tua password")


def newsletter_template(
    name: str,
    subject: str,
    content_html: str,
    cta_text: str = "Scopri di più",
    cta_url: str = "https://markettina.it"
) -> str:
    """Newsletter template."""
    content = f"""
        <h1>{subject}</h1>
        <p>Ciao <strong>{name}</strong>,</p>

        {content_html}

        <p style="margin: 32px 0;">
            <a href="{cta_url}" class="button">{cta_text}</a>
        </p>

        <p style="font-size: 14px; color: #6b7280;">
            Ricevi questa email perché sei iscritto alla newsletter di MARKETTINA.
            <br>
            <a href="https://markettina.it/unsubscribe" style="color: #6b7280;">Annulla iscrizione</a>
        </p>
    """
    return email_wrapper(content, subject)
