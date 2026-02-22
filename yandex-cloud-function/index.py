import os
import uuid
import json
import math
from datetime import datetime, timezone, timedelta
import httpx

from pymongo import MongoClient

MONGO_URL = os.environ.get("MONGO_URL", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
SUPPORT_EMAIL = "khabibullaevakhrorjon@gmail.com"
SUPPORT_PHONE = "+79998214758"

_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
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

def get_query_params(event):
    return event.get('queryStringParameters', {}) or {}

# ==================== TELEGRAM BOT FUNCTIONS ====================

def send_telegram_message(chat_id, text, parse_mode="HTML", reply_markup=None):
    """Отправка сообщения через Telegram Bot API"""
    if not TELEGRAM_BOT_TOKEN:
        print("⚠️ TELEGRAM_BOT_TOKEN not configured")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    
    try:
        with httpx.Client(timeout=10) as client:
            response = client.post(url, json=payload)
            result = response.json()
            if not result.get("ok"):
                print(f"❌ Telegram error: {result}")
            return result.get("ok", False)
    except Exception as e:
        print(f"❌ Send message error: {e}")
        return False

def notify_new_view(offer_id, viewer_telegram_id=None):
    """Уведомление владельцу о новом просмотре"""
    try:
        db = get_db()
        offer = db.offers.find_one({"id": offer_id})
        if not offer:
            return
        
        owner = db.users.find_one({"telegram_id": offer.get("user_id")})
        if not owner or not owner.get("notifications_enabled", True):
            return
        
        # Проверяем, не отправляли ли уведомление недавно (раз в час)
        last_notify = db.notifications.find_one({
            "offer_id": offer_id,
            "type": "view",
            "created_at": {"$gte": datetime.now(timezone.utc) - timedelta(hours=1)}
        })
        if last_notify:
            return
        
        # Формируем сообщение
        text = f"""
👁 <b>Новый просмотр!</b>

Ваше объявление «{offer.get('title')}» просмотрели.

📊 Всего просмотров: {offer.get('views', 0) + 1}
❤️ В избранном: {offer.get('likes', 0)}

<i>Хотите больше просмотров? Попробуйте буст!</i>
"""
        
        # Кнопка для открытия аналитики
        reply_markup = {
            "inline_keyboard": [[
                {"text": "📊 Аналитика", "web_app": {"url": f"https://mapchap-frontend.website.yandexcloud.net/analytics"}},
                {"text": "⚡ Буст", "callback_data": f"boost_{offer_id}"}
            ]]
        }
        
        send_telegram_message(owner["telegram_id"], text, reply_markup=reply_markup)
        
        # Сохраняем уведомление
        db.notifications.insert_one({
            "id": str(uuid.uuid4()),
            "offer_id": offer_id,
            "user_id": owner["telegram_id"],
            "type": "view",
            "created_at": datetime.now(timezone.utc)
        })
    except Exception as e:
        print(f"❌ notify_new_view error: {e}")

def notify_new_favorite(offer_id, fan_telegram_id):
    """Уведомление владельцу когда объявление добавили в избранное"""
    try:
        db = get_db()
        offer = db.offers.find_one({"id": offer_id})
        if not offer:
            return
        
        owner = db.users.find_one({"telegram_id": offer.get("user_id")})
        if not owner or not owner.get("notifications_enabled", True):
            return
        
        fan = db.users.find_one({"telegram_id": fan_telegram_id})
        fan_name = fan.get("first_name", "Кто-то") if fan else "Кто-то"
        
        text = f"""
❤️ <b>Новое добавление в избранное!</b>

<b>{fan_name}</b> добавил(а) «{offer.get('title')}» в избранное!

📊 Всего в избранном: {offer.get('likes', 0) + 1}
"""
        
        send_telegram_message(owner["telegram_id"], text)
    except Exception as e:
        print(f"❌ notify_new_favorite error: {e}")

def notify_boost_activated(offer_id, boost_type, expires_at):
    """Уведомление об активации буста"""
    try:
        db = get_db()
        offer = db.offers.find_one({"id": offer_id})
        if not offer:
            return
        
        owner = db.users.find_one({"telegram_id": offer.get("user_id")})
        if not owner:
            return
        
        plan = BOOST_PLANS.get(boost_type, BOOST_PLANS["1day"])
        exp_date = expires_at.strftime("%d.%m.%Y") if isinstance(expires_at, datetime) else str(expires_at)
        
        text = f"""
⚡ <b>Буст активирован!</b>

Объявление «{offer.get('title')}» теперь продвигается!

📅 Тариф: {plan['name']}
⏰ Действует до: {exp_date}

Ваше объявление теперь показывается чаще и выше в поиске!
"""
        
        send_telegram_message(owner["telegram_id"], text)
    except Exception as e:
        print(f"❌ notify_boost_activated error: {e}")

def notify_boost_expiring(offer_id, hours_left):
    """Уведомление о скором истечении буста"""
    try:
        db = get_db()
        offer = db.offers.find_one({"id": offer_id})
        if not offer:
            return
        
        owner = db.users.find_one({"telegram_id": offer.get("user_id")})
        if not owner or not owner.get("notifications_enabled", True):
            return
        
        text = f"""
⏰ <b>Буст скоро истечёт!</b>

Буст для «{offer.get('title')}» закончится через {hours_left} ч.

Продлите буст, чтобы не потерять позиции в поиске!
"""
        
        reply_markup = {
            "inline_keyboard": [[
                {"text": "🔄 Продлить буст", "callback_data": f"extend_boost_{offer_id}"}
            ]]
        }
        
        send_telegram_message(owner["telegram_id"], text, reply_markup=reply_markup)
    except Exception as e:
        print(f"❌ notify_boost_expiring error: {e}")

BOOST_PLANS = {
    "1day": {"days": 1, "name": "1 День", "price": 350, "currency": "XTR"},
    "5days": {"days": 5, "name": "5 Дней", "price": 1200, "currency": "XTR"},
    "7days": {"days": 7, "name": "7 Дней", "price": 1600, "currency": "XTR"}
}

CATEGORIES = [
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

# ==================== BASIC HANDLERS ====================

def handle_health(event, context):
    return json_response({"status": "ok", "version": "3.0.0", "service": "MapChap API (Yandex Cloud)"})

def handle_db_test(event, context):
    try:
        db = get_db()
        db.command('ping')
        count = db.users.count_documents({})
        return json_response({"status": "connected", "users_count": count})
    except Exception as e:
        return json_response({"status": "error", "error": str(e)}, 500)

def handle_categories(event, context):
    return json_response({"categories": CATEGORIES})

def handle_app_info(event, context):
    return json_response({"name": "MapChap", "version": "3.0.0", "support": {"email": SUPPORT_EMAIL, "phone": SUPPORT_PHONE}})

# ==================== AUTH ====================

def handle_telegram_auth(event, context):
    try:
        db = get_db()
        body = json.loads(event.get('body', '{}'))
        telegram_id = body.get('id')
        if not telegram_id:
            return json_response({"error": "telegram_id required"}, 400)
        
        existing = db.users.find_one({"telegram_id": telegram_id})
        if existing:
            db.users.update_one({"telegram_id": telegram_id}, {"$set": {
                "first_name": body.get('first_name', ''),
                "last_name": body.get('last_name', ''),
                "username": body.get('username', ''),
                "photo_url": body.get('photo_url', ''),
                "last_login": datetime.now(timezone.utc)
            }})
            user = db.users.find_one({"telegram_id": telegram_id})
        else:
            user = {
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
            db.users.insert_one(user)
        return json_response({"success": True, "user": serialize_doc(user)})
    except Exception as e:
        return json_response({"error": str(e)}, 500)

# ==================== USERS ====================

def handle_get_user(event, context, telegram_id):
    try:
        db = get_db()
        user = db.users.find_one({"telegram_id": int(telegram_id)})
        return json_response(serialize_doc(user)) if user else json_response({"error": "User not found"}, 404)
    except Exception as e:
        return json_response({"error": str(e)}, 500)

def handle_update_user(event, context, telegram_id):
    try:
        db = get_db()
        body = json.loads(event.get('body', '{}'))
        allowed = ['first_name', 'last_name', 'phone', 'email', 'favorite_categories', 'notification_radius']
        update_data = {k: v for k, v in body.items() if k in allowed}
        db.users.update_one({"telegram_id": int(telegram_id)}, {"$set": update_data})
        user = db.users.find_one({"telegram_id": int(telegram_id)})
        return json_response(serialize_doc(user))
    except Exception as e:
        return json_response({"error": str(e)}, 500)

# ==================== FAVORITES ====================

def handle_get_favorites(event, context, telegram_id):
    try:
        db = get_db()
        user = db.users.find_one({"telegram_id": int(telegram_id)})
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

def handle_update_favorites(event, context, telegram_id):
    try:
        db = get_db()
        body = json.loads(event.get('body', '{}'))
        offer_id = body.get('offer_id')
        
        user = db.users.find_one({"telegram_id": int(telegram_id)})
        if not user:
            return json_response({"error": "User not found"}, 404)
        
        favorites = user.get('favorites', [])
        if offer_id in favorites:
            favorites.remove(offer_id)
            action = "removed"
        else:
            favorites.append(offer_id)
            action = "added"
        
        db.users.update_one({"telegram_id": int(telegram_id)}, {"$set": {"favorites": favorites}})
        return json_response({"success": True, "action": action, "favorites": favorites})
    except Exception as e:
        return json_response({"error": str(e)}, 500)

# ==================== VERIFICATION ====================

def handle_verification_inn(event, context):
    try:
        db = get_db()
        params = get_query_params(event)
        telegram_id = int(params.get('telegram_id', 0))
        body = json.loads(event.get('body', '{}'))
        inn = body.get('inn')
        
        # Валидация ИНН
        if not inn or not inn.isdigit():
            return json_response({"error": "Неверный формат ИНН"}, 400)
        if len(inn) not in [9, 10, 12]:
            return json_response({"error": "ИНН должен содержать 9, 10 или 12 цифр"}, 400)
        
        # Если есть DaData - используем его
        if DADATA_API_KEY:
            try:
                with httpx.Client(timeout=10) as client:
                    response = client.post(
                        "https://suggestions.dadata.ru/suggestions/api/4_1/rs/findById/party",
                        json={"query": inn},
                        headers={"Authorization": f"Token {DADATA_API_KEY}", "Content-Type": "application/json"}
                    )
                    data = response.json()
                    
                    if data.get('suggestions'):
                        company = data['suggestions'][0]
                        company_data = company.get('data', {})
                        
                        db.users.update_one({"telegram_id": telegram_id}, {"$set": {
                            "role": "business_owner",
                            "is_verified": True,
                            "verification_type": "inn",
                            "inn": inn,
                            "company_name": company['value']
                        }})
                        
                        return json_response({
                            "success": True, 
                            "verification": {
                                "inn": inn,
                                "name": company['value'],
                                "address": company_data.get('address', {}).get('value'),
                                "status": company_data.get('state', {}).get('status')
                            }
                        })
            except Exception as e:
                print(f"DaData error: {e}")
        
        # Fallback: простая верификация без DaData
        # Обновляем пользователя как бизнес-владельца
        db.users.update_one({"telegram_id": telegram_id}, {"$set": {
            "role": "business_owner",
            "is_verified": True,
            "verification_type": "inn",
            "inn": inn,
            "company_name": f"Бизнес ИНН {inn}"
        }})
        
        return json_response({
            "success": True, 
            "verification": {
                "inn": inn,
                "name": f"Бизнес ИНН {inn}",
                "address": None,
                "status": "ACTIVE"
            },
            "message": "Верификация пройдена (упрощённая)"
        })
    except Exception as e:
        return json_response({"error": str(e)}, 500)

def handle_verification_manual(event, context):
    try:
        db = get_db()
        params = get_query_params(event)
        telegram_id = int(params.get('telegram_id', 0))
        body = json.loads(event.get('body', '{}'))
        
        db.users.update_one({"telegram_id": telegram_id}, {"$set": {
            "role": "business_owner",
            "is_verified": True,
            "verification_type": "manual",
            "phone": body.get('phone'),
            "email": body.get('email'),
            "company_name": body.get('company_name')
        }})
        return json_response({"success": True, "message": "Бизнес-аккаунт активирован"})
    except Exception as e:
        return json_response({"error": str(e)}, 500)

# ==================== OFFERS ====================

def handle_get_offers(event, context):
    try:
        db = get_db()
        params = get_query_params(event)
        
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
        return json_response({"offers": [serialize_doc(o) for o in offers], "total": total})
    except Exception as e:
        return json_response({"error": str(e), "offers": [], "total": 0})

def handle_get_offer(event, context, offer_id):
    try:
        db = get_db()
        params = get_query_params(event)
        viewer_id = params.get('telegram_id')
        
        offer = db.offers.find_one({"id": offer_id})
        if not offer:
            return json_response({"error": "Offer not found"}, 404)
        
        # Increment views
        db.offers.update_one({"id": offer_id}, {"$inc": {"views": 1}})
        
        # Отправляем push-уведомление владельцу (асинхронно, не блокируем ответ)
        try:
            notify_new_view(offer_id, int(viewer_id) if viewer_id else None)
        except:
            pass
        
        return json_response(serialize_doc(offer))
    except Exception as e:
        return json_response({"error": str(e)}, 500)

def handle_create_offer(event, context):
    try:
        db = get_db()
        params = get_query_params(event)
        telegram_id = int(params.get('telegram_id', 0))
        body = json.loads(event.get('body', '{}'))
        
        user = db.users.find_one({"telegram_id": telegram_id})
        if not user:
            return json_response({"error": "User not found"}, 404)
        if user.get('role') != 'business_owner':
            return json_response({"error": "Only business owners can create offers"}, 403)
        
        # Координаты могут прийти как [lat, lng] или как объект
        coords = body.get('coordinates', [55.75, 37.62])
        if isinstance(coords, list) and len(coords) >= 2:
            lat, lng = coords[0], coords[1]
        else:
            lat, lng = 55.75, 37.62
        
        # Дополнительные поля
        full_description = body.get('full_description', '')
        email = body.get('email', '')
        website = body.get('website', '')
        working_hours = body.get('working_hours', '')
        
        offer = {
            "id": str(uuid.uuid4()),
            "user_id": telegram_id,
            "title": body.get('title'),
            "description": body.get('description'),
            "full_description": full_description,
            "category": body.get('category'),
            "address": body.get('address'),
            "phone": body.get('phone'),
            "email": email,
            "website": website,
            "working_hours": working_hours,
            "coordinates": [lat, lng],  # Храним как простой массив [lat, lng]
            "images": body.get('images', []),
            "tags": body.get('tags', []),
            "amenities": body.get('amenities', []),
            "status": "active",
            "views": 0,
            "likes": 0,
            "created_at": datetime.now(timezone.utc)
        }
        
        db.offers.insert_one(offer)
        return json_response(serialize_doc(offer))
    except Exception as e:
        return json_response({"error": str(e)}, 500)

def handle_update_offer(event, context, offer_id):
    try:
        db = get_db()
        params = get_query_params(event)
        telegram_id = int(params.get('telegram_id', 0))
        body = json.loads(event.get('body', '{}'))
        
        offer = db.offers.find_one({"id": offer_id})
        if not offer:
            return json_response({"error": "Offer not found"}, 404)
        if offer.get('user_id') != telegram_id:
            return json_response({"error": "Not authorized"}, 403)
        
        allowed = ['title', 'description', 'category', 'address', 'phone', 'images', 'tags', 'amenities', 'status']
        update_data = {k: v for k, v in body.items() if k in allowed}
        update_data['updated_at'] = datetime.now(timezone.utc)
        
        db.offers.update_one({"id": offer_id}, {"$set": update_data})
        updated = db.offers.find_one({"id": offer_id})
        return json_response(serialize_doc(updated))
    except Exception as e:
        return json_response({"error": str(e)}, 500)

def handle_delete_offer(event, context, offer_id):
    try:
        db = get_db()
        params = get_query_params(event)
        telegram_id = int(params.get('telegram_id', 0))
        
        offer = db.offers.find_one({"id": offer_id})
        if not offer:
            return json_response({"error": "Offer not found"}, 404)
        if offer.get('user_id') != telegram_id:
            return json_response({"error": "Not authorized"}, 403)
        
        db.offers.delete_one({"id": offer_id})
        return json_response({"success": True, "message": "Offer deleted"})
    except Exception as e:
        return json_response({"error": str(e)}, 500)

def handle_user_offers(event, context, telegram_id):
    try:
        db = get_db()
        offers = list(db.offers.find({"user_id": int(telegram_id)}))
        return json_response({"offers": [serialize_doc(o) for o in offers]})
    except Exception as e:
        return json_response({"error": str(e), "offers": []})

# ==================== BOOSTS ====================

def handle_boost_plans(event, context):
    plans = [{"id": k, **v} for k, v in BOOST_PLANS.items()]
    return json_response({"plans": plans})

def handle_create_boost(event, context, offer_id):
    try:
        db = get_db()
        params = get_query_params(event)
        telegram_id = int(params.get('telegram_id', 0))
        body = json.loads(event.get('body', '{}'))
        
        offer = db.offers.find_one({"id": offer_id})
        if not offer or offer.get('user_id') != telegram_id:
            return json_response({"error": "Offer not found or not authorized"}, 403)
        
        boost_type = body.get('boost_type', '1day')
        plan = BOOST_PLANS.get(boost_type, BOOST_PLANS['1day'])
        
        now = datetime.now(timezone.utc)
        boost = {
            "id": str(uuid.uuid4()),
            "offer_id": offer_id,
            "user_id": telegram_id,
            "boost_type": boost_type,
            "price": plan['price'],
            "currency": plan['currency'],
            "status": "active",
            "created_at": now,
            "expires_at": now + timedelta(days=plan['days'])
        }
        
        db.boosts.insert_one(boost)
        return json_response({"success": True, "boost": serialize_doc(boost)})
    except Exception as e:
        return json_response({"error": str(e)}, 500)

# ==================== ARTICLES ====================

def handle_articles(event, context):
    try:
        db = get_db()
        articles = list(db.articles.find({"status": "published"}).sort("created_at", -1).limit(20))
        return json_response({"articles": [serialize_doc(a) for a in articles], "total": len(articles)})
    except Exception as e:
        return json_response({"error": str(e), "articles": [], "total": 0})

# ==================== ANALYTICS ====================

def handle_analytics_dashboard(event, context, telegram_id):
    try:
        db = get_db()
        params = get_query_params(event)
        period = params.get('period', '30d')
        
        user = db.users.find_one({"telegram_id": int(telegram_id)})
        if not user or user.get('role') != 'business_owner':
            return json_response({"error": "Only for business owners"}, 403)
        
        now = datetime.now(timezone.utc)
        days = {'7d': 7, '30d': 30, '90d': 90}.get(period, 30)
        start_date = now - timedelta(days=days)
        
        offers = list(db.offers.find({"user_id": int(telegram_id)}))
        offer_ids = [o["id"] for o in offers]
        
        total_views = db.view_history.count_documents({
            "offer_id": {"$in": offer_ids},
            "viewed_at": {"$gte": start_date}
        })
        
        prev_start = start_date - timedelta(days=days)
        prev_views = db.view_history.count_documents({
            "offer_id": {"$in": offer_ids},
            "viewed_at": {"$gte": prev_start, "$lt": start_date}
        })
        
        trend = round(((total_views - prev_views) / prev_views * 100), 1) if prev_views > 0 else (100 if total_views > 0 else 0)
        
        active_boosts = db.boosts.count_documents({
            "user_id": int(telegram_id),
            "status": "active",
            "expires_at": {"$gt": now}
        })
        
        offers_analytics = []
        for offer in offers:
            views = db.view_history.count_documents({"offer_id": offer["id"], "viewed_at": {"$gte": start_date}})
            boost = db.boosts.find_one({"offer_id": offer["id"], "status": "active", "expires_at": {"$gt": now}})
            offers_analytics.append({
                "id": offer["id"],
                "title": offer.get("title"),
                "views": views,
                "has_boost": boost is not None,
                "status": offer.get("status")
            })
        
        offers_analytics.sort(key=lambda x: x["views"], reverse=True)
        
        return json_response({
            "period": period,
            "summary": {
                "total_offers": len(offers),
                "active_offers": len([o for o in offers if o.get("status") == "active"]),
                "total_views": total_views,
                "trend_percent": trend,
                "trend_direction": "up" if trend > 0 else "down" if trend < 0 else "stable",
                "active_boosts": active_boosts
            },
            "offers": offers_analytics,
            "top_performers": offers_analytics[:3],
            "need_attention": [o for o in offers_analytics if o["views"] < 5][:3]
        })
    except Exception as e:
        return json_response({"error": str(e)}, 500)

def handle_analytics_offer(event, context, offer_id):
    try:
        db = get_db()
        params = get_query_params(event)
        telegram_id = int(params.get('telegram_id', 0))
        period = params.get('period', '30d')
        
        offer = db.offers.find_one({"id": offer_id})
        if not offer or offer.get("user_id") != telegram_id:
            return json_response({"error": "Not found or not authorized"}, 403)
        
        now = datetime.now(timezone.utc)
        days = {'7d': 7, '30d': 30, '90d': 90}.get(period, 30)
        start_date = now - timedelta(days=days)
        
        views = list(db.view_history.find({"offer_id": offer_id, "viewed_at": {"$gte": start_date}}))
        total_views = len(views)
        unique_visitors = len(set(v.get("user_id") for v in views))
        
        views_by_hour = {str(i): 0 for i in range(24)}
        for v in views:
            h = str(v["viewed_at"].hour)
            views_by_hour[h] = views_by_hour.get(h, 0) + 1
        
        peak_hour = max(views_by_hour, key=views_by_hour.get) if views_by_hour else "12"
        
        boost = db.boosts.find_one({"offer_id": offer_id, "status": "active", "expires_at": {"$gt": now}})
        
        return json_response({
            "offer_id": offer_id,
            "offer_title": offer.get("title"),
            "summary": {
                "total_views": total_views,
                "unique_visitors": unique_visitors,
                "avg_views_per_day": round(total_views / max(days, 1), 1),
                "peak_hour": f"{peak_hour}:00"
            },
            "charts": {
                "views_by_hour": [{"hour": f"{k}:00", "views": v} for k, v in sorted(views_by_hour.items(), key=lambda x: int(x[0]))]
            },
            "boost": {"active": boost is not None, "expires_at": boost.get("expires_at") if boost else None}
        })
    except Exception as e:
        return json_response({"error": str(e)}, 500)

# ==================== TELEGRAM WEBHOOK ====================

def handle_telegram_webhook(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        
        # Handle Telegram updates
        message = body.get('message', {})
        callback_query = body.get('callback_query', {})
        
        if message:
            chat_id = message.get('chat', {}).get('id')
            text = message.get('text', '')
            
            if text == '/start':
                send_telegram_message(chat_id, "Добро пожаловать в MapChap! 🗺️\n\nОткройте приложение через кнопку ниже:", {
                    "inline_keyboard": [[{
                        "text": "🚀 Открыть MapChap",
                        "web_app": {"url": "https://mapchap.ru"}
                    }]]
                })
            elif text == '/help':
                send_telegram_message(chat_id, "MapChap - платформа для поиска бизнесов рядом с вами!\n\n/start - Открыть приложение\n/help - Помощь")
        
        return json_response({"ok": True})
    except Exception as e:
        return json_response({"error": str(e)}, 500)

def send_telegram_message(chat_id, text, reply_markup=None):
    try:
        data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        if reply_markup:
            data["reply_markup"] = reply_markup
        
        with httpx.Client(timeout=10) as client:
            client.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json=data
            )
    except:
        pass

# ==================== MAIN HANDLER ====================

def get_path_param(event, param_name):
    """Extract path parameter from API Gateway event"""
    # Try pathParameters first (API Gateway sends params here)
    path_params = event.get('pathParameters', {}) or {}
    if param_name in path_params:
        return path_params[param_name]
    
    # Fallback: extract from path
    path = event.get('path', '/')
    if path.startswith('/api'):
        path = path[4:]
    parts = path.strip('/').split('/')
    
    # Map param names to their positions
    if param_name == 'telegram_id':
        if 'users' in parts:
            idx = parts.index('users')
            if idx + 1 < len(parts) and parts[idx + 1] != 'favorites':
                return parts[idx + 1]
            elif idx + 1 < len(parts):
                return parts[idx + 1]
        if 'dashboard' in parts:
            idx = parts.index('dashboard')
            if idx + 1 < len(parts):
                return parts[idx + 1]
        if 'user' in parts:
            idx = parts.index('user')
            if idx + 1 < len(parts):
                return parts[idx + 1]
    
    if param_name == 'offer_id':
        if 'offer' in parts:
            idx = parts.index('offer')
            if idx + 1 < len(parts):
                return parts[idx + 1]
        if 'offers' in parts:
            idx = parts.index('offers')
            if idx + 1 < len(parts) and parts[idx + 1] not in ['user']:
                return parts[idx + 1]
    
    return None

def handler(event, context):
    method = event.get('httpMethod', 'GET')
    if method == 'OPTIONS':
        return json_response({})
    
    path = event.get('path', '/')
    if path.startswith('/api'):
        path = path[4:]
    
    # Log for debugging
    print(f"Request: {method} {path}")
    print(f"Path params: {event.get('pathParameters', {})}")
    
    # Static routes
    routes = {
        ('GET', '/health'): handle_health,
        ('GET', '/db-test'): handle_db_test,
        ('GET', '/categories'): handle_categories,
        ('GET', '/app-info'): handle_app_info,
        ('POST', '/auth/telegram'): handle_telegram_auth,
        ('GET', '/offers'): handle_get_offers,
        ('POST', '/offers'): handle_create_offer,
        ('GET', '/articles'): handle_articles,
        ('GET', '/boosts/plans'): handle_boost_plans,
        ('POST', '/verification/inn'): handle_verification_inn,
        ('POST', '/verification/manual'): handle_verification_manual,
        ('POST', '/telegram/webhook'): handle_telegram_webhook,
    }
    
    if (method, path) in routes:
        return routes[(method, path)](event, context)
    
    # Dynamic routes - get parameters
    telegram_id = get_path_param(event, 'telegram_id')
    offer_id = get_path_param(event, 'offer_id')
    
    # Normalize path for matching (replace actual values with placeholders)
    normalized_path = path
    if telegram_id and telegram_id in path:
        normalized_path = path.replace(telegram_id, '{telegram_id}')
    if offer_id and offer_id in path:
        normalized_path = normalized_path.replace(offer_id, '{offer_id}')
    
    parts = normalized_path.strip('/').split('/')
    
    # /analytics/dashboard/{telegram_id}
    if len(parts) == 3 and parts[0] == 'analytics' and parts[1] == 'dashboard':
        tid = telegram_id or parts[2]
        return handle_analytics_dashboard(event, context, tid)
    
    # /analytics/offer/{offer_id}
    if len(parts) == 3 and parts[0] == 'analytics' and parts[1] == 'offer':
        oid = offer_id or parts[2]
        return handle_analytics_offer(event, context, oid)
    
    # /users/{telegram_id}/favorites
    if len(parts) == 3 and parts[0] == 'users' and parts[2] == 'favorites':
        tid = telegram_id or parts[1]
        if method == 'GET':
            return handle_get_favorites(event, context, tid)
        elif method == 'PUT':
            return handle_update_favorites(event, context, tid)
    
    # /users/{telegram_id}
    if len(parts) == 2 and parts[0] == 'users':
        tid = telegram_id or parts[1]
        if method == 'GET':
            return handle_get_user(event, context, tid)
        elif method == 'PUT':
            return handle_update_user(event, context, tid)
    
    # /offers/user/{telegram_id}
    if len(parts) == 3 and parts[0] == 'offers' and parts[1] == 'user':
        tid = telegram_id or parts[2]
        return handle_user_offers(event, context, tid)
    
    # /offers/{offer_id}/boost
    if len(parts) == 3 and parts[0] == 'offers' and parts[2] == 'boost':
        oid = offer_id or parts[1]
        if method == 'POST':
            return handle_create_boost(event, context, oid)
    
    # /offers/{offer_id}
    if len(parts) == 2 and parts[0] == 'offers':
        oid = offer_id or parts[1]
        if method == 'GET':
            return handle_get_offer(event, context, oid)
        elif method == 'PUT':
            return handle_update_offer(event, context, oid)
        elif method == 'DELETE':
            return handle_delete_offer(event, context, oid)
    
    return json_response({"error": f"Not found: {method} {path}"}, 404)
