import arxiv
import google.generativeai as genai
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 1. 配置 API Key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-3-flash-preview') # 使用 Flash 模型，速度快且免费

# 2. 定义你的研究兴趣 (System Prompt)
RESEARCH_INTEREST = """
我关注的研究方向是：
1. 人体姿态估计。
2. 对抗攻击。
3. 对抗防御。
请从以下论文中筛选出符合我关注方向的论文，并说明推荐理由。
"""

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
    prompt = f"{RESEARCH_INTEREST}\n\n以下是今日待筛选论文：\n\n{papers_text}"
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
