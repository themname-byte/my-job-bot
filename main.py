import os
import json
import requests
import gspread
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.service_account import Credentials

def send_email(rows):
    sender = os.environ['GMAIL_ADDRESS']        # ← 이렇게 되어 있어야 함
    password = os.environ['GMAIL_APP_PASSWORD'] # ← 이렇게 되어 있어야 함
    receiver = os.environ['GMAIL_ADDRESS']

    msg = MIMEMultipart()
    msg['Subject'] = f'오늘의 원티드 채용공고 ({len(rows)-1}건)'
    msg['From'] = sender
    msg['To'] = receiver

    # 이메일 본문 구성
    body = "📋 오늘의 채용공고 스크리닝 결과\n"
    body += "=" * 50 + "\n\n"

    for row in rows[1:]:  # 헤더 제외
        body += f"🏢 회사명: {row[0]}\n"
        body += f"📌 공고명: {row[1]}\n"
        body += f"⏰ 마감일: {row[2]}\n"
        body += f"🔗 링크: {row[3]}\n"
        body += "-" * 40 + "\n"

    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)
    print("이메일 발송 완료!")

def update_sheets():
    # 1. 인증 정보 로드
    info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(info, scopes=scope)
    client = gspread.authorize(creds)

    # 2. 구글 시트 연결
    SPREADSHEET_ID = "1zcV1J-dj0ZpsVk5T0cr5qEiGrbWAc3Hk9rjt88MWOxE"
    try:
        sheet = client.open_by_key(SPREADSHEET_ID).get_worksheet(0)
    except Exception as e:
        print(f"에러 발생: {e}")
        return

    # 3. 원티드 데이터 스크래핑
    url = "https://www.wanted.co.kr/api/v4/jobs?country=kr&tag_type_ids=507&job_sort=job.latest_order&years=3&years=10&locations=seoul.all"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    data = response.json()

    # 4. 데이터 정리
    rows = [["회사명", "공고명", "마감일", "링크"]]
    for job in data.get('data', []):
        rows.append([
            job['company']['name'],
            job['position'],
            job['due_time'],
            f"https://www.wanted.co.kr/wd/{job['id']}"
        ])

    # 5. 구글 시트 업데이트
    sheet.clear()
    sheet.append_rows(rows)
    print("구글 시트 업데이트 완료!")

    # 6. 이메일 발송
    send_email(rows)

if __name__ == "__main__":
    update_sheets()
