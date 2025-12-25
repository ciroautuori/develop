"""Email Templates - Week 2"""

def get_trial_welcome_email(email, end_date, amount=9.99):
    return {"subject": "Benvenuto Trial CV-Lab", "html": f"<h1>Trial attivo fino {end_date}</h1>"}

def get_trial_reminder_email(email, end_date):
    return {"subject": "Trial scade tra 3 giorni", "html": f"<h1>Scadenza: {end_date}</h1>"}

def get_last_chance_email(email, end_date, amount=9.99):
    return {"subject": "ULTIMO GIORNO trial", "html": f"<h1>Domani addebito €{amount}</h1>"}
