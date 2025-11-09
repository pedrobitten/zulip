# zerver/tests/test_message_links.py

from unittest.mock import patch
from zerver.lib.test_classes import ZulipTestCase
from zerver.models import Realm, Recipient, Message, UserProfile, Stream
from zerver.lib.url_encoding import pm_message_url, message_link_url

class TestMessageURL(ZulipTestCase):

    def test_pm_message_url_single_user(self) -> None:
        realm = Realm.objects.create(string_id="zulip", name="Zulip Realm")
        sender = UserProfile.objects.create(
            full_name="Alice",
            email="alice@example.com",
            realm=realm,
        )

        # Recipient do tipo PERSONAL (mensagem direta)
        recipient = Recipient.objects.create(type=Recipient.PERSONAL, type_id=sender.id)

        message = Message.objects.create(
            realm=realm,
            sender=sender,
            recipient=recipient,
            content="Hi Bob!"
        )

        url = pm_message_url(realm, message)
        self.assertIn(f"#narrow/dm/{sender.id}", url)
        self.assertIn(str(message.id), url)
        

    def test_pm_message_url_huddle_group(self) -> None:
           
        realm = Realm.objects.create(string_id="zulip", name="Zulip Realm")
        user1 = UserProfile.objects.create(full_name="User1", email="u1@example.com", realm=realm)
        user2 = UserProfile.objects.create(full_name="User2", email="u2@example.com", realm=realm)
        user3 = UserProfile.objects.create(full_name="User3", email="u3@example.com", realm=realm)

        # Cria recipient do tipo HUDDLE (grupo)
        recipient = Recipient.objects.create(type=Recipient.HUDDLE, type_id=999)

        message = Message.objects.create(
            realm=realm,
            sender=user1,
            recipient=recipient,
            content="Group hello!"
        )

        url = pm_message_url(realm, message)
        self.assertIn("#narrow/dm/", url)
        self.assertIn(str(message.id), url)

        

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