import os
import uuid
import math
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, List
import ssl
import tempfile

from pymongo import MongoClient
import httpx

# ===================== CONFIG =====================
MONGO_URL = os.environ.get("MONGO_URL", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
DADATA_API_KEY = os.environ.get("DADATA_API_KEY", "")
SUPPORT_EMAIL = os.environ.get("SUPPORT_EMAIL", "khabibullaevakhrorjon@gmail.com")
SUPPORT_PHONE = os.environ.get("SUPPORT_PHONE", "+79998214758")

# Yandex Cloud CA Certificate (embedded)
YANDEX_CA_CERT = """-----BEGIN CERTIFICATE-----
MIIFGTCCAwGgAwIBAgIQJMM7ZIy2SYxCBgK7WcFwnjANBgkqhkiG9w0BAQ0FADAf
MR0wGwYDVQQDExRZYW5kZXhJbnRlcm5hbFJvb3RDQTAeFw0xMzAyMTExMzQxNDNa
Fw0zMzAyMTExMzUxNDJaMB8xHTAbBgNVBAMTFFlhbmRleEludGVybmFsUm9vdENB
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAgb4xoQjBQ7oEFk8EHVGy
1pDEmPWw0Wgw5nX9RM7LL2xQWyUuEq+Lf9Dgh+O725aZ9+SO2oEs47DHHt81/fne
5N6xOftRrCpy8hGtUR/A3bvjnQgjs+LXqedJnsvCmtY3cqHn3S0jqC7Jm0F5XnNR
dLBQ+TvT9FGGDZ6Ls3HgTuQyBu+cKe+Vbh65MVPN2YTNT7cvr+Yk59aEhTMeLWaE
M3PL+gVpefmvr/+b9dPMK8qzYNC0qJPxpbYHG+OPkSO3RY8Un9LZTMYR0l+zaZ9J
P6K1Vv7WJ/kTvIpSqEh7CZJJ3E3q5sZN7L2Ahy7v53xdhc8uKGDR4dPyT/G5m1U1
s3L2DYH4ydyW+lTXs2dU1N3rrGMIooxr0n3H3znjqGP8xvBAEr2K+zOMxPJn3r1J
rYn5tqB7R2Q2X1VjwTX4Wf+w1Gu89dXpJHf2w87d+BFh1Y7Pt3mveloLOVr1qLHH
Zn0EGjpK8cnQVAjjKN4HrP5x9D7c5LvlJVVE8uXLI2SQFj7cdNYz3L7rkC+ym7ab
Z3B+3f1M7o2gg0F0lE2xzUhH2xVq3G9Pz3SG38j3n8l5p5+kFw0+c0ltejdC9YK7
+kUFyhw/T9GQkZdMH7aV+evvPblvpbCijqhdjrafHJ3cLxsLqnR1JL0WJG9jsHxu
7TEQaFPQtR3V6g0UU5lJQckCAwEAAaNRME8wCwYDVR0PBAQDAgGGMA8GA1UdEwEB
/wQFMAMBAf8wHQYDVR0OBBYEFKu5xf+h7+ZTHTM5IoGEQ27jLgNuMBAGCSsGAQQB
gjcVAQQDAgEAMA0GCSqGSIb3DQEBDQUAA4ICAQAj8LnRX3pb5r3gfZgXeC1GZGvc
pB0d+gzBJghJL5oJN5Z4RdteNFoQsu85lEfCfWrQsOK46ygIMv/p7njlS0MKWr6w
GEFBOxVsQ1LxA3pC2JWfAQf+l1s6r3okOOzZZ0rAiYyXUPW/gzpJ6g1Xp9OE0LB7
NIMeJQI1oD4p4X8p6CVQJK25O5V67RGl/8TWTIJLqFl8M7FhM8q/FY8hIq6wRpLF
vPzYIzwfiC0lxGPDBs/g0RVbSUMH/bVL3xsV4IJTHJ/gK7x3yqOFR6vF9W7KZBXa
M2svLmd8M8r7Pky5X0t1j3eVs0FN0QXN3JBDdGvJkoyEBdM+sE/Z+8BpJqLKE8+V
u7rp2sN7UYM6pTQ4xy4T6cY0GFJwL+0ue+w0mYoEI0RL5+i8BhVQ0N6viLYEjt1G
aA/2e5VKFrWOPvPJl6FqB2DPH/YH/bmbDQd/JVAJ8oFzqzK03Hy7PDP8r6o1vkcd
VlaVb8kNFzYHfXg7qSf+w5i2m+G0K0uqjJNFhOJuaA+ISwSMN4RGJPV2WneHJOJM
Sq05efbHH8jY5G0X5gVjZbVvlrUSL7jSMCIJgL1+wVJqIxz0e3KBVoQ3TARC3WET
nZpSMALsA+EWZKwiU5bXdKs0SYqL+0bMB0RzTwUC8i7/JjTnI2T0JzG05FkLJKUh
FxPD5e8aeqOj2nFj9g==
-----END CERTIFICATE-----"""

# MongoDB connection (lazy init)
_client = None
_db = None
_ca_file = None

def get_db():
    global _client, _db, _ca_file
    if _db is None:
        # Создаём временный файл с CA сертификатом
        if _ca_file is None:
            _ca_file = tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False)
            _ca_file.write(YANDEX_CA_CERT)
            _ca_file.flush()
        
        _client = MongoClient(
            MONGO_URL,
            tls=True,
            tlsCAFile=_ca_file.name,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000
        )
        _db = _client.mapchap
    return _db

