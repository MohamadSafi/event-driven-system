import pika
import os
import ast
import smtplib
import logging
from email.mime.text import MIMEText

RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_PORT = int(os.environ.get('RABBITMQ_PORT', 5672))
RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'guest')
RABBITMQ_PASS = os.environ.get('RABBITMQ_PASS', 'guest')
INCOMING_QUEUE = 'final_messages'

SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.example.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER', 'your_email@example.com')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', 'your_password')
RECIPIENTS = os.environ.get('RECIPIENTS', 'recipient1@example.com,recipient2@example.com').split(',')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def send_email(alias, message_text):
    msg = MIMEText(f"From user: {alias}\nMessage: {message_text}")
    msg['Subject'] = 'New Message'
    msg['From'] = SMTP_USER
    msg['To'] = ', '.join(RECIPIENTS)

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        logger.info(f"Connecting to SMTP server {SMTP_SERVER}:{SMTP_PORT}")
        server.login(SMTP_USER, SMTP_PASSWORD)
        logger.info(f"Sending email to {RECIPIENTS}")
        server.sendmail(SMTP_USER, RECIPIENTS, msg.as_string())
        logger.info("Email sent successfully")

def callback(ch, method, properties, body):
    message = ast.literal_eval(body.decode())
    alias = message.get('alias', '')
    text = message.get('message', '')
    try:
        logger.info(f"Processing message from {alias}")
        send_email(alias, text)
        logger.info(f"Successfully processed message: {text}")
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}", exc_info=True)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def consume_messages():
    import time
    max_retries = 5
    retry_delay = 5  # seconds
    
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
