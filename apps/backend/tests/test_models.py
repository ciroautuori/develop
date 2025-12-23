"""
Test per i modelli del database
"""
import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.bando import Bando, BandoStatus, BandoSource
from app.models.bando_config import BandoConfig, BandoLog


class TestBandoModel:
    """Test per il modello Bando."""

    @pytest.mark.asyncio
    async def test_create_bando(self, db_session: AsyncSession, sample_bando_data: dict):
        """Test creazione di un bando."""
        # Create bando
        bando = Bando(
            title=sample_bando_data["title"],
            ente=sample_bando_data["ente"],
            link=sample_bando_data["link"],
            fonte=BandoSource.COMUNE_SALERNO,
            status=BandoStatus.ATTIVO,
            hash_identifier="test123",
            descrizione=sample_bando_data["descrizione"],
            keyword_match=sample_bando_data["keyword_match"]
        )
        
        db_session.add(bando)
        await db_session.commit()
        await db_session.refresh(bando)
        
        # Verify
        assert bando.id is not None
        assert bando.title == sample_bando_data["title"]
        assert bando.ente == sample_bando_data["ente"]
        assert bando.fonte == BandoSource.COMUNE_SALERNO
        assert bando.status == BandoStatus.ATTIVO
        assert bando.hash_identifier == "test123"
        assert bando.data_trovato is not None
        assert bando.notificato_email is False
        assert bando.notificato_telegram is False

    @pytest.mark.asyncio
    async def test_bando_unique_hash(self, db_session: AsyncSession):
        """Test che hash_identifier sia univoco."""
        # Create first bando
        bando1 = Bando(
            title="Bando 1",
            ente="Ente 1",
            link="http://example.com/1",
            fonte=BandoSource.COMUNE_SALERNO,
            hash_identifier="unique123"
        )
        db_session.add(bando1)
        await db_session.commit()
        
        # Try to create second bando with same hash
        bando2 = Bando(
            title="Bando 2",
            ente="Ente 2", 
            link="http://example.com/2",
            fonte=BandoSource.REGIONE_CAMPANIA,
            hash_identifier="unique123"  # Same hash
        )
        db_session.add(bando2)
        
        # Should raise constraint error
        with pytest.raises(Exception):  # SQLite will raise IntegrityError
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_bando_enum_values(self, db_session: AsyncSession):
        """Test che gli enum abbiano i valori corretti."""
        assert BandoStatus.ATTIVO.value == "attivo"
        assert BandoStatus.SCADUTO.value == "scaduto"
        assert BandoStatus.ARCHIVIATO.value == "archiviato"
        
        assert BandoSource.COMUNE_SALERNO.value == "comune_salerno"
        assert BandoSource.REGIONE_CAMPANIA.value == "regione_campania"
        assert BandoSource.CSV_SALERNO.value == "csv_salerno"

    @pytest.mark.asyncio
    async def test_query_bandi_by_status(self, db_session: AsyncSession):
        """Test query bandi per status."""
        # Create test bandi
        bando_attivo = Bando(
            title="Bando Attivo",
            ente="Test Ente",
            link="http://example.com/attivo",
            fonte=BandoSource.COMUNE_SALERNO,
            status=BandoStatus.ATTIVO,
            hash_identifier="attivo123"
        )
        
        bando_scaduto = Bando(
            title="Bando Scaduto",
            ente="Test Ente",
            link="http://example.com/scaduto",
            fonte=BandoSource.COMUNE_SALERNO,
            status=BandoStatus.SCADUTO,
            hash_identifier="scaduto123"
        )
        
        db_session.add_all([bando_attivo, bando_scaduto])
        await db_session.commit()
        
        # Query active bandi
        result = await db_session.execute(
            select(Bando).where(Bando.status == BandoStatus.ATTIVO)
        )
        active_bandi = result.scalars().all()
        
        assert len(active_bandi) == 1
        assert active_bandi[0].title == "Bando Attivo"
        assert active_bandi[0].status == BandoStatus.ATTIVO


class TestBandoConfigModel:
    """Test per il modello BandoConfig."""

    @pytest.mark.asyncio
    async def test_create_bando_config(self, db_session: AsyncSession, sample_config_data: dict):
        """Test creazione di una configurazione."""
        config = BandoConfig(
            name=sample_config_data["name"],
            email_enabled=sample_config_data["email_enabled"],
            email_username=sample_config_data["email_username"],
            email_recipient=sample_config_data["email_recipient"],
            keywords=sample_config_data["keywords"],
            fonte_enabled=sample_config_data["fonte_enabled"]
        )
        
        db_session.add(config)
        await db_session.commit()
        await db_session.refresh(config)
        
        # Verify
        assert config.id is not None
        assert config.name == sample_config_data["name"]
        assert config.email_enabled is True
        assert config.keywords == sample_config_data["keywords"]
        assert config.is_active is True  # Default value
        assert config.schedule_enabled is True  # Default value
        assert config.created_at is not None

    @pytest.mark.asyncio
    async def test_bando_config_unique_name(self, db_session: AsyncSession):
        """Test che il nome della configurazione sia univoco."""
        # Create first config
        config1 = BandoConfig(
            name="Unique Config",
            keywords=["test"],
            fonte_enabled={}
        )
        db_session.add(config1)
        await db_session.commit()
        
        # Try to create second config with same name
        config2 = BandoConfig(
            name="Unique Config",  # Same name
            keywords=["test2"],
            fonte_enabled={}
        )
        db_session.add(config2)
        
        # Should raise constraint error
        with pytest.raises(Exception):  # SQLite will raise IntegrityError
            await db_session.commit()


class TestBandoLogModel:
    """Test per il modello BandoLog."""

    @pytest.mark.asyncio
    async def test_create_bando_log(self, db_session: AsyncSession):
        """Test creazione di un log."""
        # First create a config
        config = BandoConfig(
            name="Test Config",
            keywords=["test"],
            fonte_enabled={}
        )
        db_session.add(config)
        await db_session.commit()
        await db_session.refresh(config)
        
        # Create log
        log = BandoLog(
            config_id=config.id,
            bandi_found=5,
            bandi_new=2,
            errors_count=0,
            status="completed",
            sources_processed={"comune_salerno": {"found": 3, "status": "success"}}
        )
        
        db_session.add(log)
        await db_session.commit()
        await db_session.refresh(log)
        
        # Verify
        assert log.id is not None
        assert log.config_id == config.id
        assert log.bandi_found == 5
        assert log.bandi_new == 2
        assert log.errors_count == 0
        assert log.status == "completed"
        assert log.started_at is not None
        assert log.sources_processed == {"comune_salerno": {"found": 3, "status": "success"}}

    @pytest.mark.asyncio
    async def test_query_logs_by_config(self, db_session: AsyncSession):
        """Test query log per configurazione."""
        # Create config
        config = BandoConfig(
            name="Test Config",
            keywords=["test"],
            fonte_enabled={}
        )
        db_session.add(config)
        await db_session.commit()
        await db_session.refresh(config)
        
        # Create multiple logs
        log1 = BandoLog(config_id=config.id, status="completed", bandi_found=3)
        log2 = BandoLog(config_id=config.id, status="running", bandi_found=0)
        log3 = BandoLog(config_id=999, status="completed", bandi_found=1)  # Different config
        
        db_session.add_all([log1, log2, log3])
        await db_session.commit()
        
        # Query logs for our config
        result = await db_session.execute(
            select(BandoLog).where(BandoLog.config_id == config.id)
        )
        config_logs = result.scalars().all()
        
        assert len(config_logs) == 2
        assert all(log.config_id == config.id for log in config_logs)
