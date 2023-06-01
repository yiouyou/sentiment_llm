import openiap, asyncio
from openiap import Client
from util import sentiment_llm


async def __wait_for_message(cli: Client, message, payload):
    workitem = await cli.PopWorkitem("testq")
    if workitem != None:
        workitem.state = "successful"
        cli.UpdateWorkitem(workitem, None, True)


async def onconnected(cli: Client):
    try:
        await cli.Signin()
        print("Connected to OpenIAP")
        queuename = await cli.RegisterQueue("", __wait_for_message)
        print(f"Consuming queue {queuename}")
        result = await cli.Query(
            collectionname="entities", projection={"_created": 1, "name": 1, "_type": 1}
        )
        print(result)

    except Exception as e:
        print(e)
    # cli.Close()


async def main():
    client = openiap.Client()
    client.onconnected = onconnected
    await asyncio.sleep(2)
    while True:
        await asyncio.sleep(1)


asyncio.run(main())
