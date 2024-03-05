import asyncio
import logging

from asyncua import Client, Node, ua

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('asyncua')

# mudar com o docker
url = 'opc.tcp://localhost:4840/freeopcua/server/'
namespace = 'http://examples.freeopcua.github.io'

class SubscriptionHandler:
    def datachange_notification(self, node: Node, val, data):
        logger.info(f'datachange_notification {node} {val}')

async def main():
    print(f'Connecting to {url}...')

    async with Client(url=url) as client:
        handler = SubscriptionHandler()

        subscription = await client.create_subscription(period=1000, handler=handler, publishing=False)

        namespace_idx = await client.get_namespace_index(namespace)
        print(f"Namespace index for '{namespace}': {namespace_idx}")

        var = await client.nodes.root.get_child(f"0:Objects/{namespace_idx}:MyObj/{namespace_idx}:MyVar")
        val = await var.read_value()
        print(f"Value of MyVar ({var}): {val}")

        nodes = [var, client.get_node(ua.ObjectIds.Server_ServerStatus_CurrentTime)]

        await subscription.subscribe_data_change(var)

        await asyncio.sleep(10)

        await subscription.delete()

        await asyncio.sleep(1)
        
        #new_val = val - 50
        #print(f"Setting val of MyVar to {new_val}...")
        #await var.write_value(new_val)
        #res = await client.nodes.objects.call_method(f"{namespace_idx}:ServerMethod", 5)
        #print(f"Calling ServerMethod returned {res}")

if __name__ == '__main__':
    asyncio.run(main())
