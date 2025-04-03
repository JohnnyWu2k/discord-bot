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
        # Step 1: Gemini 轉搜尋關鍵字
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
            await ctx.send("⚠️ 找不到任何搜尋結果。")
            return

        raw_url = result_link['href']
        target_url = "https:" + raw_url if raw_url.startswith("//") else raw_url
        await ctx.send(f"🔗 使用資料來源：{target_url}")

        # Step 3: 擷取多種常見標籤文字（增加命中率）
        content_res = requests.get(target_url, headers=headers, timeout=10)
        content_soup = BeautifulSoup(content_res.text, "html.parser")
        paragraphs = content_soup.find_all(["p", "article", "section", "div"])
        texts = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50]
        all_text = " ".join(texts)

        if len(all_text) < 200:
            await ctx.send("⚠️ 抓到的資料可能不足，AI 仍將嘗試補全。")
            all_text += "\n（這些資料較少，請根據你過去的知識進行推論與補充）"

        if len(all_text) > 12000:
            all_text = all_text[:12000]
            await ctx.send("⚠️ 文章過長，已截取前 12000 字。")

        # Step 4: AI 分析與摘要
        prompt = (
            "以下是一篇文章的段落內容，請你幫我用中文摘要重點、說明主題，"
            "如果有需要可以補充推論或幫我翻譯艱澀部分：\n" + all_text
        )
        summary = model.generate_content(prompt).text.strip()

        # 分段輸出
        chunks = [summary[i:i+1800] for i in range(0, len(summary), 1800)]
        for chunk in chunks:
            await ctx.send(chunk)

    except Exception as e:
        await ctx.send(f"❌ 發生錯誤：{e}")
