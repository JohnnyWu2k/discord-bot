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
        # Step 1: Gemini 將問題轉為關鍵字
        search_prompt = f"請將這句話轉成搜尋引擎用的精簡關鍵字：'{query}'"
        search_term = model.generate_content(search_prompt).text.strip()

        await ctx.send(f"🔍 搜尋中：{search_term}")

        # Step 2: DuckDuckGo 搜尋結果
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

        # Step 3: 擷取整個網頁所有段落
        content_res = requests.get(target_url, headers=headers, timeout=10)
        content_soup = BeautifulSoup(content_res.text, "html.parser")
        paragraphs = content_soup.find_all("p")
        all_text = " ".join(p.get_text() for p in paragraphs)

        if len(all_text) < 100:
            await ctx.send("⚠️ 網頁資料過少，AI 將嘗試根據有限資訊推論。")

        elif len(all_text) > 12000:
            all_text = all_text[:12000]
            await ctx.send("⚠️ 網頁內容過長，已截取前 12000 字處理。")

        # Step 4: Gemini 生成摘要與回答
        summary_prompt = f"以下是某個網站的全部文章內容，請你幫我摘要重點，並用中文整理給我（可推論補充）：\n{all_text}"
        summary = model.generate_content(summary_prompt).text.strip()

        # Step 5: 回傳總結
        chunks = [summary[i:i+1800] for i in range(0, len(summary), 1800)]
        for chunk in chunks:
            await ctx.send(chunk)

    except Exception as e:
        await ctx.send(f"❌ 發生錯誤：{e}")