# ===================== UTILITIES =====================
def json_response(data, status_code=200):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        },
        'body': json.dumps(data, default=str)
    }

def serialize_doc(doc):
    if doc is None:
        return None
    doc = dict(doc)
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

# ===================== BOOST PLANS =====================
BOOST_PLANS = {
    "1day": {"days": 1, "name": "1 День", "price": 350, "currency": "XTR"},
    "5days": {"days": 5, "name": "5 Дней", "price": 1200, "currency": "XTR"},
    "7days": {"days": 7, "name": "7 Дней", "price": 1600, "currency": "XTR"}
}

# ===================== HANDLERS =====================

def handle_health(event, context):
    return json_response({"status": "ok", "version": "3.0.0", "service": "MapChap API"})

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
    return json_response({
        "name": "MapChap",
        "version": "3.0.0",
        "support": {"email": SUPPORT_EMAIL, "phone": SUPPORT_PHONE}
    })

def handle_telegram_auth(event, context):
    try:
        db = get_db()
        body = json.loads(event.get('body', '{}'))
        telegram_id = body.get('id')
        
        if not telegram_id:
            return json_response({"error": "telegram_id required"}, 400)
        
        existing = db.users.find_one({"telegram_id": telegram_id})
        
        if existing:
            db.users.update_one(
                {"telegram_id": telegram_id},
                {"$set": {
                    "first_name": body.get('first_name', ''),
                    "last_name": body.get('last_name', ''),
                    "username": body.get('username', ''),
                    "photo_url": body.get('photo_url', ''),
                    "last_login": datetime.now(timezone.utc)
                }}
            )
            user = db.users.find_one({"telegram_id": telegram_id})
        else:
            user_doc = {
                "id": str(uuid.uuid4()),
                "telegram_id": telegram_id,
                "first_name": body.get('first_name', ''),
                "last_name": body.get('last_name', ''),
                "username": body.get('username', ''),
                "photo_url": body.get('photo_url', ''),
                "role": "user",
                "is_verified": False,
                "favorites": [],
                "favorite_categories": [],
                "created_at": datetime.now(timezone.utc)
            }
            db.users.insert_one(user_doc)
            user = user_doc
        
        return json_response({"success": True, "user": serialize_doc(user)})
    except Exception as e:
        return json_response({"error": str(e), "type": "auth_error"}, 500)

def handle_get_user(event, context):
    try:
        db = get_db()
        params = event.get('params', {}).get('path', {})
        telegram_id = int(params.get('telegram_id', 0))
        
        user = db.users.find_one({"telegram_id": telegram_id})
        if not user:
            return json_response({"error": "User not found"}, 404)
        
        return json_response(serialize_doc(user))
    except Exception as e:
        return json_response({"error": str(e)}, 500)

def handle_update_user(event, context):
    try:
        db = get_db()
        params = event.get('params', {}).get('path', {})
        telegram_id = int(params.get('telegram_id', 0))
        body = json.loads(event.get('body', '{}'))
        
        result = db.users.update_one({"telegram_id": telegram_id}, {"$set": body})
        if result.modified_count == 0:
            return json_response({"error": "User not found"}, 404)
        
        user = db.users.find_one({"telegram_id": telegram_id})
        return json_response(serialize_doc(user))
    except Exception as e:
        return json_response({"error": str(e)}, 500)

