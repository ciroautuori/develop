"""
Modello Testimonial - Sistema Testimonianze ISS
Gestione testimonianze, recensioni e feedback degli utenti ISS
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum
from typing import Optional, List
from datetime import datetime


class TestimonialTipo(str, enum.Enum):
    """Tipologie di testimonianza"""
    CORSO = "corso"                    # Testimonianza su corso frequentato
    EVENTO = "evento"                  # Testimonianza su evento partecipato
    PROGETTO = "progetto"              # Testimonianza su progetto seguito
    VOLONTARIATO = "volontariato"      # Testimonianza esperienza volontariato
    BANDO = "bando"                    # Testimonianza su bando vinto
    PIATTAFORMA = "piattaforma"        # Testimonianza generale ISS
    PARTNERSHIP = "partnership"        # Testimonianza da partner
    SERVIZIO = "servizio"              # Testimonianza su servizio specifico
    FORMAZIONE = "formazione"          # Testimonianza formazione ricevuta
    SUPPORTO = "supporto"              # Testimonianza supporto ricevuto


class TestimonialCategoria(str, enum.Enum):
    """Categorie delle testimonianze"""
    IMPATTO_SOCIALE = "impatto_sociale"
    CRESCITA_PERSONALE = "crescita_personale"
    COMPETENZE_DIGITALI = "competenze_digitali"
    INCLUSIONE = "inclusione"
    ACCESSIBILITA = "accessibilita"
    NETWORKING = "networking"
    OPPORTUNITA_LAVORO = "opportunita_lavoro"
    INNOVAZIONE = "innovazione"
    COMMUNITY = "community"
    SOSTENIBILITA = "sostenibilita"
    EMPOWERMENT = "empowerment"
    TRASFORMAZIONE = "trasformazione"


class TestimonialStato(str, enum.Enum):
    """Stati della testimonianza"""
    BOZZA = "bozza"
    IN_REVISIONE = "in_revisione"
    APPROVATA = "approvata"
    PUBBLICATA = "pubblicata"
    RIFIUTATA = "rifiutata"
    ARCHIVIATA = "archiviata"


class TestimonialFormato(str, enum.Enum):
    """Formati della testimonianza"""
    TESTO = "testo"
    VIDEO = "video"
    AUDIO = "audio"
    IMMAGINE_TESTO = "immagine_testo"
    INTERVISTA = "intervista"
    CASE_STUDY = "case_study"


class Testimonial(Base):
    """
    Modello per testimonianze e feedback degli utenti ISS
    Raccolta di storie di successo e impatto sociale
    """
    __tablename__ = "testimonials"

    # Identificatori
    id = Column(Integer, primary_key=True, index=True)
    
    # Informazioni base
    titolo = Column(String(200), nullable=False, index=True)
    contenuto = Column(Text, nullable=False)
    contenuto_breve = Column(String(500), nullable=False)  # Versione condensata
    
    # Autore testimonianza
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # NULL se anonimo
    nome_autore = Column(String(100), nullable=False)  # Nome pubblico (può essere diverso da user)
    cognome_autore = Column(String(100), nullable=True)
    ruolo_autore = Column(String(150), nullable=True)  # es: "Presidente APS Verde Salerno"
    organizzazione_autore = Column(String(200), nullable=True)
    citta_autore = Column(String(100), nullable=True)
    
    # Categorizzazione
    tipo = Column(Enum(TestimonialTipo), nullable=False, index=True)
    categoria = Column(Enum(TestimonialCategoria), nullable=False, index=True)
    formato = Column(Enum(TestimonialFormato), default=TestimonialFormato.TESTO, nullable=False)
    stato = Column(Enum(TestimonialStato), default=TestimonialStato.BOZZA, nullable=False, index=True)
    
    # Valutazione
    rating = Column(Integer, nullable=False, index=True)  # 1-5 stelle
    rating_dettagliato = Column(Text, nullable=True)  # JSON con rating specifici
    
    # Contenuto multimediale
    immagine_autore = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    audio_url = Column(String(500), nullable=True)
    immagini_aggiuntive = Column(Text, nullable=True)  # JSON array di URL
    
    # Contesto e riferimenti
    corso_id = Column(Integer, ForeignKey("corsi.id"), nullable=True)
    evento_id = Column(Integer, ForeignKey("eventi.id"), nullable=True)
    progetto_id = Column(Integer, ForeignKey("progetti.id"), nullable=True)
    bando_id = Column(Integer, ForeignKey("bandi.id"), nullable=True)
    
    # Dettagli esperienza
    data_esperienza = Column(DateTime, nullable=True)  # Quando è avvenuta l'esperienza
    durata_esperienza = Column(String(100), nullable=True)  # "3 mesi", "1 anno", etc.
    risultati_ottenuti = Column(Text, nullable=True)
    competenze_acquisite = Column(Text, nullable=True)  # JSON array
    
    # Impatto e benefici
    impatto_personale = Column(Text, nullable=True)
    impatto_professionale = Column(Text, nullable=True)
    impatto_sociale = Column(Text, nullable=True)
    benefici_concreti = Column(Text, nullable=True)  # JSON array
    
    # Prima e dopo
    situazione_prima = Column(Text, nullable=True)
    situazione_dopo = Column(Text, nullable=True)
    cambiamenti_principali = Column(Text, nullable=True)
    
    # Raccomandazioni
    raccomandazione = Column(Text, nullable=True)
    consigli_altri = Column(Text, nullable=True)
    cosa_migliorare = Column(Text, nullable=True)
    
    # Dati quantitativi
    metriche_impatto = Column(Text, nullable=True)  # JSON con metriche specifiche
    numeri_significativi = Column(Text, nullable=True)  # JSON array
    
    # Autorizzazioni e privacy
    consenso_pubblicazione = Column(Boolean, default=False, nullable=False)
    consenso_marketing = Column(Boolean, default=False, nullable=False)
    consenso_contatto = Column(Boolean, default=False, nullable=False)
    anonimo = Column(Boolean, default=False, nullable=False)
    
    # Verifica e autenticità
    verificata = Column(Boolean, default=False, nullable=False)
    verificata_da_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    data_verifica = Column(DateTime(timezone=True), nullable=True)
    note_verifica = Column(Text, nullable=True)
    
    # Moderazione
    moderata = Column(Boolean, default=False, nullable=False)
    moderata_da_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    note_moderazione = Column(Text, nullable=True)
    
    # Timeline
    data_creazione = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    data_modifica = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    data_pubblicazione = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Engagement
    visualizzazioni = Column(Integer, default=0, nullable=False)
    like_count = Column(Integer, default=0, nullable=False)
    share_count = Column(Integer, default=0, nullable=False)
    
    # SEO e visibilità
    slug = Column(String(250), unique=True, index=True, nullable=True)
    meta_description = Column(String(160), nullable=True)
    keywords = Column(String(500), nullable=True)
    
    # Priorità e featured
    priorita = Column(Integer, default=0, nullable=False)  # 0=normale, 1=alta, 2=featured
    in_evidenza = Column(Boolean, default=False, nullable=False)
    homepage_featured = Column(Boolean, default=False, nullable=False)
    
    # Localizzazione
    lingua = Column(String(5), default="it", nullable=False)
    
    # Follow-up
    disponibile_intervista = Column(Boolean, default=False, nullable=False)
    disponibile_case_study = Column(Boolean, default=False, nullable=False)
    contatto_giornalisti = Column(Boolean, default=False, nullable=False)

    # Relationships
    autore = relationship("User", foreign_keys=[user_id])
    verificata_da = relationship("User", foreign_keys=[verificata_da_id])
    moderata_da = relationship("User", foreign_keys=[moderata_da_id])
    corso = relationship("Corso")
    evento = relationship("Evento")
    progetto = relationship("Progetto")
    bando = relationship("Bando")

    def __repr__(self):
        return f"<Testimonial(id={self.id}, titolo='{self.titolo}', rating={self.rating})>"

    @property
    def is_published(self) -> bool:
        """Verifica se la testimonianza è pubblicata"""
        return self.stato == TestimonialStato.PUBBLICATA

    @property
    def nome_completo_autore(self) -> str:
        """Restituisce il nome completo dell'autore"""
        if self.anonimo:
            return "Utente Anonimo"
        if self.cognome_autore:
            return f"{self.nome_autore} {self.cognome_autore}"
        return self.nome_autore

    @property
    def giorni_dalla_pubblicazione(self) -> Optional[int]:
        """Giorni dalla pubblicazione"""
        if not self.data_pubblicazione:
            return None
        delta = datetime.now() - self.data_pubblicazione
        return delta.days


