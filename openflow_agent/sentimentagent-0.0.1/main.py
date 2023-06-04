import os
import openiap, asyncio
from openiap import Client
from util import sentiment_llm


async def __wait_for_message(cli: Client, message, payload):
    print(payload)
    _sentiment = ""
    _cost = ""
    _7p = ""
    _competitor = ""
    # [_sentiment, _cost, _7p, _competitor] = sentiment_llm(payload["text"])
    [_sentiment, _cost] = sentiment_llm(payload["text"])
    payload["sentiment"] = _sentiment
    payload["parameters"] = _cost
    payload["noun"] = _7p
    payload["pronouns"] = _competitor
    return payload


async def onconnected(cli: Client):
    try:
        await cli.Signin()
        print("Connected to OpenIAP")
        queuename = os.getenv("queuename")
        if os.getenv("debug") == "true":
            queuename += "_debug"
        queuename = await cli.RegisterQueue(queuename, __wait_for_message)
        print(f"Consuming queue {queuename}")
        result = await cli.Query(
            collectionname="pipedrive", projection={"note": 1, "name": 1, "_type": 1}, query={"_type": "activity"}
        )
        print(result)
        # await cli.QueueMessage(queuename, {"text": "Opfølgning på målinger i de andre butikker. Obs. på at der altid er lidt mere og obs på at det er efterårsferie, hvis det har noget at sige for omsætningen. Desuden obs på, at det er meningen, det skal opbevares i længere tid."})

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
