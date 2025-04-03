from discord.ext import commands
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

@commands.command()
async def mcp(ctx, *, query: str):
    await ctx.send(f"🧠 MCP 啟動中，目標：{query}")
    try:
        # Step 1: Gemini 轉關鍵字
        search_prompt = f"請將這句話轉成搜尋引擎用的精簡關鍵字：'{query}'"
        search_term = model.generate_content(search_prompt).text.strip()

        await ctx.send(f"🔍 搜尋中：{search_term}")

        # Step 2: DuckDuckGo 搜尋
        url = f"https://html.duckduckgo.com/html/?q={search_term}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        result_link = soup.find("a", class_="result__a")

        if not result_link:
            await ctx.send("⚠️ 找不到任何相關結果。")
            return

        raw_url = result_link['href']
        if raw_url.startswith("//"):
            target_url = "https:" + raw_url
        else:
            target_url = raw_url

        await ctx.send(f"🔗 最佳結果：{target_url}")

        # Step 3: 擷取網頁內容
        content_res = requests.get(target_url, headers=headers, timeout=10)
        content_soup = BeautifulSoup(content_res.text, "html.parser")
        paragraphs = content_soup.find_all("p")
        raw_text = " ".join(p.get_text() for p in paragraphs[:5])  # 擷取前幾段

        if len(raw_text) < 100:
            await ctx.send("⚠️ 抓到的內容太少，無法摘要。")
            return

        # Step 4: Gemini 摘要
        summary_prompt = f"以下是從網頁擷取的資料，請幫我摘要並以中文說明：\n{raw_text}"
        summary = model.generate_content(summary_prompt).text.strip()

        # Step 5: 回傳結果
        await ctx.send(f"📄 回覆：\n{summary[:1800]}")  # 預防超過 Discord 字數限制
    except Exception as e:
        await ctx.send(f"❌ 發生錯誤：{e}")