def handle_get_offers(event, context):
    try:
        db = get_db()
        params = event.get('params', {}).get('query', {})
        
        query = {"status": "active"}
        category = params.get('category')
        if category and category != 'all':
            query['category'] = category
        
        search = params.get('search')
        if search:
            query['$or'] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        
        limit = int(params.get('limit', 50))
        skip = int(params.get('skip', 0))
        
        offers = list(db.offers.find(query).skip(skip).limit(limit))
        total = db.offers.count_documents(query)
        
        return json_response({
            "offers": [serialize_doc(o) for o in offers],
            "total": total
        })
    except Exception as e:
        return json_response({"error": str(e), "offers": [], "total": 0})

def handle_get_offer(event, context):
    try:
        db = get_db()
        params = event.get('params', {}).get('path', {})
        offer_id = params.get('offer_id')
        
        offer = db.offers.find_one({"id": offer_id})
        if not offer:
            return json_response({"error": "Offer not found"}, 404)
        
        return json_response(serialize_doc(offer))
    except Exception as e:
        return json_response({"error": str(e)}, 500)

def handle_create_offer(event, context):
    try:
        db = get_db()
        params = event.get('params', {}).get('query', {})
        telegram_id = int(params.get('telegram_id', 0))
        body = json.loads(event.get('body', '{}'))
        
        user = db.users.find_one({"telegram_id": telegram_id})
        if not user:
            return json_response({"error": "User not found"}, 404)
        if user.get('role') != 'business_owner':
            return json_response({"error": "Only business owners can create offers"}, 403)
        
        coords = body.get('coordinates', [55.75, 37.62])
        
        offer_doc = {
            "id": str(uuid.uuid4()),
            "user_id": telegram_id,
            "title": body.get('title'),
            "description": body.get('description'),
            "category": body.get('category'),
            "address": body.get('address'),
            "phone": body.get('phone'),
            "coordinates": {"type": "Point", "coordinates": [coords[1], coords[0]]},
            "images": body.get('images', []),
            "tags": body.get('tags', []),
            "status": "active",
            "views": 0,
            "likes": 0,
            "created_at": datetime.now(timezone.utc)
        }
        
        db.offers.insert_one(offer_doc)
        return json_response(serialize_doc(offer_doc))
    except Exception as e:
        return json_response({"error": str(e)}, 500)

def handle_user_offers(event, context):
    try:
        db = get_db()
        params = event.get('params', {}).get('path', {})
        telegram_id = int(params.get('telegram_id', 0))
        
        offers = list(db.offers.find({"user_id": telegram_id}))
        return json_response({"offers": [serialize_doc(o) for o in offers]})
    except Exception as e:
        return json_response({"error": str(e), "offers": []})

def handle_favorites(event, context):
    try:
        db = get_db()
        params = event.get('params', {}).get('path', {})
        telegram_id = int(params.get('telegram_id', 0))
        
        user = db.users.find_one({"telegram_id": telegram_id})
        if not user:
            return json_response({"error": "User not found"}, 404)
        
        favorites = []
        for offer_id in user.get('favorites', []):
            offer = db.offers.find_one({"id": offer_id})
            if offer:
                favorites.append(serialize_doc(offer))
        
        return json_response({"favorites": favorites})
    except Exception as e:
        return json_response({"error": str(e), "favorites": []})

def handle_update_favorites(event, context):
    try:
        db = get_db()
        params = event.get('params', {}).get('path', {})
        telegram_id = int(params.get('telegram_id', 0))
        body = json.loads(event.get('body', '{}'))
        offer_id = body.get('offer_id')
        
        user = db.users.find_one({"telegram_id": telegram_id})
        if not user:
            return json_response({"error": "User not found"}, 404)
        
        favorites = user.get('favorites', [])
        if offer_id in favorites:
            favorites.remove(offer_id)
            action = "removed"
        else:
            favorites.append(offer_id)
            action = "added"
        
        db.users.update_one({"telegram_id": telegram_id}, {"$set": {"favorites": favorites}})
        return json_response({"success": True, "action": action, "favorites": favorites})
    except Exception as e:
        return json_response({"error": str(e)}, 500)

def handle_boost_plans(event, context):
    plans = [
        {"id": k, "days": v["days"], "name": v["name"], "price": v["price"], "currency": v["currency"]}
        for k, v in BOOST_PLANS.items()
    ]
    return json_response({"plans": plans})

