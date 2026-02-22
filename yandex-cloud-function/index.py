import os
import uuid
import json
from datetime import datetime, timezone
import tempfile
import ssl

from pymongo import MongoClient
import httpx

MONGO_URL = os.environ.get("MONGO_URL", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
DADATA_API_KEY = os.environ.get("DADATA_API_KEY", "")
SUPPORT_EMAIL = "khabibullaevakhrorjon@gmail.com"
SUPPORT_PHONE = "+79998214758"

# Yandex Cloud CA Certificate
YANDEX_CA_CERT = """-----BEGIN CERTIFICATE-----
MIIE3TCCAsWgAwIBAgIKPxb5sAAAAAAAFzANBgkqhkiG9w0BAQ0FADAfMR0wGwYD
VQQDExRZYW5kZXhJbnRlcm5hbFJvb3RDQTAeFw0xNzA2MjAxNjQ0MzdaFw0yNzA2
MjAxNjU0MzdaMFUxEjAQBgoJkiaJk/IsZAEZFgJydTEWMBQGCgmSJomT8ixkARkW
BnlhbmRleDESMBAGCgmSJomT8ixkARkWAmxkMRMwEQYDVQQDEwpZYW5kZXhDTENB
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqgNnjk0JKPcbsk1+KG2t
eM1AfMnEe5RkAJuBBuwVV49snhcvO1jhKBx/pCnjr6biICc1/oAFDVgU8yVYYPwp
WZ2vH3ZtscjJ/RAT/NS9OKKG7kKknhFhVYxua5xhoIQmm6usBNYYiTcWoFm1eHC8
I9oddOLSscZYbh3unVRvt+3V+drVmUx9oSUKpqMgfysiv1MN6zB3vq9TFkbhz53E
k0tEcV+W2NnDaeFhLKy284FDKLvOdTDj1EDsSAihxl7sNEKpupNuhgyy2siOqUb+
d5mO/CRfaAKGg3E6hDM3pEi48E506dJdjPXWfHKSvuguMLRlb2RWdVocRZuyWxOh
0QIDAQABo4HkMIHhMBAGCSsGAQQBgjcVAQQDAgEAMB0GA1UdDgQWBBRMU5uItjx+
TOicX1+ovC1Xq2PSnzAZBgkrBgEEAYI3FAIEDB4KAFMAdQBiAEMAQTALBgNVHQ8E
BAMCAYYwDwYDVR0TAQH/BAUwAwEB/zAfBgNVHSMEGDAWgBSrucX/oe/mUx0zOSKE
0XbUN04tajBUBgNVHR8ETTBLMEmgR6BFhkNodHRwOi8vY3Jscy55YW5kZXgucnUv
WWFuZGV4SW50ZXJuYWxSb290Q0EvWWFuZGV4SW50ZXJuYWxSb290Q0EuY3JsMA0G
CSqGSIb3DQEBDQUAA4ICAQAsR5Lb4Pv2FD0Kk+4oc1GEOnehxKLsQtdV81nrU+IV
l9pr2oNMdi8lwIolvHZRllLM4Ba5AcRH6YJ5fe7AjKm+5EdSkhqVWo2UOllRCbtS
wmL50+erOAkxstSlRkO6b8x1L0MOBKv54E5YcQ/Wwt27ldSb6RkEmJBGvmxObAaf
5zc51pqSqao9tnldYaCblEQ/Zmy43FliIpa2eUJoh8DqK8bVo2gcI3wbQ32tWs9u
wvKk8fo4lAdhCwhv+QHuqau1VAY9hPU106bsFIDUmijTMxjAobKBi6CkIX6EbNHU
Jv4DzYVLlDd2y0CADdn2F6I70xpCBn5cquSGuvFbqZjQDmIHwb7WQSxadkiGRWfc
zVTnmiHjJONJJIpE2t+FOV3hc+8o98OzOtNaH2QQ9j6dnKvtIGKGFeNSDp0vXPOi
QhHiIyuB7eWx+g2whktQ74UCpGDSXYnEW3s8w5wezVWIEmouq7q4rCEkTNvJ7Ico
43AgUdPzAFS2zYktw1C+cbUALM8smvXbXrXOBzMmscjIhtXvLMrpPeh23VfdJfQB
0rN2BmRCLUE8JOV+o0k98XMm83oN+lGkL1l+hyoj3ok1uI3JrsWOcDyjOds3ptcN
KimJLm27ndjcxDNo/iA6gefMJuCxFRaqI+eF4P0jSkMgnnQqZkvLGFuHCw8eRDhm
bw==
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
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

_client = None
_db = None
_ca_file = None

def get_db():
    global _client, _db, _ca_file
    if _db is None:
        if _ca_file is None:
            _ca_file = tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False)
            _ca_file.write(YANDEX_CA_CERT)
            _ca_file.flush()
        
        # Пробуем с разными настройками TLS
        try:
            _client = MongoClient(
                MONGO_URL,
                tls=True,
                tlsCAFile=_ca_file.name,
                tlsAllowInvalidCertificates=False,
                serverSelectionTimeoutMS=30000,
                connectTimeoutMS=30000,
                socketTimeoutMS=30000,
                directConnection=True
            )
            _db = _client.mapchap
            # Проверяем подключение
            _db.command('ping')
        except Exception as e:
            # Если не удалось, пробуем без проверки сертификата
            _client = MongoClient(
                MONGO_URL,
                tls=True,
                tlsAllowInvalidCertificates=True,
                serverSelectionTimeoutMS=30000,
                connectTimeoutMS=30000
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

def get_query_params(event):
    return event.get('queryStringParameters', {}) or {}

BOOST_PLANS = {
    "1day": {"days": 1, "name": "1 День", "price": 350, "currency": "XTR"},
    "5days": {"days": 5, "name": "5 Дней", "price": 1200, "currency": "XTR"},
    "7days": {"days": 7, "name": "7 Дней", "price": 1600, "currency": "XTR"}
}

def handle_health(event, context):
    return json_response({"status": "ok", "version": "3.0.0", "service": "MapChap API"})

def handle_db_test(event, context):
    """Test MongoDB connection"""
    try:
        db = get_db()
        db.command('ping')
        count = db.users.count_documents({})
        return json_response({"status": "connected", "users_count": count})
    except Exception as e:
        return json_response({"status": "error", "error": str(e), "mongo_url": MONGO_URL[:50]+"..."}, 500)

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
        params = get_query_params(event)
        query = {"status": "active"}
        if params.get('category') and params['category'] != 'all':
            query['category'] = params['category']
        offers = list(db.offers.find(query).limit(int(params.get('limit', 50))))
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
