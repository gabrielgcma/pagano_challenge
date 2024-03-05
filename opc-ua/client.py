import asyncio

from asyncua import Client

url = 'opc.tcp://localhost:4840/freeopcua/server/'
namespace = 'http://examples.freeopcua.github.io'

async def main():
    print(f'Connecting to {url}...')

    async with Client(url=url) as client:
        namespace_idx = await client.get_namespace_index(namespace)
        print(f"Namespace index for '{namespace}': {namespace_idx}")

        var = await client.nodes.root.get_child(f"0:Objects/{namespace_idx}:MyObj/{namespace_idx}:MyVar")
        val = await var.read_value()
        print(f"Value of MyVar ({var}): {val}")

        new_val = val - 50
        print(f"Setting val of MyVar to {new_val}...")
        await var.write_value(new_val)

        res = await client.nodes.objects.call_method(f"{namespace_idx}:ServerMethod", 5)
        print(f"Calling ServerMethod returned {res}")

if __name__ == '__main__':
    asyncio.run(main())
