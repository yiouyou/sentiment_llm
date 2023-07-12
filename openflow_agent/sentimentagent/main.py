import os
import openiap, asyncio
from openiap import Client
from util_sentiment import sentiment_llm
from util_competitor import competitor_llm
from util_7P import P7_llm


async def __wait_for_message(cli: Client, message, payload):
    try:
        print(payload)
        _sentiment = ""
        _7p = ""
        _competitor = ""
        _cost_sentiment = ""
        _cost_competitor = ""
        _cost_7p = ""
        _total_cost_d5 = ""
        [_sentiment, _cost_sentiment] = sentiment_llm(payload["text"])
        [_competitor, _cost_competitor] = competitor_llm(payload["text"])
        [_7p, _cost_7p] = P7_llm(payload["text"])
        payload["sentiment"] = _sentiment
        payload["pronouns"] = _competitor
        payload["noun"] = _7p
        _cost_sentiment_d5 = format(float(_cost_sentiment), ".5f")
        _cost_competitor_d5 = format(float(_cost_competitor), ".5f")
        _cost_7p_d5 = format(float(_cost_7p), ".5f")
        _total_cost_d5 = format(float(_cost_sentiment) + float(_cost_competitor) + float(_cost_7p), ".5f")
        payload["parameters"] = f"${_total_cost_d5}=(${_cost_sentiment_d5}+${_cost_competitor_d5}+${_cost_7p_d5})"
    except Exception as e:
        print(e)
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
        # await cli.QueueMessage(queuename, {"text": "Ved ikke om de har noget organisk affald... på deres hovedkontor har de et køkken, men det er en ekstern operatør der driver det... det er Michael Kjær fra driften, et fælles køkken med andre virksomheder.. Ring til ham om det. NCC bestemmer desuden selv om de skal have vores projekt med i loopet på dgnb point i byggeriet... i deres koncept udvikling...; De er ved at definere det og vi kan vende retur til Martin i Januar, hvor han ved hvem vi skal have møde med om det."})

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
