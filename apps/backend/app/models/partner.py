"""
Modello Partner - Sistema Partnership ISS
Gestione partner, sponsor e collaborazioni strategiche
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum
from typing import Optional, List
from datetime import datetime


class PartnerTipo(str, enum.Enum):
    """Tipologie di partner"""
    ISTITUZIONALE = "istituzionale"      # Enti pubblici, istituzioni
    CORPORATE = "corporate"              # Aziende private
    NON_PROFIT = "non_profit"            # ONG, APS, Fondazioni
    ACCADEMICO = "accademico"            # Università, centri ricerca
    TECNOLOGICO = "tecnologico"          # Aziende tech, startup
    MEDIA = "media"                      # Giornali, TV, radio
    FINANZIARIO = "finanziario"          # Banche, fondi, investitori
    CONSULENZA = "consulenza"            # Studi professionali
    FORNITORE = "fornitore"              # Fornitori di servizi
    COMMUNITY = "community"              # Community, associazioni


class PartnerCategoria(str, enum.Enum):
    """Categorie di collaborazione"""
    STRATEGICO = "strategico"            # Partnership strategica
    OPERATIVO = "operativo"              # Collaborazione operativa
    FINANZIARIO = "finanziario"          # Supporto finanziario
    TECNOLOGICO = "tecnologico"          # Supporto tecnologico
    FORMATIVO = "formativo"              # Collaborazione formativa
    COMUNICAZIONE = "comunicazione"      # Supporto comunicazione
    RICERCA = "ricerca"                  # Collaborazione ricerca
    EVENTI = "eventi"                    # Partnership eventi
    MENTORING = "mentoring"              # Programmi mentoring
    ADVOCACY = "advocacy"                # Advocacy e policy


class PartnerLivello(str, enum.Enum):
    """Livelli di partnership"""
    PLATINUM = "platinum"                # Partner principale
    GOLD = "gold"                        # Partner importante
    SILVER = "silver"                    # Partner standard
    BRONZE = "bronze"                    # Partner base
    SUPPORTER = "supporter"              # Sostenitore
    COLLABORATOR = "collaborator"        # Collaboratore


class PartnerStato(str, enum.Enum):
    """Stati della partnership"""
    PROPOSTA = "proposta"                # Partnership proposta
    NEGOZIAZIONE = "negoziazione"        # In fase di negoziazione
    ATTIVA = "attiva"                    # Partnership attiva
    SOSPESA = "sospesa"                  # Temporaneamente sospesa
    CONCLUSA = "conclusa"                # Partnership conclusa
    ANNULLATA = "annullata"              # Partnership annullata


class PartnerSettore(str, enum.Enum):
    """Settori di attività"""
    TECNOLOGIA = "tecnologia"
    FINANZA = "finanza"
    SANITA = "sanita"
    EDUCAZIONE = "educazione"
    AMBIENTE = "ambiente"
    SOCIALE = "sociale"
    CULTURA = "cultura"
    TURISMO = "turismo"
    AGRICOLTURA = "agricoltura"
    MANIFATTURIERO = "manifatturiero"
    SERVIZI = "servizi"
    PUBBLICA_AMMINISTRAZIONE = "pubblica_amministrazione"
    RICERCA = "ricerca"
    MEDIA = "media"
    TRASPORTI = "trasporti"


class Partner(Base):
    """
    Modello per partner, sponsor e collaborazioni ISS
    Gestione completa delle partnership strategiche
    """
    __tablename__ = "partners"

    # Identificatori
    id = Column(Integer, primary_key=True, index=True)
    codice_partner = Column(String(20), unique=True, index=True, nullable=False)  # es: "ISS-PTR-2025-001"
    
    # Informazioni base organizzazione
    nome_organizzazione = Column(String(200), nullable=False, index=True)
    nome_breve = Column(String(100), nullable=True)  # Nome abbreviato
    descrizione = Column(Text, nullable=False)
    descrizione_breve = Column(String(500), nullable=False)
    
    # Categorizzazione
    tipo = Column(Enum(PartnerTipo), nullable=False, index=True)
    categoria = Column(Enum(PartnerCategoria), nullable=False, index=True)
    livello = Column(Enum(PartnerLivello), nullable=False, index=True)
    stato = Column(Enum(PartnerStato), default=PartnerStato.PROPOSTA, nullable=False, index=True)
    settore = Column(Enum(PartnerSettore), nullable=False, index=True)
    
    # Dati legali e fiscali
    ragione_sociale = Column(String(250), nullable=True)
    partita_iva = Column(String(20), nullable=True, index=True)
    codice_fiscale = Column(String(20), nullable=True, index=True)
    forma_giuridica = Column(String(100), nullable=True)  # SRL, SPA, APS, etc.
    
    # Contatti principali
    sito_web = Column(String(500), nullable=True)
    email_principale = Column(String(100), nullable=True)
    telefono_principale = Column(String(20), nullable=True)
    
    # Indirizzo sede legale
    indirizzo = Column(String(300), nullable=True)
    citta = Column(String(100), nullable=True)
    provincia = Column(String(50), nullable=True)
    cap = Column(String(5), nullable=True)
    regione = Column(String(50), nullable=True)
    paese = Column(String(50), default="Italia", nullable=False)
    
    # Dimensioni organizzazione
    numero_dipendenti = Column(Integer, nullable=True)
    fatturato_annuo = Column(Numeric(15, 2), nullable=True)
    anno_fondazione = Column(Integer, nullable=True)
    
    # Referenti partnership
    referente_principale_nome = Column(String(100), nullable=True)
    referente_principale_ruolo = Column(String(100), nullable=True)
    referente_principale_email = Column(String(100), nullable=True)
    referente_principale_telefono = Column(String(20), nullable=True)
    
    referente_secondario_nome = Column(String(100), nullable=True)
    referente_secondario_ruolo = Column(String(100), nullable=True)
    referente_secondario_email = Column(String(100), nullable=True)
    
    # Partnership details
    data_inizio_partnership = Column(DateTime, nullable=True, index=True)
    data_fine_partnership = Column(DateTime, nullable=True, index=True)
    durata_mesi = Column(Integer, nullable=True)
    rinnovabile = Column(Boolean, default=True, nullable=False)
    
    # Accordi e contratti
    contratto_firmato = Column(Boolean, default=False, nullable=False)
    data_firma_contratto = Column(DateTime, nullable=True)
    url_contratto = Column(String(500), nullable=True)
    nda_firmato = Column(Boolean, default=False, nullable=False)
    
    # Contributi e benefici
    contributo_finanziario = Column(Numeric(12, 2), nullable=True)
    contributo_in_kind = Column(Text, nullable=True)  # Contributi non monetari
    servizi_offerti = Column(Text, nullable=True)  # JSON array
    risorse_condivise = Column(Text, nullable=True)  # JSON array
    
    # Benefici per il partner
    benefici_ricevuti = Column(Text, nullable=True)  # JSON array
    visibilita_accordata = Column(Text, nullable=True)  # JSON array
    accesso_servizi = Column(Text, nullable=True)  # JSON array
    
    # Aree di collaborazione
    aree_collaborazione = Column(Text, nullable=False)  # JSON array
    progetti_congiunti = Column(Text, nullable=True)  # JSON array di project_id
    eventi_congiunti = Column(Text, nullable=True)  # JSON array di event_id
    
    # Obiettivi partnership
    obiettivi_partnership = Column(Text, nullable=False)
    kpi_partnership = Column(Text, nullable=True)  # JSON array di KPI
    risultati_attesi = Column(Text, nullable=True)
    
    # Valutazione e performance
    valutazione_partnership = Column(Numeric(3, 2), nullable=True)  # 1.00 - 5.00
    soddisfazione_iss = Column(Numeric(3, 2), nullable=True)  # 1.00 - 5.00
    soddisfazione_partner = Column(Numeric(3, 2), nullable=True)  # 1.00 - 5.00
    
    # Social media e comunicazione
    linkedin_url = Column(String(500), nullable=True)
    facebook_url = Column(String(500), nullable=True)
    twitter_url = Column(String(500), nullable=True)
    instagram_url = Column(String(500), nullable=True)
    
    # Logo e branding
    logo_url = Column(String(500), nullable=True)
    logo_alta_risoluzione = Column(String(500), nullable=True)
    colori_brand = Column(String(200), nullable=True)  # Hex colors
    guidelines_brand = Column(String(500), nullable=True)  # URL guidelines
    
    # Visibilità e marketing
    visibile_sito = Column(Boolean, default=True, nullable=False)
    visibile_materiali = Column(Boolean, default=True, nullable=False)
    menzione_comunicati = Column(Boolean, default=True, nullable=False)
    logo_eventi = Column(Boolean, default=True, nullable=False)
    
    # Comunicazione interna
    newsletter_partner = Column(Boolean, default=True, nullable=False)
    report_mensili = Column(Boolean, default=False, nullable=False)
    meeting_regolari = Column(Boolean, default=False, nullable=False)
    frequenza_meeting = Column(String(50), nullable=True)  # mensile, trimestrale, etc.
    
    # Compliance e certificazioni
    certificazioni = Column(Text, nullable=True)  # JSON array
    compliance_gdpr = Column(Boolean, default=False, nullable=False)
    compliance_iso = Column(Boolean, default=False, nullable=False)
    altre_compliance = Column(Text, nullable=True)
    
    # Sostenibilità e CSR
    politiche_sostenibilita = Column(Text, nullable=True)
    obiettivi_sdg = Column(Text, nullable=True)  # Sustainable Development Goals
    report_sostenibilita = Column(String(500), nullable=True)
    
    # Innovazione e R&D
    investimenti_rd = Column(Numeric(12, 2), nullable=True)
    brevetti = Column(Integer, nullable=True)
    pubblicazioni = Column(Integer, nullable=True)
    
    # Network e connessioni
    altri_partner_iss = Column(Text, nullable=True)  # JSON array
    network_esterno = Column(Text, nullable=True)  # Altri network del partner
    
    # Metadati
    creato_da_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    modificato_da_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # SEO e ricerca
    slug = Column(String(250), unique=True, index=True, nullable=True)
    keywords = Column(String(500), nullable=True)
    
    # Flags
    in_evidenza = Column(Boolean, default=False, nullable=False)
    partner_strategico = Column(Boolean, default=False, nullable=False)
    archiviato = Column(Boolean, default=False, nullable=False)

    # Relationships
    creato_da = relationship("User", foreign_keys=[creato_da_user_id])
    modificato_da = relationship("User", foreign_keys=[modificato_da_user_id])
    attivita = relationship("PartnerAttivita", back_populates="partner", cascade="all, delete-orphan")
    documenti = relationship("PartnerDocumento", back_populates="partner", cascade="all, delete-orphan")
    contatti = relationship("PartnerContatto", back_populates="partner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Partner(id={self.id}, nome='{self.nome_organizzazione}', livello='{self.livello}')>"

    @property
    def giorni_partnership(self) -> Optional[int]:
        """Giorni di durata della partnership"""
        if not self.data_inizio_partnership:
            return None
        end_date = self.data_fine_partnership or datetime.now()
        delta = end_date - self.data_inizio_partnership
        return delta.days

    @property
    def is_active(self) -> bool:
        """Verifica se la partnership è attiva"""
        return self.stato == PartnerStato.ATTIVA

    @property
    def giorni_scadenza(self) -> Optional[int]:
        """Giorni alla scadenza della partnership"""
        if not self.data_fine_partnership:
            return None
        delta = self.data_fine_partnership - datetime.now()
        return max(0, delta.days)


class PartnerContatto(Base):
    """Contatti del partner"""
    __tablename__ = "partner_contatti"

    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(Integer, ForeignKey("partners.id"), nullable=False)
    
    # Informazioni contatto
    nome = Column(String(100), nullable=False)
    cognome = Column(String(100), nullable=False)
    ruolo = Column(String(100), nullable=False)
    dipartimento = Column(String(100), nullable=True)
    
    # Contatti
    email = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=True)
    cellulare = Column(String(20), nullable=True)
    linkedin = Column(String(500), nullable=True)
    
    # Responsabilità
    aree_responsabilita = Column(Text, nullable=True)  # JSON array
    principale = Column(Boolean, default=False, nullable=False)
    
    # Stato
    attivo = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    partner = relationship("Partner")


class PartnerAttivita(Base):
    """Attività e interazioni con il partner"""
    __tablename__ = "partner_attivita"

    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(Integer, ForeignKey("partners.id"), nullable=False)
    
    # Tipo attività
    tipo_attivita = Column(String(50), nullable=False)  # meeting, evento, progetto, comunicazione
    titolo = Column(String(200), nullable=False)
    descrizione = Column(Text, nullable=False)
    
    # Timeline
    data_attivita = Column(DateTime, nullable=False, index=True)
    durata_ore = Column(Numeric(4, 2), nullable=True)
    
    # Partecipanti
    partecipanti_iss = Column(Text, nullable=True)  # JSON array
    partecipanti_partner = Column(Text, nullable=True)  # JSON array
    
    # Risultati
    risultati = Column(Text, nullable=True)
    azioni_follow_up = Column(Text, nullable=True)  # JSON array
    prossimi_passi = Column(Text, nullable=True)
    
    # Valutazione
    valutazione = Column(Numeric(3, 2), nullable=True)  # 1.00 - 5.00
    
    # Metadati
    creata_da_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    partner = relationship("Partner")
    creata_da = relationship("User")


class PartnerDocumento(Base):
    """Documenti della partnership"""
    __tablename__ = "partner_documenti"

    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(Integer, ForeignKey("partners.id"), nullable=False)
    
    # Informazioni documento
    nome_file = Column(String(255), nullable=False)
    tipo_documento = Column(String(50), nullable=False)  # contratto, nda, proposta, report
    categoria = Column(String(50), nullable=True)
    
    # File info
    url_file = Column(String(500), nullable=False)
    dimensione_bytes = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    
    # Descrizione
    descrizione = Column(Text, nullable=True)
    versione = Column(String(10), nullable=True)
    
    # Scadenze e validità
    data_scadenza = Column(DateTime, nullable=True)
    valido = Column(Boolean, default=True, nullable=False)
    
    # Accesso
    confidenziale = Column(Boolean, default=False, nullable=False)
    
    # Metadati
    caricato_da_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    partner = relationship("Partner")
    caricato_da = relationship("User")
