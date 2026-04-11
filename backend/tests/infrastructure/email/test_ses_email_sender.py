"""Tests for the SES email sender adapter."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.infrastructure.email.ses_email_sender import SESEmailSender


@pytest.fixture
def mock_ses_client() -> MagicMock:
    return MagicMock()


@pytest.fixture
def sender(mock_ses_client: MagicMock) -> SESEmailSender:
    with patch("app.infrastructure.email.ses_email_sender.boto3") as mock_boto3:
        mock_boto3.client.return_value = mock_ses_client
        ses = SESEmailSender(from_email="test@lpa.lv", region_name="eu-north-1")
    return ses


@pytest.mark.asyncio
async def test_send_plain_text(sender: SESEmailSender, mock_ses_client: MagicMock) -> None:
    await sender.send(to="user@example.com", subject="Hello", body="Test body")
    mock_ses_client.send_email.assert_called_once()
    call_kwargs = mock_ses_client.send_email.call_args[1]
    assert call_kwargs["Source"] == "test@lpa.lv"
    assert call_kwargs["Destination"] == {"ToAddresses": ["user@example.com"]}
    assert call_kwargs["Message"]["Subject"]["Data"] == "Hello"
    assert "Text" in call_kwargs["Message"]["Body"]
    assert "Html" not in call_kwargs["Message"]["Body"]


@pytest.mark.asyncio
async def test_send_with_html(sender: SESEmailSender, mock_ses_client: MagicMock) -> None:
    await sender.send(
        to="user@example.com", subject="Hello", body="Text", html_body="<p>HTML</p>"
    )
    call_kwargs = mock_ses_client.send_email.call_args[1]
    assert "Html" in call_kwargs["Message"]["Body"]
    assert call_kwargs["Message"]["Body"]["Html"]["Data"] == "<p>HTML</p>"


@pytest.mark.asyncio
async def test_boto3_error_propagates(sender: SESEmailSender, mock_ses_client: MagicMock) -> None:
    mock_ses_client.send_email.side_effect = Exception("SES error")
    with pytest.raises(Exception, match="SES error"):
        await sender.send(to="user@example.com", subject="Hello", body="body")