class TestimonialRichiesta(Base):
    """Richieste di testimonianze inviate agli utenti"""
    __tablename__ = "testimonial_richieste"

    id = Column(Integer, primary_key=True, index=True)
    
    # Destinatario
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    email_destinatario = Column(String(100), nullable=False)
    nome_destinatario = Column(String(100), nullable=False)
    
    # Contesto richiesta
    tipo_richiesto = Column(Enum(TestimonialTipo), nullable=False)
    corso_id = Column(Integer, ForeignKey("corsi.id"), nullable=True)
    evento_id = Column(Integer, ForeignKey("eventi.id"), nullable=True)
    progetto_id = Column(Integer, ForeignKey("progetti.id"), nullable=True)
    
    # Messaggio personalizzato
    messaggio_richiesta = Column(Text, nullable=True)
    domande_specifiche = Column(Text, nullable=True)  # JSON array di domande
    
    # Stato richiesta
    stato = Column(String(20), default="inviata", nullable=False)  # inviata, vista, risposta, rifiutata
    data_invio = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    data_vista = Column(DateTime(timezone=True), nullable=True)
    data_risposta = Column(DateTime(timezone=True), nullable=True)
    
    # Risultato
    testimonial_id = Column(Integer, ForeignKey("testimonials.id"), nullable=True)
    motivo_rifiuto = Column(Text, nullable=True)
    
    # Metadati
    inviata_da_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_risposta = Column(String(100), unique=True, nullable=False)  # Token per link diretto
    
    # Reminder
    reminder_inviati = Column(Integer, default=0, nullable=False)
    prossimo_reminder = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    destinatario = relationship("User", foreign_keys=[user_id])
    inviata_da = relationship("User", foreign_keys=[inviata_da_id])
    testimonial = relationship("Testimonial")
    corso = relationship("Corso")
    evento = relationship("Evento")
    progetto = relationship("Progetto")


