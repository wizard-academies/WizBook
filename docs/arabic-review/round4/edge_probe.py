import asyncio, edge_tts, sys; sys.stdout.reconfigure(encoding="utf-8")
CASES = [("ar-EG-SalmaNeural", t) for t in ["الثمن ١٬٠٠٠.", "الثمن 1,000.", "الثمن ١٠٠٠.", "من ١٩١٤ إلى ١٩١٨."]] + [("en-US-AndrewNeural", "It cost 1,000 dollars.")]
async def one(v, t):
    words = []
    async for c in edge_tts.Communicate(t, v, boundary="WordBoundary").stream():
        if c["type"] == "WordBoundary": words.append(c["text"])
    print(repr(t), '->', words[-4:])
async def main():
    for v, t in CASES: await one(v, t)
asyncio.run(main())
