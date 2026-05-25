import os
import json
import requests
import gspread
from google.oauth2.service_account import Credentials

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

if __name__ == "__main__":
    update_sheets()
