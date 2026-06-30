import sys
import traceback
from datetime import datetime
from core import storage, config, logger
from crawlers.api_crawler import APICrawler  # API 크롤러 사용!
from analyzers.rule_generator import RuleGenerator
from analyzers.analyzer import RuleBasedAnalyzer
from analyzers.ai_analyzer import AIAnalyzer
from integrations.sheets import SheetsManager
from integrations.notifier import EmailNotifier

def initial_setup():
    """최초 실행 시 사용자 조건 입력"""
    print("=== 중고 악기 AI 비서 초기 설정 ===")
    user_input = input("찾으시는 악기/부품을 자연어로 입력해주세요 (예: 펜더 텔레캐스터 넥): ")
    storage.save_user_input(user_input.strip())
    
    generator = RuleGenerator()
    rules = generator.generate_rules()
    storage.save_rules(rules)
    print("설정이 저장되었습니다. 프로그램을 다시 실행하면 자동으로 크롤링이 시작됩니다.")

def main():
    # 1. 상태 확인 및 초기 설정
    user_input = storage.get_user_input()
    if not user_input:
        initial_setup()
        user_input = storage.get_user_input()

    # 사용자 입력이 비어있다면 (깃허브 액션 등 자동 환경에서 예외 발생 방지)
    if not user_input:
        logger.warning("사용자 입력값이 없습니다. 프로그램을 종료합니다.")
        return

    rules = storage.get_rules()
    if not rules:
        generator = RuleGenerator()
        rules = generator.generate_rules()

    # 2. 크롤링 (API 크롤러 사용)
    # TODO: 나중에 실제 중고 사이트 API 주소를 분석해서 아래 가상 주소("https://api...")를 바꾸세요!
    crawler = APICrawler("https://api.example-site.com/v1/search?q=telecaster")
    
    sheets_mgr = None
    email_notifier = EmailNotifier()
    new_seen_ids = [] # 이번 사이클에서 성공적으로 처리된 아이템 ID 모음
    recommend_count = 0
    
    try:
        items = crawler.crawl()

        # 3. 분석 및 필터링
        analyzer = RuleBasedAnalyzer(rules)
        ai_analyzer = AIAnalyzer()
        
        sheets_mgr = SheetsManager()
        
        cutoff_date = datetime.strptime(config.Config.CUTOFF_DATE, "%Y-%m-%d")
        logger.info(f"총 {len(items)}개의 게시물 분석 시작...")

        for item in items:
            try:
                item_id = item['id']
                
                # 중복 체크
                if storage.is_seen(item_id):
                    continue
                    
                # 날짜 필터
                if item.get('date'):
                    if item['date'] < cutoff_date:
                        continue
                elif not config.Config.INCLUDE_NO_DATE:
                    continue
                    
                # 1차 규칙 기반 점수 계산
                score = analyzer.calculate_score(item)
                item['score'] = score
                
                # 2차 AI 분석 (가능한 경우만)
                ai_result = "AI 분석 미사용"
                if config.Config.GEMINI_API_KEY:
                    try:
                        ai_result = ai_analyzer.analyze_item(item, user_input)
                    except Exception as ai_err:
                        logger.warning(f"단일 아이템 AI 분석 에러, 스킵: {ai_err}")

                # Google Sheets 데이터 포맷팅
                is_recommend = score >= config.Config.RECOMMEND_SCORE_THRESHOLD
                grade = "S급 추천" if score >= 90 else "A급 추천" if is_recommend else "참고용"
                
                row_data = [
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "API사이트",
                    item['title'],
                    f"{item['price']:,}원",
                    item.get('date_str', '날짜 없음'),
                    score,
                    grade,
                    ai_result,
                    "",
                    item['link']
                ]
                
                # 1. 시트 저장
                sheets_mgr.append_item(row_data, is_recommend)
                
                # 2. 이메일 알림 
                if is_recommend:
                    email_notifier.send_alert(item, score, ai_result)
                    recommend_count += 1
                
                # 현재 아이템 처리 완료 -> seen 리스트에 추가 예약
                new_seen_ids.append(item_id)

            except Exception as item_err:
                # 단일 아이템 파싱 오류 시 전체 프로그램이 멈추지 않도록 다음 아이템으로 넘어감
                logger.error(f"아이템 처리 중 오류 발생 (ID: {item.get('id', 'Unknown')}): {item_err}")
                continue

        logger.info(f"실행 완료 - 신규 추천: {recommend_count}건")

    except Exception as global_err:
        # 크롤링 자체의 치명적 오류 (네트워크 단절 등)
        logger.critical(f"시스템 오류로 메인 루프가 중단되었습니다: {global_err}")
            finally:
        # 3. 안전하게 상태 업데이트 (중복 알림 방지 핵심 로직)
        if new_seen_ids:
            logger.info(f"확인된 {len(new_seen_ids)}개의 신규 아이템을 상태 파일에 안전하게 기록합니다.")
            storage.bulk_add_seen(new_seen_ids)


