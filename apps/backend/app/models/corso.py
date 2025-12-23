"""
Modello Corso - Sistema Formazione Digitale ISS
Corsi di alfabetizzazione digitale GRATUITI per cittadini salernitani
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum
from typing import Optional, List
from datetime import datetime


class CorsoLivello(str, enum.Enum):
    """Livelli di difficoltà dei corsi"""
    PRINCIPIANTE = "principiante"
    INTERMEDIO = "intermedio"
    AVANZATO = "avanzato"
    ESPERTO = "esperto"


class CorsoCategoria(str, enum.Enum):
    """Categorie dei corsi di formazione digitale"""
    ALFABETIZZAZIONE_BASE = "alfabetizzazione_base"
    OFFICE_AUTOMATION = "office_automation"
    INTERNET_EMAIL = "internet_email"
    SOCIAL_MEDIA = "social_media"
    SICUREZZA_DIGITALE = "sicurezza_digitale"
    SMARTPHONE_TABLET = "smartphone_tablet"
    SERVIZI_PUBBLICI_DIGITALI = "servizi_pubblici_digitali"
    E_COMMERCE = "e_commerce"
    CREATIVITA_DIGITALE = "creativita_digitale"
    PROGRAMMAZIONE = "programmazione"
    ACCESSIBILITA = "accessibilita"


class CorsoModalita(str, enum.Enum):
    """Modalità di erogazione del corso"""
    PRESENZA = "presenza"
    ONLINE = "online"
    IBRIDA = "ibrida"


class CorsoStato(str, enum.Enum):
    """Stati del corso"""
    BOZZA = "bozza"
    PUBBLICATO = "pubblicato"
    ISCRIZIONI_APERTE = "iscrizioni_aperte"
    ISCRIZIONI_CHIUSE = "iscrizioni_chiuse"
    IN_CORSO = "in_corso"
    COMPLETATO = "completato"
    ANNULLATO = "annullato"


class Corso(Base):
    """
    Modello per i corsi di formazione digitale ISS
    Tutti i corsi sono GRATUITI e accessibili
    """
    __tablename__ = "corsi"

    # Identificatori
    id = Column(Integer, primary_key=True, index=True)
    codice_corso = Column(String(20), unique=True, index=True, nullable=False)  # es: "ISS-2025-001"
    
    # Informazioni base
    titolo = Column(String(200), nullable=False, index=True)
    sottotitolo = Column(String(300), nullable=True)
    descrizione = Column(Text, nullable=False)
    descrizione_breve = Column(String(500), nullable=False)
    
    # Categorizzazione
    categoria = Column(Enum(CorsoCategoria), nullable=False, index=True)
    livello = Column(Enum(CorsoLivello), nullable=False, index=True)
    modalita = Column(Enum(CorsoModalita), nullable=False, index=True)
    stato = Column(Enum(CorsoStato), default=CorsoStato.BOZZA, nullable=False, index=True)
    
    # Dettagli corso
    durata_ore = Column(Integer, nullable=False)  # Durata totale in ore
    numero_lezioni = Column(Integer, nullable=False)
    max_partecipanti = Column(Integer, nullable=False, default=20)
    min_partecipanti = Column(Integer, nullable=False, default=5)
    
    # Prerequisiti e target
    prerequisiti = Column(Text, nullable=True)
    target_audience = Column(Text, nullable=False)
    obiettivi_apprendimento = Column(Text, nullable=False)
    competenze_acquisite = Column(Text, nullable=False)
    
    # Logistica
    sede = Column(String(200), nullable=True)  # Sede fisica se in presenza
    indirizzo = Column(String(300), nullable=True)
    aula = Column(String(100), nullable=True)
    link_online = Column(String(500), nullable=True)  # Link Zoom/Meet se online
    
    # Date e orari
    data_inizio = Column(DateTime, nullable=True, index=True)
    data_fine = Column(DateTime, nullable=True, index=True)
    orario_inizio = Column(String(5), nullable=True)  # "09:00"
    orario_fine = Column(String(5), nullable=True)    # "12:00"
    giorni_settimana = Column(String(20), nullable=True)  # "lun,mer,ven"
    
    # Iscrizioni
    data_apertura_iscrizioni = Column(DateTime, nullable=True, index=True)
    data_chiusura_iscrizioni = Column(DateTime, nullable=True, index=True)
    iscrizioni_aperte = Column(Boolean, default=False, nullable=False)
    
    # Docenza
    docente_nome = Column(String(100), nullable=True)
    docente_bio = Column(Text, nullable=True)
    docente_qualifiche = Column(Text, nullable=True)
    
    # Materiali e risorse
    materiali_forniti = Column(Text, nullable=True)
    software_necessario = Column(Text, nullable=True)
    hardware_necessario = Column(Text, nullable=True)
    
    # Certificazione
    certificato_rilasciato = Column(Boolean, default=True, nullable=False)
    tipo_certificato = Column(String(100), nullable=True)
    ore_minime_certificato = Column(Integer, nullable=True)
    
    # Accessibilità
    accessibile_disabili = Column(Boolean, default=True, nullable=False)
    supporto_lis = Column(Boolean, default=False, nullable=False)
    materiali_braille = Column(Boolean, default=False, nullable=False)
    sottotitoli_disponibili = Column(Boolean, default=True, nullable=False)
    
    # Costi (sempre 0 per ISS)
    costo = Column(Numeric(10, 2), default=0.00, nullable=False)
    gratuito = Column(Boolean, default=True, nullable=False)
    
    # Valutazioni e feedback
    rating_medio = Column(Numeric(3, 2), nullable=True)  # 0.00 - 5.00
    numero_recensioni = Column(Integer, default=0, nullable=False)
    
    # Statistiche
    numero_iscritti = Column(Integer, default=0, nullable=False)
    numero_completati = Column(Integer, default=0, nullable=False)
    tasso_completamento = Column(Numeric(5, 2), nullable=True)  # Percentuale
    
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
    
    # Flags
    in_evidenza = Column(Boolean, default=False, nullable=False)
    pubblicato = Column(Boolean, default=False, nullable=False)
    archiviato = Column(Boolean, default=False, nullable=False)

    # Relationships
    creato_da = relationship("User", foreign_keys=[creato_da_user_id])
    modificato_da = relationship("User", foreign_keys=[modificato_da_user_id])
    iscrizioni = relationship("CorsoIscrizione", back_populates="corso", cascade="all, delete-orphan")
    lezioni = relationship("CorsoLezione", back_populates="corso", cascade="all, delete-orphan")
    recensioni = relationship("CorsoRecensione", back_populates="corso", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Corso(id={self.id}, codice='{self.codice_corso}', titolo='{self.titolo}')>"

    @property
    def posti_disponibili(self) -> int:
        """Calcola i posti ancora disponibili"""
        return max(0, self.max_partecipanti - self.numero_iscritti)

    @property
    def is_full(self) -> bool:
        """Verifica se il corso è al completo"""
        return self.numero_iscritti >= self.max_partecipanti

    @property
    def can_start(self) -> bool:
        """Verifica se il corso può iniziare (min partecipanti raggiunto)"""
        return self.numero_iscritti >= self.min_partecipanti


class CorsoIscrizione(Base):
    """Iscrizioni ai corsi"""
    __tablename__ = "corso_iscrizioni"

    id = Column(Integer, primary_key=True, index=True)
    corso_id = Column(Integer, ForeignKey("corsi.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Stato iscrizione
    stato = Column(String(20), default="attiva", nullable=False)  # attiva, completata, ritirata
    data_iscrizione = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    data_completamento = Column(DateTime(timezone=True), nullable=True)
    
    # Progress tracking
    lezioni_completate = Column(Integer, default=0, nullable=False)
    ore_frequentate = Column(Numeric(5, 2), default=0.00, nullable=False)
    percentuale_completamento = Column(Numeric(5, 2), default=0.00, nullable=False)
    
    # Certificazione
    certificato_rilasciato = Column(Boolean, default=False, nullable=False)
    data_certificato = Column(DateTime(timezone=True), nullable=True)
    codice_certificato = Column(String(50), unique=True, nullable=True)
    
    # Valutazione
    voto_finale = Column(Numeric(3, 2), nullable=True)  # 0.00 - 10.00
    feedback_corso = Column(Text, nullable=True)
    rating_corso = Column(Integer, nullable=True)  # 1-5 stelle

    # Relationships
    corso = relationship("Corso", back_populates="iscrizioni")
    user = relationship("User")


class CorsoLezione(Base):
    """Lezioni del corso"""
    __tablename__ = "corso_lezioni"

    id = Column(Integer, primary_key=True, index=True)
    corso_id = Column(Integer, ForeignKey("corsi.id"), nullable=False)
    
    # Dettagli lezione
    numero_lezione = Column(Integer, nullable=False)
    titolo = Column(String(200), nullable=False)
    descrizione = Column(Text, nullable=True)
    durata_minuti = Column(Integer, nullable=False)
    
    # Programmazione
    data_lezione = Column(DateTime, nullable=True)
    orario_inizio = Column(String(5), nullable=True)
    orario_fine = Column(String(5), nullable=True)
    
    # Contenuti
    materiali_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    slides_url = Column(String(500), nullable=True)
    esercizi_url = Column(String(500), nullable=True)
    
    # Stato
    completata = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    corso = relationship("Corso", back_populates="lezioni")


class CorsoRecensione(Base):
    """Recensioni e feedback sui corsi"""
    __tablename__ = "corso_recensioni"

    id = Column(Integer, primary_key=True, index=True)
    corso_id = Column(Integer, ForeignKey("corsi.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Valutazione
    rating = Column(Integer, nullable=False)  # 1-5 stelle
    titolo = Column(String(200), nullable=True)
    commento = Column(Text, nullable=True)
    
    # Valutazioni specifiche
    rating_contenuti = Column(Integer, nullable=True)  # 1-5
    rating_docente = Column(Integer, nullable=True)    # 1-5
    rating_organizzazione = Column(Integer, nullable=True)  # 1-5
    rating_utilita = Column(Integer, nullable=True)    # 1-5
    
    # Raccomandazione
    raccomandato = Column(Boolean, nullable=True)
    
    # Metadati
    verificata = Column(Boolean, default=False, nullable=False)
    pubblicata = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    corso = relationship("Corso", back_populates="recensioni")
    user = relationship("User")
