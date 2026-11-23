import asyncio, edge_tts, sys; sys.stdout.reconfigure(encoding="utf-8")
async def one(t, v="ar-EG-SalmaNeural"):
    n = 0; last = 0; words = []
    async for c in edge_tts.Communicate(t, v, boundary="WordBoundary").stream():
        if c["type"] == "audio": n += len(c["data"])
        else: words.append(c['text']); last = (c["offset"] + c["duration"]) / 1e7
    print(v[:5], repr(t), [w for w in words], 'audio bytes', n, 'last word ends', round(last, 2))
async def main():
    for v in ["ar-EG-SalmaNeural", "ar-SA-HamedNeural"]:
      for t in ["الثمن ١.٥ جنيه.", "الثمن 1.5 جنيه.", "الثمن ١٠٠٠ جنيه.", "الثمن ١٫٥ جنيه.", "الثمن ١٬٠٠٠ جنيه."]: await one(t, v)
asyncio.run(main())
