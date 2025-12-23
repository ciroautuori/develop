"""
Modello Volontariato - Sistema Volontariato ISS
Gestione candidature, matching e attività di volontariato
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum
from typing import Optional, List
from datetime import datetime


class VolontariatoArea(str, enum.Enum):
    """Aree di volontariato ISS"""
    FORMAZIONE_DIGITALE = "formazione_digitale"
    SUPPORTO_TECNICO = "supporto_tecnico"
    EVENTI_ORGANIZZAZIONE = "eventi_organizzazione"
    COMUNICAZIONE_MARKETING = "comunicazione_marketing"
    RICERCA_BANDI = "ricerca_bandi"
    ASSISTENZA_UTENTI = "assistenza_utenti"
    SVILUPPO_SOFTWARE = "sviluppo_software"
    DESIGN_GRAFICO = "design_grafico"
    TRADUZIONE = "traduzione"
    ACCESSIBILITA = "accessibilita"
    FUNDRAISING = "fundraising"
    PARTNERSHIP = "partnership"
    AMMINISTRAZIONE = "amministrazione"
    MENTORING = "mentoring"
    RICERCA = "ricerca"


class VolontariatoTipo(str, enum.Enum):
    """Tipologie di volontariato"""
    CONTINUATIVO = "continuativo"     # Impegno regolare
    PROGETTUALE = "progettuale"       # Per progetti specifici
    OCCASIONALE = "occasionale"       # Eventi singoli
    STAGIONALE = "stagionale"         # Periodi specifici
    EMERGENZA = "emergenza"           # Supporto urgente
    MENTORING = "mentoring"           # Tutoraggio
    CONSULENZA = "consulenza"         # Expertise specifica


class VolontariatoModalita(str, enum.Enum):
    """Modalità di volontariato"""
    PRESENZA = "presenza"
    REMOTO = "remoto"
    IBRIDO = "ibrido"
    FLESSIBILE = "flessibile"


class VolontariatoLivello(str, enum.Enum):
    """Livello di esperienza richiesto"""
    PRINCIPIANTE = "principiante"
    INTERMEDIO = "intermedio"
    AVANZATO = "avanzato"
    ESPERTO = "esperto"
    QUALSIASI = "qualsiasi"


class VolontariatoUrgenza(str, enum.Enum):
    """Urgenza della richiesta"""
    BASSA = "bassa"           # Entro 1 mese
    MEDIA = "media"           # Entro 2 settimane
    ALTA = "alta"             # Entro 1 settimana
    URGENTE = "urgente"       # Entro 3 giorni
    IMMEDIATA = "immediata"   # Entro 24 ore


class VolontariatoStato(str, enum.Enum):
    """Stati dell'opportunità di volontariato"""
    BOZZA = "bozza"
    ATTIVA = "attiva"
    SOSPESA = "sospesa"
    COMPLETATA = "completata"
    ANNULLATA = "annullata"
    ARCHIVIATA = "archiviata"


