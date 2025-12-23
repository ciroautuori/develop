"""
Unit tests for WhatsApp Cloud API Service.

Tests cover:
- Service configuration check
- Template message sending (mocked)
- Status tracking updates
- Phone number validation
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.domain.whatsapp.service import WhatsAppService, SendResult
from app.domain.whatsapp.schemas import (
    SendTemplateRequest,
    SendTextRequest,
    TemplateParameter,
    TemplateComponent
)
from app.domain.whatsapp.models import WhatsAppMessage, WhatsAppMessageStatus


class TestWhatsAppServiceConfiguration:
    """Test service configuration detection."""

    def test_is_configured_with_credentials(self):
        """Service should be configured when credentials are set."""
        with patch('app.domain.whatsapp.service.settings') as mock_settings:
            mock_settings.WHATSAPP_PHONE_NUMBER_ID = "123456789"
            mock_settings.WHATSAPP_ACCESS_TOKEN = "test_token"
            mock_settings.WHATSAPP_BUSINESS_ACCOUNT_ID = "biz123"
            mock_settings.WHATSAPP_API_VERSION = "v21.0"

            service = WhatsAppService()
            assert service.is_configured is True

    def test_is_not_configured_without_credentials(self):
        """Service should not be configured without credentials."""
        with patch('app.domain.whatsapp.service.settings') as mock_settings:
            mock_settings.WHATSAPP_PHONE_NUMBER_ID = ""
            mock_settings.WHATSAPP_ACCESS_TOKEN = ""
            mock_settings.WHATSAPP_BUSINESS_ACCOUNT_ID = ""
            mock_settings.WHATSAPP_API_VERSION = "v21.0"

            service = WhatsAppService()
            assert service.is_configured is False


class TestPhoneValidation:
    """Test phone number validation in schemas."""

    def test_valid_italian_phone_with_plus(self):
        """Valid Italian phone with + prefix."""
        request = SendTemplateRequest(
            phone="+393331234567",
            template_name="hello_world"
        )
        assert request.phone == "+393331234567"

    def test_valid_italian_phone_without_plus(self):
        """Phone without + should be normalized."""
        request = SendTemplateRequest(
            phone="393331234567",
            template_name="hello_world"
        )
        assert request.phone == "+393331234567"

    def test_valid_italian_phone_without_country_code(self):
        """Phone without country code should add +39."""
        request = SendTemplateRequest(
            phone="3331234567",
            template_name="hello_world"
        )
        assert request.phone == "+393331234567"

    def test_phone_with_spaces_and_dashes(self):
        """Phone with formatting should be cleaned."""
        request = SendTemplateRequest(
            phone="+39 333 123-4567",
            template_name="hello_world"
        )
        assert request.phone == "+393331234567"

    def test_invalid_phone_too_short(self):
        """Too short phone should raise error."""
        with pytest.raises(ValueError, match="Invalid phone number"):
            SendTemplateRequest(
                phone="+39123",
                template_name="hello_world"
            )


class TestSendTemplateMessage:
    """Test template message sending."""

    @pytest.mark.asyncio
    async def test_send_template_not_configured(self):
        """Should return error when not configured."""
        with patch('app.domain.whatsapp.service.settings') as mock_settings:
            mock_settings.WHATSAPP_PHONE_NUMBER_ID = ""
            mock_settings.WHATSAPP_ACCESS_TOKEN = ""
            mock_settings.WHATSAPP_BUSINESS_ACCOUNT_ID = ""
            mock_settings.WHATSAPP_API_VERSION = "v21.0"

            service = WhatsAppService()
            request = SendTemplateRequest(
                phone="+393331234567",
                template_name="hello_world"
            )

            result = await service.send_template_message(request)

            assert result.success is False
            assert "not configured" in result.error

    @pytest.mark.asyncio
    async def test_send_template_success(self):
        """Should return success on valid API response."""
        with patch('app.domain.whatsapp.service.settings') as mock_settings:
            mock_settings.WHATSAPP_PHONE_NUMBER_ID = "123456789"
            mock_settings.WHATSAPP_ACCESS_TOKEN = "test_token"
            mock_settings.WHATSAPP_BUSINESS_ACCOUNT_ID = "biz123"
            mock_settings.WHATSAPP_API_VERSION = "v21.0"

            service = WhatsAppService()

            # Mock the HTTP client
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "messages": [{"id": "wamid.abcd1234"}]
            }

            with patch.object(service, '_get_client') as mock_get_client:
                mock_client = AsyncMock()
                mock_client.post.return_value = mock_response
                mock_get_client.return_value = mock_client

                request = SendTemplateRequest(
                    phone="+393331234567",
                    template_name="hello_world",
                    language="it"
                )

                result = await service.send_template_message(request)

                assert result.success is True
                assert result.message_id == "wamid.abcd1234"
                assert result.phone == "+393331234567"

    @pytest.mark.asyncio
    async def test_send_template_api_error(self):
        """Should handle API error response."""
        with patch('app.domain.whatsapp.service.settings') as mock_settings:
            mock_settings.WHATSAPP_PHONE_NUMBER_ID = "123456789"
            mock_settings.WHATSAPP_ACCESS_TOKEN = "test_token"
            mock_settings.WHATSAPP_BUSINESS_ACCOUNT_ID = "biz123"
            mock_settings.WHATSAPP_API_VERSION = "v21.0"

            service = WhatsAppService()

            # Mock error response
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.json.return_value = {
                "error": {
                    "code": 100,
                    "message": "Invalid template"
                }
            }

            with patch.object(service, '_get_client') as mock_get_client:
                mock_client = AsyncMock()
                mock_client.post.return_value = mock_response
                mock_get_client.return_value = mock_client

                request = SendTemplateRequest(
                    phone="+393331234567",
                    template_name="invalid_template"
                )

                result = await service.send_template_message(request)

                assert result.success is False
                assert "Invalid template" in result.error


class TestStatusTracking:
    """Test message status updates."""

    def test_update_status_delivered(self):
        """Should update message status to delivered."""
        mock_db = MagicMock()
        mock_message = MagicMock()
        mock_message.status = WhatsAppMessageStatus.SENT.value
        mock_db.query.return_value.filter.return_value.first.return_value = mock_message

        service = WhatsAppService(db=mock_db)

        result = service.update_message_status(
            waba_message_id="wamid.test123",
            status="delivered",
            timestamp=datetime.utcnow()
        )

        assert result is True
        assert mock_message.status == WhatsAppMessageStatus.DELIVERED.value
        mock_db.commit.assert_called_once()

    def test_update_status_message_not_found(self):
        """Should return False when message not found."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        service = WhatsAppService(db=mock_db)

        result = service.update_message_status(
            waba_message_id="wamid.notexist",
            status="delivered"
        )

        assert result is False


class TestTemplateComponents:
    """Test template component building."""

    def test_template_with_parameters(self):
        """Should correctly build template with parameters."""
        components = [
            TemplateComponent(
                type="body",
                parameters=[
                    TemplateParameter(type="text", text="Mario Rossi"),
                    TemplateParameter(type="text", text="10:00")
                ]
            )
        ]

        request = SendTemplateRequest(
            phone="+393331234567",
            template_name="appointment_reminder",
            language="it",
            components=components
        )

        assert len(request.components) == 1
        assert len(request.components[0].parameters) == 2
        assert request.components[0].parameters[0].text == "Mario Rossi"
