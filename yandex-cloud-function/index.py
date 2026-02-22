import os
import uuid
import json
from datetime import datetime, timezone

from pymongo import MongoClient

MONGO_URL = os.environ.get("MONGO_URL", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
DADATA_API_KEY = os.environ.get("DADATA_API_KEY", "")
SUPPORT_EMAIL = "khabibullaevakhrorjon@gmail.com"
SUPPORT_PHONE = "+79998214758"

_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
        # Подключаемся с отключённой проверкой сертификата для внутренней сети VPC
        _client = MongoClient(
            MONGO_URL,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000,
            socketTimeoutMS=30000
        )
        _db = _client.mapchap
    return _db

def json_response(data, status_code=200):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        },
        'body': json.dumps(data, default=str, ensure_ascii=False)
    }

def serialize_doc(doc):
    if doc is None:
        return None
    doc = dict(doc)
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

BOOST_PLANS = {
    "1day": {"days": 1, "name": "1 День", "price": 350, "currency": "XTR"},
    "5days": {"days": 5, "name": "5 Дней", "price": 1200, "currency": "XTR"},
    "7days": {"days": 7, "name": "7 Дней", "price": 1600, "currency": "XTR"}
}

def handle_health(event, context):
    return json_response({"status": "ok", "version": "3.0.0", "service": "MapChap API"})

def handle_db_test(event, context):
    try:
        db = get_db()
        db.command('ping')
        count = db.users.count_documents({})
        return json_response({"status": "connected", "users_count": count, "mongo_url": MONGO_URL[:40]+"..."})
    except Exception as e:
        return json_response({"status": "error", "error": str(e)}, 500)

def handle_categories(event, context):
    categories = [
        {"id": "food", "name": "Еда и рестораны", "icon": "🍕", "color": "#FF6B6B"},
        {"id": "shopping", "name": "Магазины", "icon": "🛍️", "color": "#4ECDC4"},
        {"id": "grocery", "name": "Продукты", "icon": "🛒", "color": "#22C55E"},
        {"id": "beauty", "name": "Салоны красоты", "icon": "💄", "color": "#FFD166"},
        {"id": "services", "name": "Услуги", "icon": "🔧", "color": "#06D6A0"},
        {"id": "medical", "name": "Медицина", "icon": "⚕️", "color": "#118AB2"},
        {"id": "furniture", "name": "Мебель и декор", "icon": "🛋️", "color": "#073B4C"},
        {"id": "pharmacy", "name": "Аптеки", "icon": "💊", "color": "#EF476F"},
        {"id": "fitness", "name": "Фитнес клубы", "icon": "💪", "color": "#F97316"},
        {"id": "entertainment", "name": "Развлечения", "icon": "🎭", "color": "#7209B7"},
        {"id": "education", "name": "Образование", "icon": "📚", "color": "#F72585"},
        {"id": "auto", "name": "Автосервисы", "icon": "🚗", "color": "#4361EE"},
        {"id": "hotel", "name": "Отели", "icon": "🏨", "color": "#4CC9F0"}
    ]
    return json_response({"categories": categories})

def handle_app_info(event, context):
    return json_response({"name": "MapChap", "version": "3.0.0", "support": {"email": SUPPORT_EMAIL, "phone": SUPPORT_PHONE}})

def handle_telegram_auth(event, context):
    try:
        db = get_db()
        body = json.loads(event.get('body', '{}'))
        telegram_id = body.get('id')
        if not telegram_id:
            return json_response({"error": "telegram_id required"}, 400)
        
        existing = db.users.find_one({"telegram_id": telegram_id})
        if existing:
            db.users.update_one({"telegram_id": telegram_id}, {"$set": {"first_name": body.get('first_name', ''), "last_login": datetime.now(timezone.utc)}})
            user = db.users.find_one({"telegram_id": telegram_id})
        else:
            user = {"id": str(uuid.uuid4()), "telegram_id": telegram_id, "first_name": body.get('first_name', ''), "role": "user", "is_verified": False, "favorites": [], "created_at": datetime.now(timezone.utc)}
            db.users.insert_one(user)
        return json_response({"success": True, "user": serialize_doc(user)})
    except Exception as e:
        return json_response({"error": str(e)}, 500)

def handle_get_user(event, context, telegram_id):
    try:
        db = get_db()
        user = db.users.find_one({"telegram_id": int(telegram_id)})
        return json_response(serialize_doc(user)) if user else json_response({"error": "User not found"}, 404)
    except Exception as e:
        return json_response({"error": str(e)}, 500)

def handle_get_offers(event, context):
    try:
        db = get_db()
        query = {"status": "active"}
        offers = list(db.offers.find(query).limit(50))
        return json_response({"offers": [serialize_doc(o) for o in offers], "total": len(offers)})
    except Exception as e:
        return json_response({"error": str(e), "offers": [], "total": 0})

def handle_boost_plans(event, context):
    return json_response({"plans": [{"id": k, **v} for k, v in BOOST_PLANS.items()]})

def handle_articles(event, context):
    try:
        db = get_db()
        articles = list(db.articles.find({"status": "published"}).limit(20))
        return json_response({"articles": [serialize_doc(a) for a in articles], "total": len(articles)})
    except Exception as e:
        return json_response({"error": str(e), "articles": [], "total": 0})

def handler(event, context):
    method = event.get('httpMethod', 'GET')
    if method == 'OPTIONS':
        return json_response({})
    
    path = event.get('path', '/').replace('/api', '') if event.get('path', '/').startswith('/api') else event.get('path', '/')
    
    routes = {
        ('GET', '/health'): handle_health,
        ('GET', '/db-test'): handle_db_test,
        ('GET', '/categories'): handle_categories,
        ('GET', '/app-info'): handle_app_info,
        ('POST', '/auth/telegram'): handle_telegram_auth,
        ('GET', '/offers'): handle_get_offers,
        ('GET', '/articles'): handle_articles,
        ('GET', '/boosts/plans'): handle_boost_plans,
    }
    
    if (method, path) in routes:
        return routes[(method, path)](event, context)
    
    parts = path.strip('/').split('/')
    if len(parts) == 2 and parts[0] == 'users':
        return handle_get_user(event, context, parts[1])
    
    return json_response({"error": f"Not found: {method} {path}"}, 404)
