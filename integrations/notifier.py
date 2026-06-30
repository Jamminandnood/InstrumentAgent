import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.config import Config
from core.logger import logger

class EmailNotifier:
    def send_alert(self, item, score, ai_analysis):
        try:
            msg = MIMEMultipart("alternative")
            msg['From'] = Config.EMAIL_SENDER
            msg['To'] = Config.EMAIL_RECEIVER
            msg['Subject'] = f"[악기 비서] 추천 매물 발견! ({item['title'][:20]}...)"
            
            html = f"""
            <h3>새로운 추천 매물이 발견되었습니다!</h3>
            <p><strong>상품명:</strong> {item['title']}</p>
            <p><strong>가격:</strong> {item['price']:,}원</p>
            <p><strong>점수:</strong> {score}점</p>
            <p><strong>링크:</strong> <a href="{item['link']}">매물 보러가기</a></p>
            <hr>
            <p><strong>AI 평가:</strong><br>{ai_analysis.replace(chr(10), '<br>')}</p>
            """
            
            msg.attach(MIMEText(html, "html", "utf-8"))
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(Config.EMAIL_SENDER, Config.EMAIL_PASSWORD)
                server.sendmail(Config.EMAIL_SENDER, Config.EMAIL_RECEIVER, msg.as_string())
                
            logger.info(f"이메일 알림 전송 완료: {item['title']}")
        except Exception as e:
            logger.error(f"이메일 전송 실패: {e}")
