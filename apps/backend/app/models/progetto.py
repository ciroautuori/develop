"""
Modello Progetto - Sistema Progetti ISS
Progetti di innovazione sociale e iniziative della comunità ISS
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum
from typing import Optional, List
from datetime import datetime


class ProgettoStato(str, enum.Enum):
    """Stati del progetto"""
    IDEA = "idea"
    PIANIFICAZIONE = "pianificazione"
    APPROVATO = "approvato"
    IN_CORSO = "in_corso"
    SOSPESO = "sospeso"
    COMPLETATO = "completato"
    ARCHIVIATO = "archiviato"
    ANNULLATO = "annullato"


class ProgettoCategoria(str, enum.Enum):
    """Categorie dei progetti ISS"""
    INNOVAZIONE_SOCIALE = "innovazione_sociale"
    FORMAZIONE_DIGITALE = "formazione_digitale"
    INCLUSIONE_SOCIALE = "inclusione_sociale"
    SOSTENIBILITA = "sostenibilita"
    TERZO_SETTORE = "terzo_settore"
    TECNOLOGIA_SOCIALE = "tecnologia_sociale"
    ACCESSIBILITA = "accessibilita"
    VOLONTARIATO = "volontariato"
    RICERCA_SVILUPPO = "ricerca_sviluppo"
    PARTNERSHIP = "partnership"
    EVENTI_COMMUNITY = "eventi_community"
    ADVOCACY = "advocacy"


class ProgettoTipo(str, enum.Enum):
    """Tipologie di progetto"""
    INTERNO = "interno"           # Progetto interno ISS
    COLLABORATIVO = "collaborativo"  # Con partner esterni
    FINANZIATO = "finanziato"     # Con finanziamento esterno
    VOLONTARIATO = "volontariato" # Basato su volontari
    RICERCA = "ricerca"           # Progetto di ricerca
    PILOTA = "pilota"             # Progetto pilota/sperimentale
    CONTINUATIVO = "continuativo" # Progetto a lungo termine


class ProgettoVisibilita(str, enum.Enum):
    """Livelli di visibilità del progetto"""
    PUBBLICO = "pubblico"         # Visibile a tutti
    MEMBRI = "membri"             # Solo membri ISS
    TEAM = "team"                 # Solo team del progetto
    PRIVATO = "privato"           # Solo admin


class Progetto(Base):
    """
    Modello per i progetti ISS
    Progetti di innovazione sociale e iniziative della comunità
    """
    __tablename__ = "progetti"

    # Identificatori
    id = Column(Integer, primary_key=True, index=True)
    codice_progetto = Column(String(20), unique=True, index=True, nullable=False)  # es: "ISS-PRJ-2025-001"
    
    # Informazioni base
    nome = Column(String(200), nullable=False, index=True)
    tagline = Column(String(300), nullable=True)  # Slogan/sottotitolo
    descrizione = Column(Text, nullable=False)
    descrizione_breve = Column(String(500), nullable=False)
    
    # Categorizzazione
    categoria = Column(Enum(ProgettoCategoria), nullable=False, index=True)
    tipo = Column(Enum(ProgettoTipo), nullable=False, index=True)
    stato = Column(Enum(ProgettoStato), default=ProgettoStato.IDEA, nullable=False, index=True)
    visibilita = Column(Enum(ProgettoVisibilita), default=ProgettoVisibilita.PUBBLICO, nullable=False)
    
    # Obiettivi e impatto
    obiettivi = Column(Text, nullable=False)
    target_beneficiari = Column(Text, nullable=False)
    impatto_atteso = Column(Text, nullable=False)
    kpi_successo = Column(Text, nullable=True)  # JSON array di KPI
    
    # Timeline
    data_inizio = Column(DateTime, nullable=True, index=True)
    data_fine_prevista = Column(DateTime, nullable=True, index=True)
    data_fine_effettiva = Column(DateTime, nullable=True, index=True)
    durata_mesi = Column(Integer, nullable=True)
    
    # Milestone e fasi
    milestone = Column(Text, nullable=True)  # JSON array di milestone
    fase_attuale = Column(String(100), nullable=True)
    percentuale_completamento = Column(Numeric(5, 2), default=0.00, nullable=False)
    
    # Team e risorse umane
    project_manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    team_size = Column(Integer, default=1, nullable=False)
    volontari_necessari = Column(Integer, default=0, nullable=False)
    volontari_attuali = Column(Integer, default=0, nullable=False)
    competenze_richieste = Column(Text, nullable=True)  # JSON array
    
    # Budget e finanziamenti
    budget_totale = Column(Numeric(12, 2), nullable=True)
    budget_utilizzato = Column(Numeric(12, 2), default=0.00, nullable=False)
    fonti_finanziamento = Column(Text, nullable=True)  # JSON array
    bando_riferimento_id = Column(Integer, ForeignKey("bandi.id"), nullable=True)
    
    # Partnership e collaborazioni
    partner_principali = Column(Text, nullable=True)  # JSON array di partner
    sponsor = Column(Text, nullable=True)  # JSON array di sponsor
    enti_patrocinatori = Column(Text, nullable=True)  # JSON array
    
    # Localizzazione
    territorio_intervento = Column(String(200), nullable=True)
    citta = Column(String(100), nullable=True, default="Salerno")
    regione = Column(String(50), nullable=True, default="Campania")
    ambito_geografico = Column(String(50), nullable=True)  # locale, regionale, nazionale, internazionale
    
    # Metodologia e approccio
    metodologia = Column(Text, nullable=True)
    strumenti_utilizzati = Column(Text, nullable=True)  # JSON array
    tecnologie = Column(Text, nullable=True)  # JSON array
    
    # Risultati e deliverable
    deliverable = Column(Text, nullable=True)  # JSON array
    risultati_raggiunti = Column(Text, nullable=True)
    lezioni_apprese = Column(Text, nullable=True)
    
    # Comunicazione e disseminazione
    sito_web = Column(String(500), nullable=True)
    social_media = Column(Text, nullable=True)  # JSON object
    materiali_comunicazione = Column(Text, nullable=True)  # JSON array
    pubblicazioni = Column(Text, nullable=True)  # JSON array
    
    # Sostenibilità
    piano_sostenibilita = Column(Text, nullable=True)
    continuita_post_progetto = Column(Text, nullable=True)
    scalabilita = Column(Text, nullable=True)
    
    # Valutazione e monitoraggio
    sistema_monitoraggio = Column(Text, nullable=True)
    indicatori_impatto = Column(Text, nullable=True)  # JSON array
    valutazione_esterna = Column(Boolean, default=False, nullable=False)
    
    # Accessibilità e inclusione
    accessibile_disabili = Column(Boolean, default=True, nullable=False)
    inclusione_sociale = Column(Boolean, default=True, nullable=False)
    target_vulnerabili = Column(Text, nullable=True)
    
    # Innovazione
    elemento_innovativo = Column(Text, nullable=True)
    tecnologie_innovative = Column(Text, nullable=True)
    approccio_sperimentale = Column(Boolean, default=False, nullable=False)
    
    # Rischi e mitigazione
    rischi_identificati = Column(Text, nullable=True)  # JSON array
    strategie_mitigazione = Column(Text, nullable=True)  # JSON array
    
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
    cerca_volontari = Column(Boolean, default=False, nullable=False)
    open_source = Column(Boolean, default=False, nullable=False)

    # Relationships
    creato_da = relationship("User", foreign_keys=[creato_da_user_id])
    modificato_da = relationship("User", foreign_keys=[modificato_da_user_id])
    project_manager = relationship("User", foreign_keys=[project_manager_id])
    bando_riferimento = relationship("Bando")
    team_members = relationship("ProgettoTeamMember", back_populates="progetto", cascade="all, delete-orphan")
    aggiornamenti = relationship("ProgettoAggiornamento", back_populates="progetto", cascade="all, delete-orphan")
    documenti = relationship("ProgettoDocumento", back_populates="progetto", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Progetto(id={self.id}, codice='{self.codice_progetto}', nome='{self.nome}')>"

    @property
    def giorni_rimanenti(self) -> Optional[int]:
        """Calcola i giorni rimanenti alla scadenza"""
        if not self.data_fine_prevista:
            return None
        from datetime import datetime
        delta = self.data_fine_prevista - datetime.now()
        return max(0, delta.days)

    @property
    def is_in_ritardo(self) -> bool:
        """Verifica se il progetto è in ritardo"""
        if not self.data_fine_prevista:
            return False
        from datetime import datetime
        return datetime.now() > self.data_fine_prevista and self.stato != ProgettoStato.COMPLETATO

    @property
    def budget_rimanente(self) -> Optional[float]:
        """Calcola il budget rimanente"""
        if not self.budget_totale:
            return None
        return float(self.budget_totale - self.budget_utilizzato)

    @property
    def volontari_mancanti(self) -> int:
        """Calcola quanti volontari servono ancora"""
        return max(0, self.volontari_necessari - self.volontari_attuali)


class ProgettoTeamMember(Base):
    """Membri del team del progetto"""
    __tablename__ = "progetto_team_members"

    id = Column(Integer, primary_key=True, index=True)
    progetto_id = Column(Integer, ForeignKey("progetti.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Ruolo nel progetto
    ruolo = Column(String(100), nullable=False)  # project_manager, developer, designer, volontario, etc.
    responsabilita = Column(Text, nullable=True)
    competenze_apportate = Column(Text, nullable=True)
    
    # Partecipazione
    data_ingresso = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    data_uscita = Column(DateTime(timezone=True), nullable=True)
    attivo = Column(Boolean, default=True, nullable=False)
    
    # Impegno
    ore_settimanali = Column(Numeric(4, 2), nullable=True)
    tipo_impegno = Column(String(20), default="volontario", nullable=False)  # volontario, retribuito, stage
    
    # Valutazione
    performance_rating = Column(Numeric(3, 2), nullable=True)  # 0.00 - 5.00
    feedback = Column(Text, nullable=True)

    # Relationships
    progetto = relationship("Progetto")
    user = relationship("User")


class ProgettoAggiornamento(Base):
    """Aggiornamenti e progress report del progetto"""
    __tablename__ = "progetto_aggiornamenti"

    id = Column(Integer, primary_key=True, index=True)
    progetto_id = Column(Integer, ForeignKey("progetti.id"), nullable=False)
    
    # Contenuto aggiornamento
    titolo = Column(String(200), nullable=False)
    contenuto = Column(Text, nullable=False)
    tipo = Column(String(50), default="progress", nullable=False)  # progress, milestone, issue, news
    
    # Metriche
    percentuale_completamento = Column(Numeric(5, 2), nullable=True)
    budget_utilizzato = Column(Numeric(12, 2), nullable=True)
    milestone_raggiunte = Column(Text, nullable=True)  # JSON array
    
    # Problemi e soluzioni
    problemi_riscontrati = Column(Text, nullable=True)
    soluzioni_adottate = Column(Text, nullable=True)
    
    # Prossimi passi
    prossime_attivita = Column(Text, nullable=True)
    scadenze_imminenti = Column(Text, nullable=True)
    
    # Metadati
    autore_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    pubblico = Column(Boolean, default=True, nullable=False)

    # Relationships
    progetto = relationship("Progetto")
    autore = relationship("User")


class ProgettoDocumento(Base):
    """Documenti e file del progetto"""
    __tablename__ = "progetto_documenti"

    id = Column(Integer, primary_key=True, index=True)
    progetto_id = Column(Integer, ForeignKey("progetti.id"), nullable=False)
    
    # Informazioni documento
    nome_file = Column(String(255), nullable=False)
    nome_originale = Column(String(255), nullable=False)
    tipo_documento = Column(String(50), nullable=False)  # proposal, report, deliverable, contract, etc.
    categoria = Column(String(50), nullable=True)
    
    # File info
    url_file = Column(String(500), nullable=False)
    dimensione_bytes = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    
    # Descrizione
    descrizione = Column(Text, nullable=True)
    versione = Column(String(10), nullable=True)
    
    # Accesso
    pubblico = Column(Boolean, default=False, nullable=False)
    solo_team = Column(Boolean, default=True, nullable=False)
    
    # Metadati
    caricato_da_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    progetto = relationship("Progetto")
    caricato_da = relationship("User")
