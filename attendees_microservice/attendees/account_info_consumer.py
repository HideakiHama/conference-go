from datetime import datetime
import json
import pika
from pika.exceptions import AMQPConnectionError
import django
import os
import sys
import time


sys.path.append("")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "attendees_bc.settings")
django.setup()
# boilerplate for django

from attendees.models import AccountVO  # noqa

# import AccountVO model after call to django.setup()


# Declare a function to update the AccountVO object (ch, method, properties, body)


def update_AccountVO(ch, method, properties, body):
    #   content = load the json in body
    #   first_name = content["first_name"]
    #   last_name = content["last_name"]
    #   email = content["email"]
    #   is_active = content["is_active"]
    #   updated_string = content["updated"]
    #   updated = convert updated_string from ISO string to datetime
    content = json.loads(body)
    print(content)
    # is_active = content["is_active"]
    # https://docs.djangoproject.com/en/4.1/topics/i18n/timezones/#naive-and-aware-datetime-objects
    content["updated"] = datetime.fromisoformat(content["updated"])
    if content["is_active"]:  # is the person active or no?
        AccountVO.objects.update_or_create(
            email=content["email"],  # checking for email (data to update)
            defaults=content,  # ID pram  (have to be dict) key email and val content # noqa
        )
    else:
        AccountVO.objects.filter(email=content["email"]).delete()
        # delete the inactive account!!!


#   if is_active:
#       Use the update_or_create method of the AccountVO.objects QuerySet
#           to update or create the AccountVO object
#   otherwise:
#       Delete the AccountVO object with the specified email, if it exists


# Based on the reference code at
#   https://github.com/rabbitmq/rabbitmq-tutorials/blob/master/python/receive_logs.py
# infinite loop
while True:
    try:
        #   try
        def main():
            #       create the pika connection parameters
            parameters = pika.ConnectionParameters(host="rabbitmq")
            #       create a blocking connection with the parameters
            connection = pika.BlockingConnection(parameters)
            #       open a channel
            channel = connection.channel()
            #       declare a fanout exchange named "account_info"

            channel.exchange_declare(
                exchange="account_info", exchange_type="fanout"
            )
            #       declare a randomly-named queue
            confq = channel.queue_declare(queue="", exclusive=True)
            # print(confq)
            #       get the queue name of the randomly-named queue
            queue_name = confq.method.queue
            #       bind the queue to the "account_info" exchange
            channel.queue_bind(exchange="account_info", queue=queue_name)
            #       do a basic_consume for the queue name that calls
            def callback(ch, method, properties, body):  # noqa
                print(" [x] %r" % body.decode())

            #           function above
            channel.basic_consume(
                queue=queue_name, on_message_callback=callback, auto_ack=True
            )
            #       tell the channel to start consuming
            channel.start_consuming()

        if __name__ == "__main__":
            try:
                main()
            except KeyboardInterrupt:
                print("Interrupted")
                try:
                    sys.exit(0)
                except SystemExit:
                    os._exit(0)

    #   except AMQPConnectionError
    except AMQPConnectionError:
        print("it could not connect to RabbitMQ")
        #       print that it could not connect to RabbitMQ
        time.sleep(5)
#       have it sleep for a couple of seconds
