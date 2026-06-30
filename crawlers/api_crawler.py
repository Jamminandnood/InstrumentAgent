import json
from .base_crawler import BaseCrawler
from core.storage import generate_hash
from core.logger import logger
from datetime import datetime

class APICrawler(BaseCrawler):
    """
    당근마켓, 번개장터 등 API 기반 사이트 크롤링용 클래스입니다.
    """
    def __init__(self, base_url):
        super().__init__(base_url)
        # API는 보통 JSON 요청을 기대하므로 헤더를 수정합니다.
        self.session.headers.update({
            'Accept': 'application/json, text/plain, */*',
            'Referer': base_url # 사이트에서 막는 것을 우회하기 위해 Referer 설정
        })

    def parse_items(self, response_text):
        # API는 HTML이 아니라 JSON 데이터를 반환하므로 BeautifulSoup을 쓰지 않습니다.
        try:
            data = json.loads(response_text)
            # 가상의 API 응답 구조입니다. 실제 사이트 분석 후 이 부분을 수정해야 합니다.
            documents = data.get('data', {}).get('documents', []) 
            
            items = []
            for doc in documents:
                post_id = str(doc.get('id', ''))
                title = doc.get('title', '')
                price = int(doc.get('price', 0)) if doc.get('price') else 0
                link = f"https://당근마켓或有사이트.com/items/{post_id}"
                date_str = doc.get('createdAt', '')[:10] # 예: "2026-03-15"
                
                date_obj = datetime.strptime(date_str, "%Y-%m-%d") if date_str else None
                item_id = post_id if post_id else generate_hash(title, str(price), link, date_str)
                
                items.append({
                    'id': item_id,
                    'title': title,
                    'price': price,
                    'link': link,
                    'date': date_obj,
                    'date_str': date_str,
                    'status': doc.get('status', '판매중'),
                    'description': doc.get('content', ''),
                    'images': [img.get('url') for img in doc.get('images', [])]
                })
            return items
        except Exception as e:
            logger.error(f"API 응답 파싱 오류: {e}")
            return []

    def get_next_page_url(self, html, current_page):
        # API 방식에서는 보통 URL 뒤에 ?page= 숫자를 붙여서 다음 페이지를 요청합니다.
        separator = "&" if "?" in self.base_url else "?"
        return f"{self.base_url}{separator}page={current_page}"
