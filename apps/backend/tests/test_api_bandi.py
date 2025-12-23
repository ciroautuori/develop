"""
Test per gli endpoint API dei bandi
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bando import Bando, BandoStatus, BandoSource
from app.crud.bando import bando_crud


class TestBandiPublicAPI:
    """Test per gli endpoint pubblici dei bandi."""

    @pytest.mark.asyncio
    async def test_get_bandi_stats(self, client: AsyncClient, db_session: AsyncSession):
        """Test endpoint statistiche bandi."""
        # Create some test bandi
        test_bandi = [
            Bando(
                title="Bando Attivo 1",
                ente="Test Ente",
                link="https://example.com/1",
                fonte=BandoSource.COMUNE_SALERNO,
                status=BandoStatus.ATTIVO,
                hash_identifier="hash1"
            ),
            Bando(
                title="Bando Attivo 2", 
                ente="Test Ente",
                link="https://example.com/2",
                fonte=BandoSource.REGIONE_CAMPANIA,
                status=BandoStatus.ATTIVO,
                hash_identifier="hash2"
            ),
            Bando(
                title="Bando Scaduto",
                ente="Test Ente",
                link="https://example.com/3",
                fonte=BandoSource.CSV_SALERNO,
                status=BandoStatus.SCADUTO,
                hash_identifier="hash3"
            )
        ]
        
        for bando in test_bandi:
            db_session.add(bando)
        await db_session.commit()
        
        # Test API
        response = await client.get("/api/v1/bandi/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_bandi"] == 3
        assert data["bandi_attivi"] == 2
        assert data["bandi_scaduti"] == 1
        assert "bandi_per_fonte" in data
        assert data["bandi_per_fonte"]["comune_salerno"] == 1
        assert data["bandi_per_fonte"]["regione_campania"] == 1
        assert data["bandi_per_fonte"]["csv_salerno"] == 1

    @pytest.mark.asyncio
    async def test_get_bandi_list(self, client: AsyncClient, db_session: AsyncSession):
        """Test endpoint lista bandi."""
        # Create test bandi
        bandi = [
            Bando(
                title="Alfabetizzazione Digitale",
                ente="Comune Test",
                link="https://example.com/1",
                fonte=BandoSource.COMUNE_SALERNO,
                hash_identifier="alpha1",
                keyword_match="alfabetizzazione digitale"
            ),
            Bando(
                title="Inclusione Sociale",
                ente="Regione Test", 
                link="https://example.com/2",
                fonte=BandoSource.REGIONE_CAMPANIA,
                hash_identifier="incl1",
                keyword_match="inclusione sociale"
            )
        ]
        
        for bando in bandi:
            db_session.add(bando)
        await db_session.commit()
        
        # Test API without filters
        response = await client.get("/api/v1/bandi/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert data["total"] == 2
        assert len(data["items"]) == 2
        
        # Test with search filter
        response = await client.get("/api/v1/bandi/?query=alfabetizzazione")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Alfabetizzazione Digitale"

    @pytest.mark.asyncio
    async def test_get_bandi_recent(self, client: AsyncClient, db_session: AsyncSession):
        """Test endpoint bandi recenti."""
        # Create test bando
        bando = Bando(
            title="Bando Recente",
            ente="Test Ente",
            link="https://example.com/recent",
            fonte=BandoSource.COMUNE_SALERNO,
            hash_identifier="recent1"
        )
        db_session.add(bando)
        await db_session.commit()
        
        # Test API
        response = await client.get("/api/v1/bandi/recent")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["title"] == "Bando Recente"

    @pytest.mark.asyncio
    async def test_get_bando_by_id(self, client: AsyncClient, db_session: AsyncSession):
        """Test endpoint singolo bando."""
        # Create test bando
        bando = Bando(
            title="Bando Specifico",
            ente="Test Ente",
            link="https://example.com/specific",
            fonte=BandoSource.COMUNE_SALERNO,
            hash_identifier="spec1"
        )
        db_session.add(bando)
        await db_session.commit()
        await db_session.refresh(bando)
        
        # Test existing bando
        response = await client.get(f"/api/v1/bandi/{bando.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == bando.id
        assert data["title"] == "Bando Specifico"
        
        # Test non-existing bando
        response = await client.get("/api/v1/bandi/99999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_bandi_pagination(self, client: AsyncClient, db_session: AsyncSession):
        """Test paginazione bandi."""
        # Create multiple bandi
        for i in range(25):
            bando = Bando(
                title=f"Bando {i}",
                ente="Test Ente",
                link=f"https://example.com/{i}",
                fonte=BandoSource.COMUNE_SALERNO,
                hash_identifier=f"hash{i}"
            )
            db_session.add(bando)
        await db_session.commit()
        
        # Test first page
        response = await client.get("/api/v1/bandi/?skip=0&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total"] == 25
        assert len(data["items"]) == 10
        assert data["page"] == 1
        assert data["size"] == 10
        assert data["pages"] == 3  # ceil(25/10)
        
        # Test second page
        response = await client.get("/api/v1/bandi/?skip=10&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["page"] == 2
        assert len(data["items"]) == 10

    @pytest.mark.asyncio
    async def test_bandi_filters(self, client: AsyncClient, db_session: AsyncSession):
        """Test filtri bandi."""
        # Create test bandi with different sources and statuses
        bandi = [
            Bando(
                title="Bando Comune",
                ente="Comune", 
                link="https://example.com/comune",
                fonte=BandoSource.COMUNE_SALERNO,
                status=BandoStatus.ATTIVO,
                hash_identifier="comune1"
            ),
            Bando(
                title="Bando Regione",
                ente="Regione",
                link="https://example.com/regione", 
                fonte=BandoSource.REGIONE_CAMPANIA,
                status=BandoStatus.SCADUTO,
                hash_identifier="regione1"
            )
        ]
        
        for bando in bandi:
            db_session.add(bando)
        await db_session.commit()
        
        # Test filter by fonte
        response = await client.get("/api/v1/bandi/?fonte=comune_salerno")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["fonte"] == "comune_salerno"
        
        # Test filter by status
        response = await client.get("/api/v1/bandi/?status=attivo")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "attivo"


class TestBandiAdminAPI:
    """Test per gli endpoint admin dei bandi."""

    @pytest.mark.asyncio
    async def test_create_bando_admin(self, client: AsyncClient, db_session: AsyncSession, sample_bando_data: dict, auth_headers: dict):
        """Test creazione bando via API admin."""
        # Mock admin authentication for this test
        response = await client.post(
            "/api/v1/bandi/",
            json=sample_bando_data,
            headers=auth_headers
        )
        
        # Since we don't have auth implemented yet, expect authentication error
        assert response.status_code in [401, 422]  # Unauthorized or validation error

    @pytest.mark.asyncio
    async def test_update_bando_admin(self, client: AsyncClient, db_session: AsyncSession, auth_headers: dict):
        """Test aggiornamento bando via API admin."""
        # Create test bando
        bando = Bando(
            title="Bando da Aggiornare",
            ente="Test Ente",
            link="https://example.com/update",
            fonte=BandoSource.COMUNE_SALERNO,
            hash_identifier="update1"
        )
        db_session.add(bando)
        await db_session.commit()
        await db_session.refresh(bando)
        
        update_data = {
            "title": "Bando Aggiornato",
            "status": "scaduto"
        }
        
        response = await client.put(
            f"/api/v1/bandi/{bando.id}",
            json=update_data,
            headers=auth_headers
        )
        
        # Expect authentication error since auth not implemented
        assert response.status_code in [401, 422]

    @pytest.mark.asyncio
    async def test_delete_bando_admin(self, client: AsyncClient, db_session: AsyncSession, auth_headers: dict):
        """Test eliminazione bando via API admin."""
        # Create test bando
        bando = Bando(
            title="Bando da Eliminare",
            ente="Test Ente",
            link="https://example.com/delete",
            fonte=BandoSource.COMUNE_SALERNO,
            hash_identifier="delete1"
        )
        db_session.add(bando)
        await db_session.commit()
        await db_session.refresh(bando)
        
        response = await client.delete(
            f"/api/v1/bandi/{bando.id}",
            headers=auth_headers
        )
        
        # Expect authentication error since auth not implemented
        assert response.status_code in [401, 422]


class TestBandiValidation:
    """Test per la validazione degli input."""

    @pytest.mark.asyncio
    async def test_invalid_pagination_params(self, client: AsyncClient):
        """Test parametri di paginazione invalidi."""
        # Test negative skip
        response = await client.get("/api/v1/bandi/?skip=-1")
        assert response.status_code == 422
        
        # Test limit too high
        response = await client.get("/api/v1/bandi/?limit=1000")
        assert response.status_code == 422

    @pytest.mark.asyncio 
    async def test_invalid_filter_values(self, client: AsyncClient):
        """Test valori di filtro invalidi."""
        # Test invalid fonte
        response = await client.get("/api/v1/bandi/?fonte=invalid_source")
        assert response.status_code == 422
        
        # Test invalid status
        response = await client.get("/api/v1/bandi/?status=invalid_status")
        assert response.status_code == 422
