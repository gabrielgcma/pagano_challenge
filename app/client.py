import asyncio
import logging

import database
import threading

from asyncua import Client, Node, ua

from kafka import KafkaProducer, KafkaConsumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("asyncua")

kafka_topic = "opc-ua"
kafka_producer = KafkaProducer(bootstrap_servers=["kafka:9092"])


def on_send_success(record):
    logging.info("message sent")


# mudar com o docker?
opcua_server_url = "opc.tcp://opcua_server:4840/freeopcua/server/"
opcua_namespace = "http://examples.freeopcua.github.io"


class SubscriptionHandler:
    def datachange_notification(self, node: Node, val, data):
        logger.info(f"datachange_notification {node} {val}")
        kafka_producer.send(kafka_topic, str(val).encode()).add_callback(
            on_send_success
        )
        kafka_producer.flush()


values = []


async def kafka_consumer_task():
    kafka_consumer = KafkaConsumer(
        kafka_topic,
        bootstrap_servers=["kafka:9092"],
        auto_offset_reset="earliest",
        enable_auto_commit=False,
    )

    for msg in kafka_consumer:
        logging.info("got a message")
        database.create_msg(msg.value.decode("utf-8"))
        values.append(msg.value.decode("utf-8"))


async def write_to_txt_task():
    while True:
        with open("/home/data.txt", "a") as f:
            for val in values:
                try:
                    logging.info(f"writing {val}")
                    f.write(val + "\n")
                except Exception as e:
                    logging.error(e)
            values.clear()
        await asyncio.sleep(10)


async def opcua_client_task():
    print(f"Connecting to OPC-UA server {opcua_server_url}...")

    async with Client(url=opcua_server_url) as client:
        handler = SubscriptionHandler()

        subscription = await client.create_subscription(
            period=1000, handler=handler, publishing=False
        )

        namespace_idx = await client.get_namespace_index(opcua_namespace)
        print(f"Namespace index for '{opcua_namespace}': {namespace_idx}")

        var = await client.nodes.root.get_child(
            f"0:Objects/{namespace_idx}:MyObj/{namespace_idx}:MyVar"
        )
        val = await var.read_value()
        print(f"Value of MyVar ({var}): {val}")

        await subscription.subscribe_data_change(var)

        # await forever:
        await asyncio.Future()


# async def main():
# opcua_client = asyncio.create_task(opcua_client_task())
# kafka_consumer = asyncio.create_task(kafka_consumer_task())

# await asyncio.gather(opcua_client, kafka_consumer)

if __name__ == "__main__":
    print("entry point")
    # asyncio.run(main(), debug=True)

    opcua_thread = threading.Thread(target=asyncio.run, args=(opcua_client_task(),))
    kafka_consumer_thread = threading.Thread(
        target=asyncio.run, args=(kafka_consumer_task(),)
    )
    writer_thread = threading.Thread(target=asyncio.run, args=(write_to_txt_task(),))

    opcua_thread.start()
    kafka_consumer_thread.start()
    writer_thread.start()

    opcua_thread.join()
    kafka_consumer_thread.join()
    writer_thread.join()
