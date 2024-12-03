import pika
import os
import ast
import logging

RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_PORT = int(os.environ.get('RABBITMQ_PORT', 5672))
RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'guest')
RABBITMQ_PASS = os.environ.get('RABBITMQ_PASS', 'guest')
INCOMING_QUEUE = 'filtered_messages'
OUTGOING_QUEUE = 'final_messages'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def callback(ch, method, properties, body):
    message = ast.literal_eval(body.decode())
    text = message.get('message', '')
    logger.info(f"Processing message: {text}")
    message['message'] = text.upper()
    logger.info(f"Converted message to uppercase: {message['message']}")
    publish_message(str(message))
    ch.basic_ack(delivery_tag=method.delivery_tag)

def publish_message(message):
    logger.info("Attempting to publish message")
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=OUTGOING_QUEUE, durable=False)
    channel.basic_publish(
        exchange='',
        routing_key=OUTGOING_QUEUE,
        body=message
    )
    logger.info(f"Successfully published message to {OUTGOING_QUEUE}")
    connection.close()

def consume_messages():
    logger.info("Starting message consumer")
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=INCOMING_QUEUE, durable=False)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=INCOMING_QUEUE, on_message_callback=callback)
    logger.info(f"Waiting for messages on queue {INCOMING_QUEUE}. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == '__main__':
    consume_messages()