class TestimonialTemplate(Base):
    """Template per richieste di testimonianze"""
    __tablename__ = "testimonial_templates"

    id = Column(Integer, primary_key=True, index=True)
    
    # Informazioni template
    nome = Column(String(100), nullable=False)
    descrizione = Column(Text, nullable=True)
    tipo_target = Column(Enum(TestimonialTipo), nullable=False)
    
    # Contenuto template
    oggetto_email = Column(String(200), nullable=False)
    messaggio_template = Column(Text, nullable=False)
    domande_template = Column(Text, nullable=False)  # JSON array di domande
    
    # Configurazione
    attivo = Column(Boolean, default=True, nullable=False)
    automatico = Column(Boolean, default=False, nullable=False)  # Invio automatico
    delay_giorni = Column(Integer, nullable=True)  # Giorni dopo l'evento per invio auto
    
    # Metadati
    creato_da_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Statistiche
    utilizzi_totali = Column(Integer, default=0, nullable=False)
    tasso_risposta = Column(Numeric(5, 2), nullable=True)  # Percentuale di risposta

    # Relationships
    creato_da = relationship("User")


class TestimonialMetrica(Base):
    """Metriche e analytics delle testimonianze"""
    __tablename__ = "testimonial_metriche"

    id = Column(Integer, primary_key=True, index=True)
    testimonial_id = Column(Integer, ForeignKey("testimonials.id"), nullable=False)
    
    # Data metrica
    data_metrica = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Metriche engagement
    visualizzazioni_giorno = Column(Integer, default=0, nullable=False)
    like_giorno = Column(Integer, default=0, nullable=False)
    share_giorno = Column(Integer, default=0, nullable=False)
    
    # Sorgenti traffico
    traffico_diretto = Column(Integer, default=0, nullable=False)
    traffico_social = Column(Integer, default=0, nullable=False)
    traffico_email = Column(Integer, default=0, nullable=False)
    traffico_search = Column(Integer, default=0, nullable=False)
    
    # Device
    desktop_views = Column(Integer, default=0, nullable=False)
    mobile_views = Column(Integer, default=0, nullable=False)
    tablet_views = Column(Integer, default=0, nullable=False)

    # Relationships
    testimonial = relationship("Testimonial")
