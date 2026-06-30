from core.logger import logger

class AIAnalyzer:
    def analyze_item(self, item, user_input):
        try:
            import google.generativeai as genai
            from core.config import Config
            genai.configure(api_key=Config.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            사용자가 찾는 물품: "{user_input}"
            분석할 매물:
            제목: {item['title']}
            가격: {item['price']}원
            설명: {item['description']}
            
            이 매물을 분석하여 아래 항목을 간결하게 요약해주세요.
            1. 부품/악기 종류 판단
            2. 브랜드 및 모델 추정
            3. 상태 분석
            4. 위험 요소 경고 (정품 여부, 넥 휨, 프렛 마모 등)
            5. 구매 전 확인 사항
            """
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.warning(f"AI 2차 분석 실패 (스킵): {e}")
            return "AI 분석 불가 (API 한도 초과 또는 오류)"