def handle_articles(event, context):
    try:
        db = get_db()
        params = event.get('params', {}).get('query', {})
        
        query = {"status": "published"}
        limit = int(params.get('limit', 20))
        
        articles = list(db.articles.find(query).sort("created_at", -1).limit(limit))
        return json_response({"articles": [serialize_doc(a) for a in articles], "total": len(articles)})
    except Exception as e:
        return json_response({"error": str(e), "articles": [], "total": 0})

def handle_verification_inn(event, context):
    try:
        db = get_db()
        params = event.get('params', {}).get('query', {})
        telegram_id = int(params.get('telegram_id', 0))
        body = json.loads(event.get('body', '{}'))
        inn = body.get('inn')
        
        if not DADATA_API_KEY:
            return json_response({"error": "DaData not configured"}, 500)
        
        with httpx.Client(timeout=10) as client:
            response = client.post(
                "https://suggestions.dadata.ru/suggestions/api/4_1/rs/findById/party",
                json={"query": inn},
                headers={
                    "Authorization": f"Token {DADATA_API_KEY}",
                    "Content-Type": "application/json"
                }
            )
            data = response.json()
            
            if data.get('suggestions'):
                company = data['suggestions'][0]
                db.users.update_one(
                    {"telegram_id": telegram_id},
                    {"$set": {
                        "role": "business_owner",
                        "is_verified": True,
                        "verification_type": "inn",
                        "inn": inn,
                        "company_name": company['value']
                    }}
                )
                return json_response({"success": True, "company_name": company['value']})
            else:
                return json_response({"error": "ИНН не найден"}, 400)
    except Exception as e:
        return json_response({"error": str(e)}, 500)

def handle_verification_manual(event, context):
    try:
        db = get_db()
        params = event.get('params', {}).get('query', {})
        telegram_id = int(params.get('telegram_id', 0))
        body = json.loads(event.get('body', '{}'))
        
        db.users.update_one(
            {"telegram_id": telegram_id},
            {"$set": {
                "role": "business_owner",
                "is_verified": True,
                "verification_type": "manual",
                "phone": body.get('phone'),
                "email": body.get('email'),
                "company_name": body.get('company_name')
            }}
        )
        return json_response({"success": True, "message": "Бизнес-аккаунт активирован"})
    except Exception as e:
        return json_response({"error": str(e)}, 500)

# ===================== MAIN HANDLER =====================
def handler(event, context):
    method = event.get('httpMethod', 'GET')
    if method == 'OPTIONS':
        return json_response({})
    
    path = event.get('path', '/')
    
    if path.startswith('/api'):
        path = path[4:]
    
    routes = {
        ('GET', '/health'): handle_health,
        ('GET', '/categories'): handle_categories,
        ('GET', '/app-info'): handle_app_info,
        ('POST', '/auth/telegram'): handle_telegram_auth,
        ('GET', '/offers'): handle_get_offers,
        ('POST', '/offers'): handle_create_offer,
        ('GET', '/articles'): handle_articles,
        ('GET', '/boosts/plans'): handle_boost_plans,
        ('POST', '/verification/inn'): handle_verification_inn,
        ('POST', '/verification/manual'): handle_verification_manual,
    }
    
    route_key = (method, path)
    if route_key in routes:
        return routes[route_key](event, context)
    
    if path.startswith('/users/') and '/favorites' in path:
        telegram_id = path.split('/')[2]
        event.setdefault('params', {}).setdefault('path', {})['telegram_id'] = telegram_id
        if method == 'GET':
            return handle_favorites(event, context)
        elif method == 'PUT':
            return handle_update_favorites(event, context)
    
    if path.startswith('/users/'):
        parts = path.split('/')
        if len(parts) >= 3:
            telegram_id = parts[2]
            event.setdefault('params', {}).setdefault('path', {})['telegram_id'] = telegram_id
            if method == 'GET':
                return handle_get_user(event, context)
            elif method == 'PUT':
                return handle_update_user(event, context)
    
    if path.startswith('/offers/user/'):
        telegram_id = path.split('/')[3]
        event.setdefault('params', {}).setdefault('path', {})['telegram_id'] = telegram_id
        return handle_user_offers(event, context)
    
    if path.startswith('/offers/'):
        offer_id = path.split('/')[2]
        event.setdefault('params', {}).setdefault('path', {})['offer_id'] = offer_id
        return handle_get_offer(event, context)
    
    return json_response({"error": f"Route not found: {method} {path}"}, 404)
