# MapChap - Telegram Mini App для бизнес-объявлений

## Дата: 22 февраля 2026

## 🎉 СТАТУС: Yandex Cloud ПОЛНОСТЬЮ НАСТРОЕН!

## Что выполнено

### ✅ Шаг 1: Добавлены endpoints в Cloud Function и API Gateway
- `/api/verification/inn` - верификация по ИНН
- `/api/verification/manual` - ручная верификация
- `/api/users/{telegram_id}/favorites` - избранное (GET, PUT)
- `/api/analytics/dashboard/{telegram_id}` - дашборд аналитики
- `/api/analytics/offer/{offer_id}` - аналитика объявления
- `/api/offers/user/{telegram_id}` - объявления пользователя
- `/api/offers/{offer_id}/boost` - создание буста
- `/api/telegram/webhook` - Telegram webhook

### ✅ Шаг 2: Фронтенд задеплоен в Yandex Object Storage
- Bucket: `mapchap-frontend`
- URL: http://mapchap-frontend.website.yandexcloud.net
- Service Account: `mapchap-s3-uploader` для загрузки файлов

### ✅ Шаг 3: Telegram Bot Webhook подключён
- Webhook URL: https://d5djdb4t6ohnfrpfaaic.ql6wied2.apigw.yandexcloud.net/api/telegram/webhook
- Bot: @mapchap_bot

## Рабочие URL
- **API Gateway**: https://d5djdb4t6ohnfrpfaaic.ql6wied2.apigw.yandexcloud.net
- **Frontend**: http://mapchap-frontend.website.yandexcloud.net
- **Emergent Preview**: https://process-steps-2.preview.emergentagent.com

## Конфигурация Yandex Cloud
- **Folder ID**: b1gfh042gbr60ukjqqi0
- **Function ID**: d4ekri024dh40qmoh0m5
- **API Gateway ID**: d5djdb4t6ohnfrpfaaic
- **MongoDB Cluster ID**: c9q57kp6i9hmo0gbi3p3
- **VPC Network**: enpja6k6tvpqjon21urk
- **Object Storage Bucket**: mapchap-frontend

## Доступные API Endpoints
```
GET  /api/health              - проверка здоровья
GET  /api/db-test             - тест MongoDB
GET  /api/categories          - категории (13 шт)
GET  /api/app-info            - информация о приложении

POST /api/auth/telegram       - авторизация через Telegram
POST /api/verification/inn    - верификация по ИНН
POST /api/verification/manual - ручная верификация

GET  /api/users/{id}          - профиль пользователя
PUT  /api/users/{id}          - обновление профиля
GET  /api/users/{id}/favorites - список избранного
PUT  /api/users/{id}/favorites - добавить/удалить из избранного

GET  /api/offers              - список объявлений
POST /api/offers              - создание объявления
GET  /api/offers/{id}         - детали объявления
PUT  /api/offers/{id}         - обновление объявления
DELETE /api/offers/{id}       - удаление объявления
GET  /api/offers/user/{id}    - объявления пользователя
POST /api/offers/{id}/boost   - создание буста

GET  /api/analytics/dashboard/{id}  - дашборд аналитики
GET  /api/analytics/offer/{id}      - аналитика объявления

GET  /api/boosts/plans        - тарифы бустов
GET  /api/articles            - статьи блога

POST /api/telegram/webhook    - Telegram webhook
```

## Аналитика для бизнеса
- ✅ Dashboard с графиками просмотров
- ✅ Детальная статистика по объявлению
- ✅ Тренды и сравнение периодов
- ✅ Умные рекомендации по бустам

## Технический стек
- **Frontend**: Vue.js 3, Vite, Pinia
- **Backend**: Python 3.12, Yandex Cloud Functions
- **Database**: Yandex Managed MongoDB
- **Storage**: Yandex Object Storage
- **API**: Yandex API Gateway (OpenAPI 3.0)

## Следующие шаги
- [ ] Настроить HTTPS для Object Storage (через CDN)
- [ ] Добавить мониторинг и алерты
- [ ] Настроить CI/CD для автоматического деплоя
