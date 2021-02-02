import asyncio
import boto3
from decouple import config

LOCALSTACK_SQS_ENDPOINT_URL = config("LOCALSTACK_SQS_ENDPOINT_URL")
BOOKING_QUEUE_URL = config("BOOKING_QUEUE_URL")

sqs = boto3.client("sqs", endpoint_url=LOCALSTACK_SQS_ENDPOINT_URL)


def create_booking(booking):
    # @TODO implement db
    print(booking)


async def listen():
    while True:
        try:
            messages = sqs.receive_message(
                QueueUrl=BOOKING_QUEUE_URL, AttributeNames=['All'],
                MaxNumberOfMessages=10, WaitTimeSeconds=2, VisibilityTimeout=30
            )

            messages = messages.get("Messages", [])
            for message in messages:
                handler_id = message['ReceiptHandle']
                create_booking(message['Body'])
                sqs.delete_message(
                    QueueUrl=BOOKING_QUEUE_URL,
                    ReceiptHandle=handler_id
                )

            # print("Messages", messages)
        except Exception as e:
            print("SQS receive message failure: ", e)


loop = asyncio.get_event_loop()

try:
    asyncio.ensure_future(listen())
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    loop.close()
