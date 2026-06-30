import json
import os
import hashlib

STATE_FILE = "data/state.json"

def _load_state():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(STATE_FILE):
        return {"seen_items": [], "user_input": "", "rules": []}
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def _save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=4)

def get_user_input():
    return _load_state().get("user_input", "")

def save_user_input(text):
    state = _load_state()
    state["user_input"] = text
    _save_state(state)

def get_rules():
    return _load_state().get("rules", [])

def save_rules(rules):
    state = _load_state()
    state["rules"] = rules
    _save_state(state)

def is_seen(item_identifier):
    state = _load_state()
    return item_identifier in state["seen_items"]

def add_seen(item_identifier):
    state = _load_state()
    state["seen_items"].append(item_identifier)
    _save_state(state)

def generate_hash(title, price, link, date):
    """게시물 ID가 없을 경우 해시 생성"""
    raw = f"{title}{price}{link}{date}"
    return hashlib.md5(raw.encode('utf-8')).hexdigest()
