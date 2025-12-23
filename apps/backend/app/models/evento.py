"""
Modello Evento - Sistema Eventi e Workshop ISS
Eventi, workshop, hackathon GRATUITI e accessibili per la comunità salernitana
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum
from typing import Optional, List
from datetime import datetime


class EventoTipo(str, enum.Enum):
    """Tipologie di eventi ISS"""
    WORKSHOP = "workshop"
    HACKATHON = "hackathon"
    CONFERENZA = "conferenza"
    SEMINARIO = "seminario"
    MEETUP = "meetup"
    FORMAZIONE = "formazione"
    NETWORKING = "networking"
    PRESENTAZIONE = "presentazione"
    TAVOLA_ROTONDA = "tavola_rotonda"
    DEMO_DAY = "demo_day"
    OPEN_DAY = "open_day"
    VOLONTARIATO = "volontariato"


class EventoCategoria(str, enum.Enum):
    """Categorie tematiche degli eventi"""
    INNOVAZIONE_SOCIALE = "innovazione_sociale"
    TECNOLOGIA = "tecnologia"
    FORMAZIONE_DIGITALE = "formazione_digitale"
    TERZO_SETTORE = "terzo_settore"
    STARTUP = "startup"
    SOSTENIBILITA = "sostenibilita"
    INCLUSIONE = "inclusione"
    ACCESSIBILITA = "accessibilita"
    VOLONTARIATO = "volontariato"
    NETWORKING = "networking"
    BANDI_FINANZIAMENTI = "bandi_finanziamenti"
    COMPETENZE_DIGITALI = "competenze_digitali"


class EventoModalita(str, enum.Enum):
    """Modalità di partecipazione"""
    PRESENZA = "presenza"
    ONLINE = "online"
    IBRIDA = "ibrida"


class EventoStato(str, enum.Enum):
    """Stati dell'evento"""
    BOZZA = "bozza"
    PUBBLICATO = "pubblicato"
    ISCRIZIONI_APERTE = "iscrizioni_aperte"
    ISCRIZIONI_CHIUSE = "iscrizioni_chiuse"
    IN_CORSO = "in_corso"
    COMPLETATO = "completato"
    ANNULLATO = "annullato"
    RIMANDATO = "rimandato"


class EventoTarget(str, enum.Enum):
    """Target audience dell'evento"""
    TUTTI = "tutti"
    APS = "aps"
    CITTADINI = "cittadini"
    VOLONTARI = "volontari"
    STUDENTI = "studenti"
    PROFESSIONISTI = "professionisti"
    STARTUP = "startup"
    ENTI_PUBBLICI = "enti_pubblici"
    DISABILI = "disabili"
    ANZIANI = "anziani"


