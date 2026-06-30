from core.logger import logger

class RuleBasedAnalyzer:
    def __init__(self, rules):
        self.rules = rules

    def calculate_score(self, item):
        score = 0
        text_to_analyze = f"{item.get('title', '')} {item.get('description', '')}".lower()
        
        for rule in self.rules:
            rule_value = rule.get("value", "").lower()
            if rule_value and rule_value in text_to_analyze:
                score += rule.get("score", 0)
                
        # 가격 기반 가산점 (예: 50만원 이하 가산 - 설정에 따라 변경 가능)
        if 0 < item.get('price', 0) <= 500000:
            score += 10
            
        return max(score, 0) # 최소 0점

