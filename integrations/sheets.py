import base64
import json
import os
import tempfile
import gspread
from core.config import Config
from core.logger import logger

class SheetsManager:
    def __init__(self):
        self.gc = None
        self.spreadsheet = None
        self._authenticate()

    def _authenticate(self):
        try:
            # GitHub Actions Secrets에서 Base64로 디코딩하여 임시 파일 생성
            b64_key = Config.GCP_SERVICE_ACCOUNT_B64
            json_key = base64.b64decode(b64_key).decode('utf-8')
            
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w')
            tmp.write(json_key)
            tmp.close()
            
            self.gc = gspread.service_account(filename=tmp.name)
            self.spreadsheet = self.gc.open_by_key(Config.GCP_SHEETS_ID)
            
            # 시트 없으면 생성
            try:
                self.spreadsheet.worksheet(Config.SHEET_RECOMMEND)
            except gspread.exceptions.WorksheetNotFound:
                self.spreadsheet.add_worksheet(title=Config.SHEET_RECOMMEND, rows="100", cols="20")
                self._set_headers(Config.SHEET_RECOMMEND)
                
            try:
                self.spreadsheet.worksheet(Config.SHEET_REFERENCE)
            except gspread.exceptions.WorksheetNotFound:
                self.spreadsheet.add_worksheet(title=Config.SHEET_REFERENCE, rows="100", cols="20")
                self._set_headers(Config.SHEET_REFERENCE)
                
            os.unlink(tmp.name) # 임시 파일 삭제
        except Exception as e:
            logger.error(f"Google Sheets 인증/초기화 실패: {e}")

    def _set_headers(self, sheet_name):
        ws = self.spreadsheet.worksheet(sheet_name)
        headers = ["검색 날짜", "사이트", "제목", "가격", "등록 날짜", "규칙 점수", "추천 등급", "AI 분석", "경고 사항", "링크"]
        ws.append_row(headers)

    def append_item(self, item_data, is_recommend):
        try:
            sheet_name = Config.SHEET_RECOMMEND if is_recommend else Config.SHEET_REFERENCE
            ws = self.spreadsheet.worksheet(sheet_name)
            ws.append_row(item_data)
        except Exception as e:
            logger.error(f"시트 저장 실패: {e}")
