import json

import boto3

from listens.definitions import Listen
from listens.gateways.notification_gateway_abc import NotificationGateway as NotificationGatewayABC


class NotificationGateway(NotificationGatewayABC):
    client = boto3.client('sns')

    def __init__(self, listen_added_topic_arn: str) -> None:
        self.listen_added_topic_arn = listen_added_topic_arn

    def announce_listen_added(self, listen: Listen) -> None:
        payload = {'listen_id': listen.id}
        self.client.publish(
            TopicArn=self.listen_added_topic_arn,
            Message=json.dumps(payload)
        )
