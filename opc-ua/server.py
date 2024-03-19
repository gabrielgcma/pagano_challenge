import asyncio
import logging
from asyncua import ua, Server
from asyncua.common.methods import uamethod

@uamethod
def func(parent, value):
    return value * 2

async def main():
    logger = logging.getLogger(__name__)

    server = Server()
    await server.init()
    server.set_endpoint('opc.tcp://0.0.0.0:4840/freeopcua/server/')

    namespace_uri = 'http://examples.freeopcua.github.io'
    idx = await server.register_namespace(namespace_uri)

    my_obj = await server.nodes.objects.add_object(idx, "MyObj")
    my_var = await my_obj.add_variable(idx, "MyVar", 6.7)

    await my_var.set_writable()
    await server.nodes.objects.add_method(
        ua.NodeId("ServerMethod", idx),
        ua.QualifiedName('ServerMethod', idx),
        func,
        [ua.VariantType.Int64],
        [ua.VariantType.Int64]
    )

    logger.info('Starting server...')

    async with server:
        while True:
            await asyncio.sleep(2)
            new_val = await my_var.get_value() + 0.1
            logger.info(f'Set value of {my_var} to {new_val}')
            await my_var.write_value(new_val)
            
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main(), debug=True)
