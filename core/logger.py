import logging
import os
from datetime import datetime

# logger라는 이름으로 바로 쓸 수 있게 세팅합니다.
logger = logging.getLogger("InstrumentAgent")
logger.setLevel(logging.INFO)

# 콘솔 핸들러
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# 파일 핸들러 (logs 폴더에 저장)
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
fh = logging.FileHandler(f"{log_dir}/run_{datetime.now().strftime('%Y%m%d')}.log", encoding='utf-8')
fh.setLevel(logging.INFO)

formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)
fh.setFormatter(formatter)

# 중복 추가 방지
if not logger.handlers:
    logger.addHandler(ch)
    logger.addHandler(fh)