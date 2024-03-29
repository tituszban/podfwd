from mock import patch, MagicMock, Mock
from email_exporter.individual.run import export_inbox
from email_exporter.inbox import InboxProcessor
from email_exporter.email_exporter import EmailExporter


def test_export_inbox():
    mock_inbox = Mock()
    mock_email_exporter = Mock()

    def side_effect(t):
        if t == InboxProcessor:
            return mock_inbox
        if t == EmailExporter:
            return mock_email_exporter
        raise KeyError()

    deps = Mock()
    deps.get = MagicMock(side_effect=side_effect)

    with patch("email_exporter.individual.run.Dependencies.default", MagicMock(return_value=deps)):
        export_inbox()

    mock_inbox.process_inbox.assert_called_once()
    mock_email_exporter.apply_feeds.assert_called_once()
