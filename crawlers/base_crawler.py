import time
import random
import requests
from abc import ABC, abstractmethod
from core.config import Config
from core.logger import logger

class BaseCrawler(ABC):
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def delay(self):
        time.sleep(random.uniform(Config.REQUEST_DELAY_MIN, Config.REQUEST_DELAY_MAX))

    def fetch_page(self, url, retries=Config.MAX_RETRIES):
        for attempt in range(retries):
            try:
                self.delay()
                res = self.session.get(url, timeout=10)
                res.raise_for_status()
                return res
            except Exception as e:
                logger.warning(f"요청 실패 ({attempt+1}/{retries}): {url} - {e}")
        return None

    @abstractmethod
    def parse_items(self, html):
        """게시물 목록 파싱 (반환: dict 리스트)"""
        pass

    @abstractmethod
    def get_next_page_url(self, html, current_page):
        """다음 페이지 URL 반환 (없으면 None)"""
        pass

    def crawl(self, max_pages=Config.MAX_PAGES):
        logger.info(f"[{self.__class__.__name__}] 크롤링 시작: {self.base_url}")
        items = []
        current_page = Config.MIN_PAGES
        
        while current_page <= max_pages:
            url = self.get_next_page_url(None, current_page) if current_page > 1 else self.base_url
            if not url:
                logger.info("다음 페이지 없음. 탐색 종료.")
                break
                
            res = self.fetch_page(url)
            if not res:
                logger.error(f"페이지 {current_page} 로드 실패. 스킵합니다.")
                current_page += 1
                continue

            page_items = self.parse_items(res.text)
            items.extend(page_items)
            current_page += 1
            
        return items
