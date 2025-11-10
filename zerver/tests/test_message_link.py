from zerver.models import Realm, Recipient, Message, Stream
from unittest.mock import patch
from zerver.lib.url_encoding import message_link_url
from zerver.lib.streams import create_stream_if_needed
from zerver.lib.test_classes import ZulipTestCase



class TestMessageLinkURL(ZulipTestCase):
    
    @patch("zerver.lib.url_encoding.pm_message_url", return_value="pm-url")
    @patch("zerver.lib.url_encoding.stream_message_url", return_value="stream-url")
    
    def test_message_link_url_dispatches_correct_function(self, mock_stream, mock_pm) -> None:
        realm = Realm.objects.create(string_id="zulip", name="Zulip Realm")
        stream = Stream.objects.create(name="general", realm=realm)
        recipient_stream = Recipient.objects.create(type=Recipient.STREAM, type_id=stream.id)
        message_stream = Message.objects.create(realm=realm, recipient=recipient_stream)

        # Testa mensagem de stream
        result_stream = message_link_url(realm, message_stream)
        mock_stream.assert_called_once_with(realm, message_stream)
        self.assertEqual(result_stream, "stream-url")

        # Testa mensagem privada
        recipient_pm = Recipient.objects.create(type=Recipient.PERSONAL, type_id=1)
        message_pm = Message.objects.create(realm=realm, recipient=recipient_pm)
        result_pm = message_link_url(realm, message_pm)
        mock_pm.assert_called_once_with(realm, message_pm)
        self.assertEqual(result_pm, "pm-url")