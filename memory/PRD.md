# MapChap - Telegram Mini App для бизнес-объявлений

## Дата: 22 февраля 2026

## 🎉 СТАТУС: Yandex Cloud ПОЛНОСТЬЮ РАБОТАЕТ!

## Что работает

### Yandex Cloud (100%)
- ✅ **Cloud Function** - подключается к MongoDB через VPC
- ✅ **API Gateway** - все основные эндпоинты работают
- ✅ **Managed MongoDB** - база данных в РФ (соответствует 152-ФЗ)
- ✅ **Security Group** - настроена для доступа

### API Endpoints (Yandex Cloud)
```
✅ GET  /api/health      - работает
✅ GET  /api/db-test     - MongoDB подключен
✅ GET  /api/categories  - 13 категорий
✅ POST /api/auth/telegram - создание пользователей
✅ GET  /api/offers      - список объявлений
✅ GET  /api/boosts/plans - планы бустов
✅ GET  /api/articles    - статьи
```

### Аналитика для бизнеса (Emergent)
- ✅ Dashboard с графиками
- ✅ Детальная статистика по объявлению
- ✅ Умные рекомендации

## URL
- **Yandex Cloud**: https://d5djdb4t6ohnfrpfaaic.ql6wied2.apigw.yandexcloud.net
- **Emergent**: https://backend-fix-34.preview.emergentagent.com

## Конфигурация
- Folder ID: b1gfh042gbr60ukjqqi0
- Function ID: d4ekri024dh40qmoh0m5
- MongoDB: c9q57kp6i9hmo0gbi3p3 (rc1a-7036pnpkejfpk6to.mdb.yandexcloud.net)
- Security Group: enphdkq66kg4elgf9dvf

## Решённая проблема
Проблема подключения Cloud Function к MongoDB решена:
1. Создана Security Group с правилами для MongoDB (порт 27018)
2. Функция подключена к VPC (networkId)
3. Использован TLS с tlsAllowInvalidCertificates=True для внутренней сети

## Следующие шаги
- [ ] Исправить передачу path parameters в API Gateway
- [ ] Добавить все endpoints из Emergent версии
- [ ] Настроить фронтенд на Yandex Cloud