class Evento(Base):
    """
    Modello per eventi, workshop e attività ISS
    Tutti gli eventi sono GRATUITI e accessibili
    """
    __tablename__ = "eventi"

    # Identificatori
    id = Column(Integer, primary_key=True, index=True)
    codice_evento = Column(String(20), unique=True, index=True, nullable=False)  # es: "ISS-EVT-2025-001"
    
    # Informazioni base
    titolo = Column(String(200), nullable=False, index=True)
    sottotitolo = Column(String(300), nullable=True)
    descrizione = Column(Text, nullable=False)
    descrizione_breve = Column(String(500), nullable=False)
    
    # Categorizzazione
    tipo = Column(Enum(EventoTipo), nullable=False, index=True)
    categoria = Column(Enum(EventoCategoria), nullable=False, index=True)
    modalita = Column(Enum(EventoModalita), nullable=False, index=True)
    stato = Column(Enum(EventoStato), default=EventoStato.BOZZA, nullable=False, index=True)
    target = Column(Enum(EventoTarget), nullable=False, index=True)
    
    # Date e orari
    data_inizio = Column(DateTime, nullable=False, index=True)
    data_fine = Column(DateTime, nullable=False, index=True)
    durata_ore = Column(Numeric(4, 2), nullable=False)  # Durata in ore (es: 2.5)
    
    # Iscrizioni
    data_apertura_iscrizioni = Column(DateTime, nullable=True, index=True)
    data_chiusura_iscrizioni = Column(DateTime, nullable=True, index=True)
    iscrizioni_aperte = Column(Boolean, default=False, nullable=False)
    iscrizione_obbligatoria = Column(Boolean, default=True, nullable=False)
    
    # Capacità
    max_partecipanti = Column(Integer, nullable=True)  # NULL = illimitato
    min_partecipanti = Column(Integer, nullable=True, default=1)
    numero_iscritti = Column(Integer, default=0, nullable=False)
    lista_attesa = Column(Boolean, default=True, nullable=False)
    
    # Logistica - Presenza
    sede = Column(String(200), nullable=True)
    indirizzo = Column(String(300), nullable=True)
    citta = Column(String(100), nullable=True, default="Salerno")
    cap = Column(String(5), nullable=True)
    aula_sala = Column(String(100), nullable=True)
    indicazioni_sede = Column(Text, nullable=True)
    
    # Logistica - Online
    link_evento = Column(String(500), nullable=True)  # Zoom, Meet, Teams
    password_evento = Column(String(100), nullable=True)
    istruzioni_accesso = Column(Text, nullable=True)
    
    # Organizzazione
    organizzatore_principale = Column(String(200), nullable=False, default="ISS - Innovazione Sociale Salernitana")
    co_organizzatori = Column(Text, nullable=True)  # JSON array di organizzatori
    contatto_email = Column(String(100), nullable=True)
    contatto_telefono = Column(String(20), nullable=True)
    
    # Relatori e speaker
    relatori = Column(Text, nullable=True)  # JSON array di relatori
    moderatore = Column(String(200), nullable=True)
    
    # Programma
    agenda = Column(Text, nullable=True)  # JSON dell'agenda dettagliata
    materiali_forniti = Column(Text, nullable=True)
    prerequisiti = Column(Text, nullable=True)
    cosa_portare = Column(Text, nullable=True)
    
    # Accessibilità
    accessibile_disabili = Column(Boolean, default=True, nullable=False)
    parcheggio_disponibile = Column(Boolean, default=False, nullable=False)
    trasporti_pubblici = Column(Text, nullable=True)
    supporto_lis = Column(Boolean, default=False, nullable=False)
    materiali_braille = Column(Boolean, default=False, nullable=False)
    sottotitoli_live = Column(Boolean, default=False, nullable=False)
    assistenza_mobilita = Column(Boolean, default=False, nullable=False)
    
    # Servizi aggiuntivi
    registrazione_evento = Column(Boolean, default=False, nullable=False)
    streaming_live = Column(Boolean, default=False, nullable=False)
    coffee_break = Column(Boolean, default=False, nullable=False)
    pranzo_incluso = Column(Boolean, default=False, nullable=False)
    gadget_omaggio = Column(Boolean, default=False, nullable=False)
    
    # Certificazioni
    attestato_partecipazione = Column(Boolean, default=True, nullable=False)
    crediti_formativi = Column(Boolean, default=False, nullable=False)
    tipo_crediti = Column(String(100), nullable=True)
    ore_formative = Column(Numeric(4, 2), nullable=True)
    
    # Costi (sempre 0 per ISS)
    costo = Column(Numeric(10, 2), default=0.00, nullable=False)
    gratuito = Column(Boolean, default=True, nullable=False)
    
    # Follow-up
    survey_post_evento = Column(Boolean, default=True, nullable=False)
    materiali_post_evento = Column(Boolean, default=True, nullable=False)
    video_registrazione = Column(String(500), nullable=True)
    slides_evento = Column(String(500), nullable=True)
    
    # Valutazioni
    rating_medio = Column(Numeric(3, 2), nullable=True)  # 0.00 - 5.00
    numero_recensioni = Column(Integer, default=0, nullable=False)
    numero_partecipanti_effettivi = Column(Integer, default=0, nullable=False)
    
    # Partnership e sponsor
    partner_evento = Column(Text, nullable=True)  # JSON array di partner
    sponsor = Column(Text, nullable=True)  # JSON array di sponsor
    
    # Metadati
    creato_da_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    modificato_da_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # SEO e marketing
    slug = Column(String(250), unique=True, index=True, nullable=True)
    meta_description = Column(String(160), nullable=True)
    keywords = Column(String(500), nullable=True)
    immagine_copertina = Column(String(500), nullable=True)
    hashtag_ufficiale = Column(String(50), nullable=True)
    
    # Social media
    facebook_event = Column(String(500), nullable=True)
    linkedin_event = Column(String(500), nullable=True)
    eventbrite_url = Column(String(500), nullable=True)
    
    # Flags
    in_evidenza = Column(Boolean, default=False, nullable=False)
    pubblicato = Column(Boolean, default=False, nullable=False)
    archiviato = Column(Boolean, default=False, nullable=False)
    evento_ricorrente = Column(Boolean, default=False, nullable=False)

    # Relationships
    creato_da = relationship("User", foreign_keys=[creato_da_user_id])
    modificato_da = relationship("User", foreign_keys=[modificato_da_user_id])
    iscrizioni = relationship("EventoIscrizione", back_populates="evento", cascade="all, delete-orphan")
    recensioni = relationship("EventoRecensione", back_populates="evento", cascade="all, delete-orphan")
    check_ins = relationship("EventoCheckIn", back_populates="evento", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Evento(id={self.id}, codice='{self.codice_evento}', titolo='{self.titolo}')>"

    @property
    def posti_disponibili(self) -> Optional[int]:
        """Calcola i posti ancora disponibili (None se illimitato)"""
        if self.max_partecipanti is None:
            return None
        return max(0, self.max_partecipanti - self.numero_iscritti)

    @property
    def is_full(self) -> bool:
        """Verifica se l'evento è al completo"""
        if self.max_partecipanti is None:
            return False
        return self.numero_iscritti >= self.max_partecipanti

    @property
    def can_start(self) -> bool:
        """Verifica se l'evento può svolgersi (min partecipanti raggiunto)"""
        if self.min_partecipanti is None:
            return True
        return self.numero_iscritti >= self.min_partecipanti

    @property
    def is_online(self) -> bool:
        """Verifica se è un evento online"""
        return self.modalita in [EventoModalita.ONLINE, EventoModalita.IBRIDA]

    @property
    def is_in_presenza(self) -> bool:
        """Verifica se è un evento in presenza"""
        return self.modalita in [EventoModalita.PRESENZA, EventoModalita.IBRIDA]


class EventoIscrizione(Base):
    """Iscrizioni agli eventi"""
    __tablename__ = "evento_iscrizioni"

    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventi.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Stato iscrizione
    stato = Column(String(20), default="confermata", nullable=False)  # confermata, lista_attesa, annullata
    data_iscrizione = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    data_annullamento = Column(DateTime(timezone=True), nullable=True)
    
    # Partecipazione
    partecipato = Column(Boolean, default=False, nullable=False)
    check_in_effettuato = Column(Boolean, default=False, nullable=False)
    data_check_in = Column(DateTime(timezone=True), nullable=True)
    
    # Esigenze speciali
    esigenze_alimentari = Column(String(500), nullable=True)
    esigenze_accessibilita = Column(String(500), nullable=True)
    note_organizzatori = Column(Text, nullable=True)
    
    # Feedback
    feedback_evento = Column(Text, nullable=True)
    rating_evento = Column(Integer, nullable=True)  # 1-5 stelle
    survey_completata = Column(Boolean, default=False, nullable=False)
    
    # Certificazione
    attestato_rilasciato = Column(Boolean, default=False, nullable=False)
    data_attestato = Column(DateTime(timezone=True), nullable=True)
    codice_attestato = Column(String(50), unique=True, nullable=True)

    # Relationships
    evento = relationship("Evento")
    user = relationship("User")


class EventoCheckIn(Base):
    """Check-in agli eventi (QR code system)"""
    __tablename__ = "evento_check_ins"

    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventi.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Check-in data
    data_check_in = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metodo_check_in = Column(String(20), default="qr_code", nullable=False)  # qr_code, manuale, app
    
    # Location check-in
    latitudine = Column(Numeric(10, 8), nullable=True)
    longitudine = Column(Numeric(11, 8), nullable=True)
    
    # Device info
    device_info = Column(String(200), nullable=True)
    ip_address = Column(String(45), nullable=True)

    # Relationships
    evento = relationship("Evento")
    user = relationship("User")


class EventoRecensione(Base):
    """Recensioni e feedback sugli eventi"""
    __tablename__ = "evento_recensioni"

    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventi.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Valutazione generale
    rating = Column(Integer, nullable=False)  # 1-5 stelle
    titolo = Column(String(200), nullable=True)
    commento = Column(Text, nullable=True)
    
    # Valutazioni specifiche
    rating_contenuti = Column(Integer, nullable=True)      # 1-5
    rating_organizzazione = Column(Integer, nullable=True) # 1-5
    rating_relatori = Column(Integer, nullable=True)       # 1-5
    rating_sede = Column(Integer, nullable=True)           # 1-5
    rating_utilita = Column(Integer, nullable=True)        # 1-5
    
    # Feedback specifico
    cosa_migliorare = Column(Text, nullable=True)
    cosa_piaciuto_di_piu = Column(Text, nullable=True)
    raccomandazioni = Column(Text, nullable=True)
    
    # Raccomandazione
    raccomandato = Column(Boolean, nullable=True)
    parteciperebbe_ancora = Column(Boolean, nullable=True)
    
    # Metadati
    verificata = Column(Boolean, default=False, nullable=False)
    pubblicata = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    evento = relationship("Evento")
    user = relationship("User")
