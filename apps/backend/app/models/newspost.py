"""
Modello NewsPost - Sistema Blog e Notizie ISS
Gestione articoli, notizie e contenuti editoriali della piattaforma ISS
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum
from typing import Optional, List
from datetime import datetime


class NewsCategoria(str, enum.Enum):
    """Categorie degli articoli"""
    NOTIZIE = "notizie"
    EVENTI = "eventi"
    PROGETTI = "progetti"
    FORMAZIONE = "formazione"
    BANDI = "bandi"
    VOLONTARIATO = "volontariato"
    PARTNERSHIP = "partnership"
    INNOVAZIONE = "innovazione"
    ACCESSIBILITA = "accessibilita"
    COMMUNITY = "community"
    TUTORIAL = "tutorial"
    CASE_STUDY = "case_study"
    INTERVISTE = "interviste"
    COMUNICATI = "comunicati"


class NewsStato(str, enum.Enum):
    """Stati dell'articolo"""
    BOZZA = "bozza"
    IN_REVISIONE = "in_revisione"
    PROGRAMMATO = "programmato"
    PUBBLICATO = "pubblicato"
    ARCHIVIATO = "archiviato"
    RIMOSSO = "rimosso"


class NewsTipo(str, enum.Enum):
    """Tipologie di contenuto"""
    ARTICOLO = "articolo"
    NOTIZIA = "notizia"
    COMUNICATO = "comunicato"
    TUTORIAL = "tutorial"
    CASE_STUDY = "case_study"
    INTERVISTA = "intervista"
    RECENSIONE = "recensione"
    OPINIONE = "opinione"
    AGGIORNAMENTO = "aggiornamento"