class OpportunitaVolontariato(Base):
    """
    Modello per le opportunità di volontariato ISS
    Definisce le posizioni aperte per volontari
    """
    __tablename__ = "opportunita_volontariato"

    # Identificatori
    id = Column(Integer, primary_key=True, index=True)
    codice_opportunita = Column(String(20), unique=True, index=True, nullable=False)  # es: "ISS-VOL-2025-001"
    
    # Informazioni base
    titolo = Column(String(200), nullable=False, index=True)
    descrizione = Column(Text, nullable=False)
    descrizione_breve = Column(String(500), nullable=False)
    
    # Categorizzazione
    area = Column(Enum(VolontariatoArea), nullable=False, index=True)
    tipo = Column(Enum(VolontariatoTipo), nullable=False, index=True)
    modalita = Column(Enum(VolontariatoModalita), nullable=False, index=True)
    livello_richiesto = Column(Enum(VolontariatoLivello), nullable=False, index=True)
    urgenza = Column(Enum(VolontariatoUrgenza), default=VolontariatoUrgenza.MEDIA, nullable=False)
    stato = Column(Enum(VolontariatoStato), default=VolontariatoStato.BOZZA, nullable=False, index=True)
    
    # Dettagli posizione
    numero_volontari_richiesti = Column(Integer, default=1, nullable=False)
    numero_candidature = Column(Integer, default=0, nullable=False)
    numero_volontari_selezionati = Column(Integer, default=0, nullable=False)
    
    # Competenze e requisiti
    competenze_richieste = Column(Text, nullable=False)  # JSON array
    competenze_preferite = Column(Text, nullable=True)   # JSON array
    requisiti_minimi = Column(Text, nullable=True)
    requisiti_preferiti = Column(Text, nullable=True)
    
    # Impegno richiesto
    ore_settimanali_min = Column(Numeric(4, 2), nullable=True)
    ore_settimanali_max = Column(Numeric(4, 2), nullable=True)
    durata_mesi = Column(Integer, nullable=True)
    flessibilita_orari = Column(Boolean, default=True, nullable=False)
    
    # Timeline
    data_inizio_prevista = Column(DateTime, nullable=True, index=True)
    data_fine_prevista = Column(DateTime, nullable=True, index=True)
    data_scadenza_candidature = Column(DateTime, nullable=True, index=True)
    
    # Localizzazione
    sede_lavoro = Column(String(200), nullable=True)
    indirizzo = Column(String(300), nullable=True)
    citta = Column(String(100), nullable=True, default="Salerno")
    possibilita_remoto = Column(Boolean, default=True, nullable=False)
    
    # Progetto/Iniziativa collegata
    progetto_id = Column(Integer, ForeignKey("progetti.id"), nullable=True)
    evento_id = Column(Integer, ForeignKey("eventi.id"), nullable=True)
    corso_id = Column(Integer, ForeignKey("corsi.id"), nullable=True)
    
    # Benefici per il volontario
    benefici_offerti = Column(Text, nullable=True)  # JSON array
    formazione_fornita = Column(Text, nullable=True)
    certificazioni_ottenibili = Column(Text, nullable=True)
    rimborsi_spese = Column(Boolean, default=False, nullable=False)
    
    # Responsabile e contatti
    responsabile_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    contatto_email = Column(String(100), nullable=True)
    contatto_telefono = Column(String(20), nullable=True)
    
    # Processo di selezione
    processo_selezione = Column(Text, nullable=True)
    colloquio_richiesto = Column(Boolean, default=False, nullable=False)
    test_competenze = Column(Boolean, default=False, nullable=False)
    periodo_prova = Column(Boolean, default=False, nullable=False)
    
    # Accessibilità e inclusione
    accessibile_disabili = Column(Boolean, default=True, nullable=False)
    supporto_accessibilita = Column(Text, nullable=True)
    target_specifici = Column(Text, nullable=True)  # studenti, pensionati, disoccupati, etc.
    
    # Metadati
    creato_da_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    modificato_da_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # SEO e marketing
    slug = Column(String(250), unique=True, index=True, nullable=True)
    keywords = Column(String(500), nullable=True)
    
    # Flags
    in_evidenza = Column(Boolean, default=False, nullable=False)
    pubblicata = Column(Boolean, default=False, nullable=False)
    archiviata = Column(Boolean, default=False, nullable=False)
    candidature_aperte = Column(Boolean, default=True, nullable=False)

    # Relationships
    creato_da = relationship("User", foreign_keys=[creato_da_user_id])
    modificato_da = relationship("User", foreign_keys=[modificato_da_user_id])
    responsabile = relationship("User", foreign_keys=[responsabile_id])
    progetto = relationship("Progetto")
    evento = relationship("Evento")
    corso = relationship("Corso")
    candidature = relationship("VolontariatoCandidatura", back_populates="opportunita", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<OpportunitaVolontariato(id={self.id}, titolo='{self.titolo}')>"

    @property
    def posti_disponibili(self) -> int:
        """Calcola i posti ancora disponibili"""
        return max(0, self.numero_volontari_richiesti - self.numero_volontari_selezionati)

    @property
    def is_full(self) -> bool:
        """Verifica se tutti i posti sono stati coperti"""
        return self.numero_volontari_selezionati >= self.numero_volontari_richiesti

    @property
    def giorni_scadenza(self) -> Optional[int]:
        """Giorni rimanenti per candidarsi"""
        if not self.data_scadenza_candidature:
            return None
        delta = self.data_scadenza_candidature - datetime.now()
        return max(0, delta.days)


class VolontariatoCandidatura(Base):
    """Candidature per opportunità di volontariato"""
    __tablename__ = "volontariato_candidature"

    id = Column(Integer, primary_key=True, index=True)
    opportunita_id = Column(Integer, ForeignKey("opportunita_volontariato.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Stato candidatura
    stato = Column(String(20), default="inviata", nullable=False, index=True)
    # Stati: inviata, in_valutazione, colloquio, selezionata, rifiutata, ritirata
    
    # Motivazione e competenze
    lettera_motivazionale = Column(Text, nullable=False)
    competenze_dichiarate = Column(Text, nullable=True)  # JSON array
    esperienze_precedenti = Column(Text, nullable=True)
    
    # Disponibilità
    ore_settimanali_disponibili = Column(Numeric(4, 2), nullable=True)
    giorni_disponibili = Column(String(20), nullable=True)  # "lun,mer,ven"
    orari_preferiti = Column(String(100), nullable=True)
    data_inizio_disponibilita = Column(DateTime, nullable=True)
    
    # Preferenze
    modalita_preferita = Column(Enum(VolontariatoModalita), nullable=True)
    note_aggiuntive = Column(Text, nullable=True)
    
    # Processo di selezione
    data_candidatura = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    data_valutazione = Column(DateTime(timezone=True), nullable=True)
    data_colloquio = Column(DateTime(timezone=True), nullable=True)
    data_risposta = Column(DateTime(timezone=True), nullable=True)
    
    # Valutazione
    punteggio_competenze = Column(Numeric(3, 2), nullable=True)  # 0.00 - 5.00
    punteggio_motivazione = Column(Numeric(3, 2), nullable=True)  # 0.00 - 5.00
    punteggio_disponibilita = Column(Numeric(3, 2), nullable=True)  # 0.00 - 5.00
    punteggio_totale = Column(Numeric(3, 2), nullable=True)  # 0.00 - 5.00
    
    # Feedback
    feedback_candidato = Column(Text, nullable=True)
    feedback_organizzazione = Column(Text, nullable=True)
    motivo_rifiuto = Column(Text, nullable=True)
    
    # Documenti allegati
    cv_url = Column(String(500), nullable=True)
    portfolio_url = Column(String(500), nullable=True)
    certificazioni_url = Column(String(500), nullable=True)

    # Relationships
    opportunita = relationship("OpportunitaVolontariato")
    user = relationship("User")
    attivita = relationship("VolontariatoAttivita", back_populates="candidatura", cascade="all, delete-orphan")


class VolontariatoAttivita(Base):
    """Attività di volontariato svolte (time tracking)"""
    __tablename__ = "volontariato_attivita"

    id = Column(Integer, primary_key=True, index=True)
    candidatura_id = Column(Integer, ForeignKey("volontariato_candidature.id"), nullable=False)
    
    # Dettagli attività
    data_attivita = Column(DateTime, nullable=False, index=True)
    durata_ore = Column(Numeric(4, 2), nullable=False)
    descrizione_attivita = Column(Text, nullable=False)
    
    # Localizzazione
    modalita_svolta = Column(Enum(VolontariatoModalita), nullable=False)
    sede = Column(String(200), nullable=True)
    
    # Valutazione
    auto_valutazione = Column(Numeric(3, 2), nullable=True)  # 1.00 - 5.00
    valutazione_responsabile = Column(Numeric(3, 2), nullable=True)  # 1.00 - 5.00
    feedback_attivita = Column(Text, nullable=True)
    
    # Risultati
    obiettivi_raggiunti = Column(Text, nullable=True)
    difficolta_incontrate = Column(Text, nullable=True)
    suggerimenti = Column(Text, nullable=True)
    
    # Approvazione
    approvata = Column(Boolean, default=False, nullable=False)
    approvata_da_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    data_approvazione = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    candidatura = relationship("VolontariatoCandidatura")
    approvata_da = relationship("User")


class VolontariatoCertificato(Base):
    """Certificati di volontariato rilasciati"""
    __tablename__ = "volontariato_certificati"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Dettagli certificato
    codice_certificato = Column(String(50), unique=True, nullable=False)
    tipo_certificato = Column(String(100), nullable=False)  # partecipazione, competenze, leadership
    
    # Periodo di volontariato
    data_inizio = Column(DateTime, nullable=False)
    data_fine = Column(DateTime, nullable=False)
    ore_totali = Column(Numeric(6, 2), nullable=False)
    
    # Aree di volontariato
    aree_coinvolte = Column(Text, nullable=False)  # JSON array
    progetti_coinvolti = Column(Text, nullable=True)  # JSON array
    
    # Competenze sviluppate
    competenze_acquisite = Column(Text, nullable=True)  # JSON array
    risultati_raggiunti = Column(Text, nullable=True)
    
    # Valutazione finale
    valutazione_finale = Column(Numeric(3, 2), nullable=True)  # 1.00 - 5.00
    raccomandazione = Column(Text, nullable=True)
    
    # Metadati
    rilasciato_da_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    data_rilascio = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    url_certificato = Column(String(500), nullable=True)  # PDF del certificato
    
    # Verifica
    verificabile_online = Column(Boolean, default=True, nullable=False)
    codice_verifica = Column(String(100), unique=True, nullable=True)

    # Relationships
    volontario = relationship("User", foreign_keys=[user_id])
    rilasciato_da = relationship("User", foreign_keys=[rilasciato_da_id])


class VolontariatoSkill(Base):
    """Competenze dei volontari"""
    __tablename__ = "volontariato_skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Competenza
    nome_competenza = Column(String(100), nullable=False, index=True)
    categoria = Column(String(50), nullable=False, index=True)  # tecnica, soft, linguistica, etc.
    livello = Column(Enum(VolontariatoLivello), nullable=False)
    
    # Validazione
    auto_dichiarata = Column(Boolean, default=True, nullable=False)
    verificata = Column(Boolean, default=False, nullable=False)
    verificata_da_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    data_verifica = Column(DateTime(timezone=True), nullable=True)
    
    # Esperienza
    anni_esperienza = Column(Integer, nullable=True)
    progetti_utilizzata = Column(Text, nullable=True)  # JSON array
    
    # Disponibilità
    disponibile_per_formazione = Column(Boolean, default=True, nullable=False)
    disponibile_per_mentoring = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    volontario = relationship("User", foreign_keys=[user_id])
    verificata_da = relationship("User", foreign_keys=[verificata_da_id])
