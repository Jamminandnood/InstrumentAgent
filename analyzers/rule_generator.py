import json
from core.storage import get_user_input, save_rules, get_rules
from core.logger import logger

class RuleGenerator:
    def generate_rules(self):
        user_input = get_user_input()
        if not user_input:
            return []

        # 1. AI 시도 (Gemini)
        rules = self._generate_with_ai(user_input)
        if rules:
            logger.info("AI가 점수 규칙을 생성했습니다.")
            # TODO: 실제 서비스 시 사용자 승인 로직 추가 (콘솔 입력 y/n)
            save_rules(rules)
            return rules

        # 2. 기존 규칙 확인
        existing_rules = get_rules()
        if existing_rules:
            logger.info("AI 사용 불가. 기존 저장된 규칙을 사용합니다.")
            return existing_rules

        # 3. 기본 규칙 생성
        logger.info("AI 사용 불가 및 기존 규칙 없음. 기본 규칙을 생성합니다.")
        rules = self._generate_default_rules(user_input)
        save_rules(rules)
        return rules

    def _generate_with_ai(self, user_input):
        try:
            import google.generativeai as genai
            from core.config import Config
            genai.configure(api_key=Config.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            사용자가 중고 악기/부품을 찾습니다: "{user_input}"
            아래 형식의 JSON 배열로 점수 규칙을 생성하세요.
            브랜드를 직접 언급하지 않았다면 유명 브랜드를 임의로 우대하는 규칙은 만들지 마세요.
            [
              {{"type": "keyword", "value": "텔레캐스터", "score": 30}},
              {{"type": "keyword", "value": "넥", "score": 30}},
              {{"type": "condition_good", "value": "상태 좋음", "score": 20}},
              {{"type": "condition_bad", "value": "고장", "score": -50}},
              {{"type": "condition_bad", "value": "수리 필요", "score": -50}}
            ]
            오직 JSON 배열만 반환하세요.
            """
            response = model.generate_content(prompt)
            return json.loads(response.text.replace("```json", "").replace("```", "").strip())
        except Exception as e:
            logger.warning(f"AI 규칙 생성 실패: {e}")
            return None

    def _generate_default_rules(self, user_input):
        # 간단한 토큰화 (띄어쓰기 기준)
        keywords = user_input.split()
        rules = []
        for kw in keywords:
            rules.append({"type": "keyword", "value": kw, "score": 30})
        
        # 기본 상태 규칙 추가
        rules.extend([
            {"type": "condition_good", "value": "상태 좋음", "score": 20},
            {"type": "condition_good", "value": "미사용", "score": 20},
            {"type": "condition_bad", "value": "고장", "score": -50},
            {"type": "condition_bad", "value": "수리 필요", "score": -50},
            {"type": "condition_bad", "value": "파손", "score": -40}
        ])
        return rules
