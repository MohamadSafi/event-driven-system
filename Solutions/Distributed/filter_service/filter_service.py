import pika
import os
import ast
import logging

RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_PORT = int(os.environ.get('RABBITMQ_PORT', 5672))
RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'guest')
RABBITMQ_PASS = os.environ.get('RABBITMQ_PASS', 'guest')
INCOMING_QUEUE = 'incoming_messages'
OUTGOING_QUEUE = 'filtered_messages'
STOP_WORDS = {'bird-watching', 'ailurophobia', 'mango'}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def callback(ch, method, properties, body):
    message = ast.literal_eval(body.decode())
    text = message.get('message', '')
    if any(stop_word in text for stop_word in STOP_WORDS):
        logger.info(f"Message discarded due to stop-word: {text}")
    else:
        logger.info(f"Processing message: {text}")
        publish_message(str(message))
    ch.basic_ack(delivery_tag=method.delivery_tag)

def publish_message(message):
    import time
    max_retries = 5
    retry_delay = 5
    
    for retry in range(max_retries):
        try:
            logger.info(f"Attempting to connect to RabbitMQ (attempt {retry + 1}/{max_retries})")
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    port=RABBITMQ_PORT,
                    credentials=credentials
                )
            )
            logger.info("Successfully connected to RabbitMQ")
            break
        except pika.exceptions.AMQPConnectionError:
            if retry < max_retries - 1:
                logger.warning(f"Failed to connect, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Failed to connect to RabbitMQ after multiple retries")
                raise Exception("Failed to connect to RabbitMQ after multiple retries")
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
    import time
    max_retries = 5
    retry_delay = 5
    
    for retry in range(max_retries):
        try:
            logger.info(f"Attempting to connect to RabbitMQ (attempt {retry + 1}/{max_retries})")
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    port=RABBITMQ_PORT,
                    credentials=credentials
                )
            )
            logger.info("Successfully connected to RabbitMQ")
            break
        except pika.exceptions.AMQPConnectionError:
            if retry < max_retries - 1:
                logger.warning(f"Failed to connect, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Failed to connect to RabbitMQ after multiple retries")
                raise Exception("Failed to connect to RabbitMQ after multiple retries")
    channel = connection.channel()
    channel.queue_declare(queue=INCOMING_QUEUE, durable=False)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=INCOMING_QUEUE, on_message_callback=callback)
    logger.info('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    consume_messages()
