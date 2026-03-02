import arxiv
import google.generativeai as genai
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 1. 配置 API Key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-3-flash-preview') # 使用 Flash 模型，速度快且免费


# Prompt
PROMPT_TEMPLATE = """
你是一位顶尖的 AI 首席科学家。请分析以下今日最新的 ArXiv 论文列表，并生成一份 HTML 格式的学术简报。

### 你的任务：
1. **总体研究风向分析**：基于今日所有论文的标题和摘要，总结出 2-3 条当前 CV 领域的最新研究趋势或热点转向（例如：从单纯的生成转向可控性、具身智能的物理对齐等）。
2. **论文精选（我的兴趣：{interest}）**：从列表中筛选出最符合我兴趣的论文。
3. **输出格式**：必须输出完整的 HTML 代码，包含简单的 CSS 样式（如表格边框、背景色、字体等），确保在邮件客户端中显示美观。

### HTML 结构要求：
- 使用 <h2> 标题展示“今日风向趋势”。
- 使用 <table> 展示精选论文，列包含：标题、核心亮点（1句话）、推荐分（1-10）、链接。
- 整体风格简洁、学术、专业。

### 待处理论文列表：
{papers_text}
"""


# 2. 定义你的研究兴趣 (System Prompt)
RESEARCH_INTEREST = "人体姿态估计、对抗攻击与防御、多目标跟踪"

def get_latest_papers(query="cat:cs.CV", max_results=30):
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



    # try:
    #     # 使用 SSL 加密连接
    #         server = smtplib.SMTP(smtp_server, 587)
    #         server.starttls() # 启用 TLS 加密
    #         server.login(sender, password)
    #         server.sendmail(sender, [receiver], message.as_string())
    #         server.quit()
    #         print("邮件推送成功！")
    # except Exception as e:
    #     print(f"邮件推送失败: {e}")

def send_email(content):
    sender = os.environ["EMAIL_SENDER"]      # 必须是 xxx@qq.com
    password = os.environ["EMAIL_PASSWORD"]  # 16位授权码
    receiver = os.environ["EMAIL_RECEIVER"]
    smtp_server = "smtp.qq.com"

    message = MIMEText(content, 'plain', 'utf-8')
    
    message['From'] = f"Gemini Academic Assistant <{sender}>"
    message['To'] = receiver
    message['Subject'] = Header("今日 Arxiv 论文精选报告", 'utf-8')

    try:
        # 建议继续使用 465 端口和 SMTP_SSL，这对 QQ 邮箱最稳定
        with smtplib.SMTP_SSL(smtp_server, 465) as server:
            server.login(sender, password)
            server.sendmail(sender, [receiver], message.as_string())
        print("邮件推送成功！")
    except Exception as e:
        print(f"邮件推送失败: {e}")

def screen_papers_with_gemini(papers_text):
    prompt = PROMPT_TEMPLATE.format(interest=RESEARCH_INTEREST, papers_text=latest_content)
    response = model.generate_content(prompt)
    return response.text

# 执行流程
if __name__ == "__main__":
    print("正在从 ArXiv 获取最新论文...")
    latest_content = get_latest_papers("cat:cs.CV", max_results=30) # 获取 CV 领域前 30 篇
    
    print("正在调用 Gemini 进行智能筛选...")
    report = screen_papers_with_gemini(latest_content)
    
    print("\n==== 每日论文精选报告 ====\n")
    print(report)
    send_email(report)
