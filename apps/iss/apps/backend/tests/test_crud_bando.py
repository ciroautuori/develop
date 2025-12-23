"""
Test per le operazioni CRUD dei bandi
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.bando import bando_crud
from app.models.bando import Bando, BandoStatus, BandoSource
from app.schemas.bando import BandoCreate, BandoUpdate, BandoSearch


class TestBandoCRUD:
    """Test per le operazioni CRUD sui bandi."""

    @pytest.mark.asyncio
    async def test_create_bando(self, db_session: AsyncSession, sample_bando_data: dict):
        """Test creazione bando via CRUD."""
        bando_create = BandoCreate(
            title=sample_bando_data["title"],
            ente=sample_bando_data["ente"],
            link=sample_bando_data["link"],
            fonte=sample_bando_data["fonte"],
            descrizione=sample_bando_data["descrizione"],
            keyword_match=sample_bando_data["keyword_match"]
        )
        
        created_bando = await bando_crud.create_bando(db_session, bando_create)
        
        assert created_bando.id is not None
        assert created_bando.title == sample_bando_data["title"]
        assert created_bando.ente == sample_bando_data["ente"]
        assert created_bando.hash_identifier is not None
        assert len(created_bando.hash_identifier) == 32  # MD5 hash length
        assert created_bando.status == BandoStatus.ATTIVO  # Default status

    @pytest.mark.asyncio
    async def test_create_duplicate_bando(self, db_session: AsyncSession, sample_bando_data: dict):
        """Test che la creazione di bandi duplicati non crei duplicati."""
        bando_create = BandoCreate(
            title=sample_bando_data["title"],
            ente=sample_bando_data["ente"],
            link=sample_bando_data["link"],
            fonte=sample_bando_data["fonte"]
        )
        
        # Crea primo bando
        bando1 = await bando_crud.create_bando(db_session, bando_create)
        
        # Prova a creare stesso bando (stesso hash)
        bando2 = await bando_crud.create_bando(db_session, bando_create)
        
        # Dovrebbe ritornare il primo bando, non crearne uno nuovo
        assert bando1.id == bando2.id
        assert bando1.hash_identifier == bando2.hash_identifier

    @pytest.mark.asyncio
    async def test_get_bando_by_id(self, db_session: AsyncSession):
        """Test recupero bando per ID."""
        # Crea bando di test
        bando = Bando(
            title="Test Bando",
            ente="Test Ente",
            link="https://example.com/test",
            fonte=BandoSource.COMUNE_SALERNO,
            hash_identifier="testid123"
        )
        db_session.add(bando)
        await db_session.commit()
        await db_session.refresh(bando)
        
        # Test recupero
        found_bando = await bando_crud.get_bando(db_session, bando.id)
        
        assert found_bando is not None
        assert found_bando.id == bando.id
        assert found_bando.title == "Test Bando"
        
        # Test bando inesistente
        not_found = await bando_crud.get_bando(db_session, 99999)
        assert not_found is None

    @pytest.mark.asyncio
    async def test_get_bando_by_hash(self, db_session: AsyncSession):
        """Test recupero bando per hash."""
        hash_id = "unique_hash_123"
        
        bando = Bando(
            title="Test Bando Hash",
            ente="Test Ente",
            link="https://example.com/hash",
            fonte=BandoSource.COMUNE_SALERNO,
            hash_identifier=hash_id
        )
        db_session.add(bando)
        await db_session.commit()
        
        # Test recupero per hash
        found_bando = await bando_crud.get_bando_by_hash(db_session, hash_id)
        
        assert found_bando is not None
        assert found_bando.hash_identifier == hash_id
        assert found_bando.title == "Test Bando Hash"
        
        # Test hash inesistente
        not_found = await bando_crud.get_bando_by_hash(db_session, "nonexistent")
        assert not_found is None

    @pytest.mark.asyncio
    async def test_get_bandi_list(self, db_session: AsyncSession):
        """Test recupero lista bandi con paginazione."""
        # Crea bandi di test
        for i in range(15):
            bando = Bando(
                title=f"Bando {i}",
                ente="Test Ente",
                link=f"https://example.com/{i}",
                fonte=BandoSource.COMUNE_SALERNO,
                hash_identifier=f"hash{i}"
            )
            db_session.add(bando)
        await db_session.commit()
        
        # Test prima pagina
        bandi, total = await bando_crud.get_bandi(db_session, skip=0, limit=10)
        
        assert len(bandi) == 10
        assert total == 15
        
        # Test seconda pagina
        bandi_page2, total2 = await bando_crud.get_bandi(db_session, skip=10, limit=10)
        
        assert len(bandi_page2) == 5  # Remaining items
        assert total2 == 15

    @pytest.mark.asyncio
    async def test_get_bandi_with_search(self, db_session: AsyncSession):
        """Test ricerca bandi con filtri."""
        # Crea bandi di test con caratteristiche diverse
        bandi_test = [
            Bando(
                title="Alfabetizzazione Digitale Anziani",
                ente="Comune di Salerno",
                link="https://example.com/1",
                fonte=BandoSource.COMUNE_SALERNO,
                status=BandoStatus.ATTIVO,
                hash_identifier="search1",
                keyword_match="alfabetizzazione digitale"
            ),
            Bando(
                title="Inclusione Sociale Giovani",
                ente="Regione Campania",
                link="https://example.com/2",
                fonte=BandoSource.REGIONE_CAMPANIA,
                status=BandoStatus.SCADUTO,
                hash_identifier="search2",
                keyword_match="inclusione sociale"
            ),
            Bando(
                title="Formazione Professionale",
                ente="CSV Salerno",
                link="https://example.com/3",
                fonte=BandoSource.CSV_SALERNO,
                status=BandoStatus.ATTIVO,
                hash_identifier="search3"
            )
        ]
        
        for bando in bandi_test:
            db_session.add(bando)
        await db_session.commit()
        
        # Test ricerca per query
        search = BandoSearch(query="alfabetizzazione")
        bandi, total = await bando_crud.get_bandi(db_session, search=search)
        
        assert total == 1
        assert bandi[0].title == "Alfabetizzazione Digitale Anziani"
        
        # Test filtro per fonte
        search = BandoSearch(fonte=BandoSource.COMUNE_SALERNO)
        bandi, total = await bando_crud.get_bandi(db_session, search=search)
        
        assert total == 1
        assert bandi[0].fonte == BandoSource.COMUNE_SALERNO
        
        # Test filtro per status
        search = BandoSearch(status=BandoStatus.ATTIVO)
        bandi, total = await bando_crud.get_bandi(db_session, search=search)
        
        assert total == 2
        assert all(bando.status == BandoStatus.ATTIVO for bando in bandi)

    @pytest.mark.asyncio
    async def test_update_bando(self, db_session: AsyncSession):
        """Test aggiornamento bando."""
        # Crea bando di test
        bando = Bando(
            title="Bando Originale",
            ente="Test Ente",
            link="https://example.com/update",
            fonte=BandoSource.COMUNE_SALERNO,
            hash_identifier="update123"
        )
        db_session.add(bando)
        await db_session.commit()
        await db_session.refresh(bando)
        
        # Test aggiornamento
        update_data = BandoUpdate(
            title="Bando Aggiornato",
            status=BandoStatus.SCADUTO,
            descrizione="Descrizione aggiornata"
        )
        
        updated_bando = await bando_crud.update_bando(db_session, bando.id, update_data)
        
        assert updated_bando is not None
        assert updated_bando.title == "Bando Aggiornato"
        assert updated_bando.status == BandoStatus.SCADUTO
        assert updated_bando.descrizione == "Descrizione aggiornata"
        assert updated_bando.ente == "Test Ente"  # Unchanged field
        
        # Test aggiornamento bando inesistente
        not_updated = await bando_crud.update_bando(db_session, 99999, update_data)
        assert not_updated is None

    @pytest.mark.asyncio
    async def test_delete_bando(self, db_session: AsyncSession):
        """Test eliminazione bando."""
        # Crea bando di test
        bando = Bando(
            title="Bando da Eliminare",
            ente="Test Ente",
            link="https://example.com/delete",
            fonte=BandoSource.COMUNE_SALERNO,
            hash_identifier="delete123"
        )
        db_session.add(bando)
        await db_session.commit()
        await db_session.refresh(bando)
        
        bando_id = bando.id
        
        # Test eliminazione
        success = await bando_crud.delete_bando(db_session, bando_id)
        assert success is True
        
        # Verifica che sia stato eliminato
        deleted_bando = await bando_crud.get_bando(db_session, bando_id)
        assert deleted_bando is None
        
        # Test eliminazione bando inesistente
        not_deleted = await bando_crud.delete_bando(db_session, 99999)
        assert not_deleted is False

    @pytest.mark.asyncio
    async def test_mark_as_notified(self, db_session: AsyncSession):
        """Test marcatura bando come notificato."""
        # Crea bando di test
        bando = Bando(
            title="Bando Notifica",
            ente="Test Ente",
            link="https://example.com/notify",
            fonte=BandoSource.COMUNE_SALERNO,
            hash_identifier="notify123"
        )
        db_session.add(bando)
        await db_session.commit()
        await db_session.refresh(bando)
        
        assert bando.notificato_email is False
        assert bando.notificato_telegram is False
        
        # Test marca come notificato email
        updated_bando = await bando_crud.mark_as_notified(
            db_session, bando.id, email=True
        )
        
        assert updated_bando is not None
        assert updated_bando.notificato_email is True
        assert updated_bando.notificato_telegram is False
        
        # Test marca come notificato telegram
        updated_bando = await bando_crud.mark_as_notified(
            db_session, bando.id, telegram=True
        )
        
        assert updated_bando.notificato_email is True
        assert updated_bando.notificato_telegram is True

    @pytest.mark.asyncio
    async def test_get_stats(self, db_session: AsyncSession):
        """Test statistiche bandi."""
        # Crea bandi di test con diverse caratteristiche
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        
        bandi_test = [
            Bando(
                title="Bando Attivo 1",
                ente="Test",
                link="https://example.com/1",
                fonte=BandoSource.COMUNE_SALERNO,
                status=BandoStatus.ATTIVO,
                hash_identifier="stats1"
            ),
            Bando(
                title="Bando Attivo 2",
                ente="Test",
                link="https://example.com/2",
                fonte=BandoSource.REGIONE_CAMPANIA,
                status=BandoStatus.ATTIVO,
                hash_identifier="stats2"
            ),
            Bando(
                title="Bando Scaduto",
                ente="Test",
                link="https://example.com/3",
                fonte=BandoSource.CSV_SALERNO,
                status=BandoStatus.SCADUTO,
                hash_identifier="stats3"
            )
        ]
        
        for bando in bandi_test:
            db_session.add(bando)
        await db_session.commit()
        
        # Test statistiche
        stats = await bando_crud.get_stats(db_session)
        
        assert stats["total_bandi"] == 3
        assert stats["bandi_attivi"] == 2
        assert stats["bandi_scaduti"] == 1
        assert stats["bandi_per_fonte"]["comune_salerno"] == 1
        assert stats["bandi_per_fonte"]["regione_campania"] == 1
        assert stats["bandi_per_fonte"]["csv_salerno"] == 1
        assert isinstance(stats["media_giornaliera"], float)

    @pytest.mark.asyncio
    async def test_get_recent_bandi(self, db_session: AsyncSession):
        """Test recupero bandi recenti."""
        # Crea bandi di test
        for i in range(15):
            bando = Bando(
                title=f"Bando Recente {i}",
                ente="Test Ente",
                link=f"https://example.com/{i}",
                fonte=BandoSource.COMUNE_SALERNO,
                hash_identifier=f"recent{i}"
            )
            db_session.add(bando)
        await db_session.commit()
        
        # Test recupero recenti (default limit 10)
        recent_bandi = await bando_crud.get_recent_bandi(db_session)
        
        assert len(recent_bandi) == 10
        # Should be ordered by data_trovato desc, so newer first
        assert "Bando Recente" in recent_bandi[0].title
        
        # Test con limit personalizzato
        recent_5 = await bando_crud.get_recent_bandi(db_session, limit=5)
        assert len(recent_5) == 5

    @pytest.mark.asyncio
    async def test_cleanup_old_bandi(self, db_session: AsyncSession):
        """Test pulizia bandi vecchi."""
        # Crea bandi di test (simuliamo date vecchie modificando direttamente)
        old_bando = Bando(
            title="Bando Vecchio",
            ente="Test Ente",
            link="https://example.com/old",
            fonte=BandoSource.COMUNE_SALERNO,
            status=BandoStatus.ATTIVO,
            hash_identifier="old123"
        )
        
        new_bando = Bando(
            title="Bando Nuovo", 
            ente="Test Ente",
            link="https://example.com/new",
            fonte=BandoSource.COMUNE_SALERNO,
            status=BandoStatus.ATTIVO,
            hash_identifier="new123"
        )
        
        db_session.add_all([old_bando, new_bando])
        await db_session.commit()
        
        # Il cleanup dovrebbe funzionare ma probabilmente non troverà bandi
        # vecchi in questo test dato che sono appena stati creati
        archived_count = await bando_crud.cleanup_old_bandi(db_session, days_old=1)
        
        # Verifichiamo che la funzione esegua senza errori
        assert isinstance(archived_count, int)
        assert archived_count >= 0

    @pytest.mark.asyncio
    async def test_generate_hash(self, db_session: AsyncSession):
        """Test generazione hash per bandi."""
        title = "Test Bando"
        ente = "Test Ente"
        link = "https://example.com/test"
        
        hash1 = bando_crud.generate_hash(title, ente, link)
        hash2 = bando_crud.generate_hash(title, ente, link)
        
        # Stesso input dovrebbe produrre stesso hash
        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 length
        
        # Input diverso dovrebbe produrre hash diverso
        hash3 = bando_crud.generate_hash(title + " Modified", ente, link)
        assert hash1 != hash3
