
import json
import boto3
from web_socket_api.communication.abstractions.communication import ISubscriber

class SQSSubscriber(ISubscriber):
    def __init__(self, session: boto3.Session) -> None:
        self._sqs = session.client("sqs", region_name="us-east-1")

   
    def subscribe(self, to: str):
        while True:
            try:
                response = self._sqs.receive_message(
                    QueueUrl=to,
                    AttributeNames=["All"],
                    MaxNumberOfMessages=1,
                    MessageAttributeNames=["All"],
                    VisibilityTimeout=0,
                    WaitTimeSeconds=20,
                )

                messages = response.get("Messages", [])
                if not messages:
                    continue

                for message in messages:
                    body = json.loads(message['Body'])
                    body["attempts"] = message["Attributes"]["ApproximateReceiveCount"]
                    body["message_id"] = message['MessageId']
                    yield body

                    self._sqs.delete_message(
                        QueueUrl=to, ReceiptHandle=message["ReceiptHandle"]
                    )

            except Exception as e:
                raise Exception("Failed to receive message", e)
