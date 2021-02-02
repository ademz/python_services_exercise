import boto3
import json
import uuid

from decouple import config
from flask_api import FlaskAPI
from flask_restful import reqparse, Api, Resource


LOCALSTACK_SQS_ENDPOINT_URL = config("LOCALSTACK_SQS_ENDPOINT_URL")
BOOKING_QUEUE_URL = config("BOOKING_QUEUE_URL")

sqs = boto3.client("sqs", endpoint_url=LOCALSTACK_SQS_ENDPOINT_URL)

app = FlaskAPI(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('name')
parser.add_argument('time')


class Reservation(Resource):

    def post(self):
        args = parser.parse_args()
        message_id = str(uuid.uuid4())

        values = {}
        # @TODO implement form validation!
        values['name'] = args.get('name', '')
        values['time'] = args.get('time', '')
        values['message_id'] = message_id

        try:
            sqs.send_message(
                QueueUrl=BOOKING_QUEUE_URL,
                MessageBody=json.dumps(values),
                MessageDeduplicationId=message_id,
                MessageGroupId="messages",
                MessageAttributes={
                    "contentType": {
                        "StringValue": "application/json",
                        "DataType": "String"
                    }
                }
            )
        except Exception as e:
            print('message failed: ', e)

        return {'message': 'Your booking was added to the queue.'}


api.add_resource(Reservation, '/reservation')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
