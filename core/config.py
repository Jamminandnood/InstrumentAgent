import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API 및 인증 키 (GitHub Actions Secrets 또는 .env에서 로드)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GCP_SERVICE_ACCOUNT_B64 = os.getenv("GCP_SERVICE_ACCOUNT_B64") # Base64 인코딩된 JSON 키
    GCP_SHEETS_ID = os.getenv("GCP_SHEETS_ID")
    
    EMAIL_SENDER = os.getenv("EMAIL_SENDER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD") # Gmail 앱 비밀번호
    EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
    
    # 탐색 설정
    MIN_PAGES = 1
    MAX_PAGES = 10
    CUTOFF_DATE = "2026-01-01" # 이 날짜 이후 게시물만 분석
    INCLUDE_NO_DATE = False # 날짜 없는 게시물 포함 여부
    RECOMMEND_SCORE_THRESHOLD = 70 # 추천 매물 최소 점수
    
    # Sheets 이름 설정
    SHEET_RECOMMEND = "추천 매물"
    SHEET_REFERENCE = "참고 매물"
    
    # 크롤링 속도 제한 (초)
    REQUEST_DELAY_MIN = 2.0
    REQUEST_DELAY_MAX = 5.0
    MAX_RETRIES = 3