class NewsPost(Base):
    """
    Modello per articoli, notizie e contenuti editoriali ISS
    Sistema completo di content management
    """
    __tablename__ = "news_posts"

    # Identificatori
    id = Column(Integer, primary_key=True, index=True)
    
    # Contenuto principale
    titolo = Column(String(200), nullable=False, index=True)
    sottotitolo = Column(String(300), nullable=True)
    sommario = Column(String(500), nullable=False)  # Abstract/riassunto
    contenuto = Column(Text, nullable=False)  # Contenuto completo (HTML/Markdown)
    
    # Categorizzazione
    categoria = Column(Enum(NewsCategoria), nullable=False, index=True)
    tipo = Column(Enum(NewsTipo), nullable=False, index=True)
    stato = Column(Enum(NewsStato), default=NewsStato.BOZZA, nullable=False, index=True)
    
    # Autore e redazione
    autore_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    co_autori = Column(Text, nullable=True)  # JSON array di user_id
    editore_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timeline pubblicazione
    data_creazione = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    data_modifica = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    data_pubblicazione = Column(DateTime(timezone=True), nullable=True, index=True)
    data_programmata = Column(DateTime(timezone=True), nullable=True, index=True)
    data_scadenza = Column(DateTime(timezone=True), nullable=True)  # Per contenuti temporanei
    
    # Media e immagini
    immagine_copertina = Column(String(500), nullable=True)
    immagine_copertina_alt = Column(String(200), nullable=True)  # Alt text per accessibilità
    galleria_immagini = Column(Text, nullable=True)  # JSON array di URL immagini
    video_url = Column(String(500), nullable=True)
    audio_url = Column(String(500), nullable=True)
    
    # SEO e metadata
    slug = Column(String(250), unique=True, index=True, nullable=False)
    meta_description = Column(String(160), nullable=True)
    meta_keywords = Column(String(500), nullable=True)
    canonical_url = Column(String(500), nullable=True)
    
    # Tagging e classificazione
    tags = Column(Text, nullable=True)  # JSON array di tag
    argomenti_correlati = Column(Text, nullable=True)  # JSON array
    
    # Engagement e statistiche
    visualizzazioni = Column(Integer, default=0, nullable=False)
    like_count = Column(Integer, default=0, nullable=False)
    share_count = Column(Integer, default=0, nullable=False)
    commenti_count = Column(Integer, default=0, nullable=False)
    
    # Contenuto correlato
    articoli_correlati = Column(Text, nullable=True)  # JSON array di post_id
    progetti_correlati = Column(Text, nullable=True)  # JSON array di project_id
    eventi_correlati = Column(Text, nullable=True)    # JSON array di event_id
    bandi_correlati = Column(Text, nullable=True)     # JSON array di bando_id
    
    # Impostazioni contenuto
    commenti_abilitati = Column(Boolean, default=True, nullable=False)
    condivisione_abilitata = Column(Boolean, default=True, nullable=False)
    newsletter_incluso = Column(Boolean, default=True, nullable=False)
    
    # Accessibilità
    trascrizione_audio = Column(Text, nullable=True)  # Per contenuti audio
    sottotitoli_video = Column(String(500), nullable=True)  # URL file sottotitoli
    versione_facile_lettura = Column(Text, nullable=True)  # Versione semplificata
    
    # Localizzazione
    lingua = Column(String(5), default="it", nullable=False)
    traduzioni_disponibili = Column(Text, nullable=True)  # JSON array di lingue
    
    # Social media
    facebook_post_id = Column(String(100), nullable=True)
    twitter_post_id = Column(String(100), nullable=True)
    linkedin_post_id = Column(String(100), nullable=True)
    instagram_post_id = Column(String(100), nullable=True)
    
    # Priorità e visibilità
    priorita = Column(Integer, default=0, nullable=False)  # 0=normale, 1=alta, 2=urgente
    in_evidenza = Column(Boolean, default=False, nullable=False)
    homepage_featured = Column(Boolean, default=False, nullable=False)
    newsletter_featured = Column(Boolean, default=False, nullable=False)
    
    # Workflow editoriale
    note_redazione = Column(Text, nullable=True)
    revisioni_richieste = Column(Text, nullable=True)
    approvato_da_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    data_approvazione = Column(DateTime(timezone=True), nullable=True)
    
    # Archiviazione
    archiviato = Column(Boolean, default=False, nullable=False)
    motivo_archiviazione = Column(String(200), nullable=True)
    
    # Metriche avanzate
    tempo_lettura_minuti = Column(Integer, nullable=True)  # Tempo stimato di lettura
    engagement_rate = Column(Numeric(5, 4), nullable=True)  # Tasso di engagement
    bounce_rate = Column(Numeric(5, 4), nullable=True)      # Tasso di rimbalzo
    
    # Flags speciali
    breaking_news = Column(Boolean, default=False, nullable=False)  # Notizia urgente
    evergreen = Column(Boolean, default=False, nullable=False)      # Contenuto sempre attuale
    sponsored = Column(Boolean, default=False, nullable=False)      # Contenuto sponsorizzato

    # Relationships
    autore = relationship("User", foreign_keys=[autore_id])
    editore = relationship("User", foreign_keys=[editore_id])
    approvato_da = relationship("User", foreign_keys=[approvato_da_id])
    commenti = relationship("NewsCommento", back_populates="post", cascade="all, delete-orphan")
    like = relationship("NewsLike", back_populates="post", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<NewsPost(id={self.id}, titolo='{self.titolo}', stato='{self.stato}')>"

    @property
    def is_published(self) -> bool:
        """Verifica se l'articolo è pubblicato"""
        return self.stato == NewsStato.PUBBLICATO and self.data_pubblicazione is not None

    @property
    def is_scheduled(self) -> bool:
        """Verifica se l'articolo è programmato"""
        return self.stato == NewsStato.PROGRAMMATO and self.data_programmata is not None

    @property
    def giorni_dalla_pubblicazione(self) -> Optional[int]:
        """Giorni trascorsi dalla pubblicazione"""
        if not self.data_pubblicazione:
            return None
        delta = datetime.now() - self.data_pubblicazione
        return delta.days

    @property
    def engagement_score(self) -> float:
        """Calcola un punteggio di engagement"""
        if self.visualizzazioni == 0:
            return 0.0
        interactions = self.like_count + self.share_count + self.commenti_count
        return (interactions / self.visualizzazioni) * 100


class NewsCommento(Base):
    """Commenti agli articoli"""
    __tablename__ = "news_commenti"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("news_posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Contenuto commento
    contenuto = Column(Text, nullable=False)
    
    # Thread/Reply system
    parent_id = Column(Integer, ForeignKey("news_commenti.id"), nullable=True)  # Per risposte
    livello = Column(Integer, default=0, nullable=False)  # Livello di nesting
    
    # Moderazione
    approvato = Column(Boolean, default=True, nullable=False)
    moderato_da_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    motivo_moderazione = Column(String(200), nullable=True)
    
    # Engagement
    like_count = Column(Integer, default=0, nullable=False)
    dislike_count = Column(Integer, default=0, nullable=False)
    
    # Metadati
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Flags
    segnalato = Column(Boolean, default=False, nullable=False)
    numero_segnalazioni = Column(Integer, default=0, nullable=False)

    # Relationships
    post = relationship("NewsPost")
    user = relationship("User", foreign_keys=[user_id])
    moderato_da = relationship("User", foreign_keys=[moderato_da_id])
    parent = relationship("NewsCommento", remote_side=[id], foreign_keys=[parent_id])
    risposte = relationship("NewsCommento", back_populates="parent", foreign_keys=[parent_id], cascade="all, delete-orphan")


class NewsLike(Base):
    """Like agli articoli"""
    __tablename__ = "news_likes"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("news_posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Unique constraint per evitare like multipli
    __table_args__ = (
        {"extend_existing": True}
    )

    # Relationships
    post = relationship("NewsPost")
    user = relationship("User")


class NewsNewsletter(Base):
    """Newsletter e digest automatici"""
    __tablename__ = "news_newsletters"

    id = Column(Integer, primary_key=True, index=True)
    
    # Informazioni newsletter
    titolo = Column(String(200), nullable=False)
    descrizione = Column(Text, nullable=True)
    tipo = Column(String(50), default="settimanale", nullable=False)  # giornaliera, settimanale, mensile
    
    # Contenuto
    articoli_inclusi = Column(Text, nullable=False)  # JSON array di post_id
    template_html = Column(Text, nullable=False)
    template_text = Column(Text, nullable=False)
    
    # Programmazione
    data_invio_programmata = Column(DateTime(timezone=True), nullable=False)
    data_invio_effettiva = Column(DateTime(timezone=True), nullable=True)
    
    # Statistiche invio
    destinatari_totali = Column(Integer, default=0, nullable=False)
    invii_riusciti = Column(Integer, default=0, nullable=False)
    invii_falliti = Column(Integer, default=0, nullable=False)
    aperture = Column(Integer, default=0, nullable=False)
    click = Column(Integer, default=0, nullable=False)
    
    # Stato
    stato = Column(String(20), default="programmata", nullable=False)  # programmata, inviata, fallita
    
    # Metadati
    creata_da_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    creata_da = relationship("User")


class NewsCategoriaSottoscrizione(Base):
    """Sottoscrizioni degli utenti alle categorie di notizie"""
    __tablename__ = "news_categoria_sottoscrizioni"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    categoria = Column(Enum(NewsCategoria), nullable=False)
    
    # Preferenze notifica
    email_abilitata = Column(Boolean, default=True, nullable=False)
    push_abilitata = Column(Boolean, default=False, nullable=False)
    frequenza = Column(String(20), default="immediata", nullable=False)  # immediata, giornaliera, settimanale
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Unique constraint
    __table_args__ = (
        {"extend_existing": True}
    )

    # Relationships
    user = relationship("User")
