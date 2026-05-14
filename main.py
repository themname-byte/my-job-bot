import os
import json
import requests
import gspread
from google.oauth2.service_account import Credentials

def update_sheets():
    # 1. GitHub Secrets에서 구글 인증 정보 가져오기
    info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(info, scopes=scope)
    client = gspread.authorize(creds)

    # 2. 구글 시트 열기 (본인의 시트 이름을 적으세요)
    sheet = client.open("원티드 채용공고").get_worksheet(0)

    # 3. 원티드 데이터 스크래핑 (사용자 요청 URL 기반)
    url = "https://www.wanted.co.kr/api/v4/jobs?country=kr&tag_type_ids=507&job_sort=job.latest_order&years=3&years=10&locations=seoul.all"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    data = response.json()

    # 4. 데이터 정리 및 시트 업데이트
    rows = [["회사명", "공고명", "경력", "마감일", "링크"]]
    for job in data.get('data', []):
        rows.append([
            job['company']['name'],
            job['position'],
            f"{job['experience_level']}",
            job['due_time'],
            f"https://www.wanted.co.kr/wd/{job['id']}"
        ])

    sheet.clear()
    sheet.append_rows(rows)
    print("업데이트 완료!")

if __name__ == "__main__":
    update_sheets()
