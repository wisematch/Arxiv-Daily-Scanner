import arxiv
import google.generativeai as genai
import os

# 1. 配置 API Key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-3-flash-preview') # 使用 Flash 模型，速度快且免费

# 2. 定义你的研究兴趣 (System Prompt)
RESEARCH_INTEREST = """
我关注的研究方向是：
1. 。
2. 扩散模型 (Diffusion Models) 的推理加速技术。
3. 医疗影像的鲁棒性分析。
请从以下论文中筛选出 Top 3，并说明推荐理由。
"""

def get_latest_papers(query="cat:cs.CV", max_results=20):
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    
    paper_list = []
    for res in client.results(search):
        paper_info = f"标题: {res.title}\n链接: {res.pdf_url}\n摘要: {res.summary[:500]}..."
        paper_list.append(paper_info)
    return "\n\n---\n\n".join(paper_list)

def screen_papers_with_gemini(papers_text):
    prompt = f"{RESEARCH_INTEREST}\n\n以下是今日待筛选论文：\n\n{papers_text}"
    response = model.generate_content(prompt)
    return response.text

# 执行流程
print("正在从 ArXiv 获取最新论文...")
latest_content = get_latest_papers("cat:cs.CV", max_results=30) # 获取 CV 领域前 30 篇

print("正在调用 Gemini 进行智能筛选...")
report = screen_papers_with_gemini(latest_content)

print("\n==== 每日论文精选报告 ====\n")
print(report)
