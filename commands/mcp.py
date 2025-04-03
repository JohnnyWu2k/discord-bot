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
        # Step 1: Gemini 轉成搜尋關鍵字
        search_prompt = f"請將這句話轉成搜尋引擎用的精簡關鍵字：'{query}'"
        search_term = model.generate_content(search_prompt).text.strip()
        await ctx.send(f"🔍 搜尋中：{search_term}")

        # Step 2: DuckDuckGo 搜尋
        url = f"https://html.duckduckgo.com/html/?q={search_term}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        result_links = soup.find_all("a", class_="result__a")

        if not result_links:
            await ctx.send("⚠️ 找不到任何搜尋結果。")
            return

        # 嘗試每個連結直到抓到夠的內容
        target_url = ""
        all_text = ""
        for link in result_links:
            raw_url = link['href']
            target_url = "https:" + raw_url if raw_url.startswith("//") else raw_url
            try:
                content_res = requests.get(target_url, headers=headers, timeout=10)
                content_soup = BeautifulSoup(content_res.text, "html.parser")
                # 多抓幾種內容標籤
                paragraphs = content_soup.find_all(["p", "article", "section", "div"])
                texts = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50]
                all_text = " ".join(texts)
                if len(all_text) > 500:
                    break
            except:
                continue  # 換下一個網址

        if not all_text:
            await ctx.send("⚠️ 無法從任何搜尋結果中擷取足夠資料。")
            return

        await ctx.send(f"🔗 使用資料來源：{target_url}")
        if len(all_text) > 12000:
            all_text = all_text[:12000]
            await ctx.send("⚠️ 文章過長，已截取前 12000 字。")

        # Step 3: Gemini 分析與補全
        summary_prompt = (
            "以下是網站內容的原文段落。請你用中文總結這些資料的重點。"
            "如果你覺得資料仍不足，請主動補充推論或背景知識，"
            "讓回答更完整且容易理解：\n" + all_text
        )
        summary = model.generate_content(summary_prompt).text.strip()

        # 分段回傳
        chunks = [summary[i:i+1800] for i in range(0, len(summary), 1800)]
        for chunk in chunks:
            await ctx.send(chunk)

    except Exception as e:
        await ctx.send(f"❌ 發生錯誤：{e}")
