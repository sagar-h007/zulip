from zerver.lib.test_classes import ZulipTestCase
from zerver.models import Stream, Subscription
from zerver.actions.streams import do_change_subscription_property

class MandatoryEmailNotificationsTest(ZulipTestCase):
    def test_create_and_update_mandatory_notification_stream(self) -> None:
        user = self.example_user("iago")
        self.login_user(user)

        # Create a stream with mandatory email notifications
        stream_name = "Mandatory Stream"
        result = self.common_subscribe_to_streams(
            user,
            [stream_name],
            {"mandatory_email_notifications": True},
        )

        stream = Stream.objects.get(name=stream_name, realm=user.realm)
        self.assertTrue(stream.mandatory_email_notifications)

        # Update an existing stream to have mandatory email notifications
        stream_name_2 = "Normal Stream"
        self.common_subscribe_to_streams(user, [stream_name_2])
        stream_2 = Stream.objects.get(name=stream_name_2, realm=user.realm)
        self.assertFalse(stream_2.mandatory_email_notifications)

        result = self.client_patch(
            f"/json/streams/{stream_2.id}",
            {"mandatory_email_notifications": "true"}
        )
        self.assert_json_success(result)
        stream_2.refresh_from_db()
        self.assertTrue(stream_2.mandatory_email_notifications)

    def test_subscription_property_enforcement(self) -> None:
        user = self.example_user("hamlet")
        self.login_user(user)
        
        stream_name = "Mandatory Enforced"
        # Admin creates the stream
        admin = self.example_user("iago")
        self.login_user(admin)
        self.common_subscribe_to_streams(
            admin,
            [stream_name],
            {"mandatory_email_notifications": True},
        )
        
        # User subscribes
        self.login_user(user)
        self.subscribe(user, stream_name)
        stream = Stream.objects.get(name=stream_name, realm=user.realm)
        sub = Subscription.objects.get(user_profile=user, recipient__type=Subscription.STREAM, recipient__type_id=stream.id)
        
        # Try to disable email notifications via API
        result = self.client_post(
            "/json/users/me/subscriptions/properties",
            {"subscription_data": f'[{{"stream_id": {stream.id}, "property": "email_notifications", "value": false}}]'}
        )
        self.assert_json_error(result, "Email notifications are mandatory for this stream.")
        
        # Ensure it is still True in DB
        sub.refresh_from_db()
        self.assertTrue(sub.email_notifications)

