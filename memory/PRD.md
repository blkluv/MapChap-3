# MapChap - Telegram Mini App для бизнес-объявлений

## Дата обновления: 22 февраля 2026

## 🎉 СТАТУС: ВСЕ ЗАДАЧИ ВЫПОЛНЕНЫ!

## Выполнено в этой сессии

### ✅ 1. HTTPS через Yandex Cloud
- Фронтенд доступен по HTTPS: `https://storage.yandexcloud.net/mapchap-frontend/`
- Сертификат SSL автоматический от Yandex Cloud

### ✅ 2. Убрана верификация через DaData/ИНН
- Оставлена только ручная верификация бизнеса
- Форма: название компании, адрес, телефон, описание

### ✅ 3. Telegram Bot Push-уведомления
Бот @mapchap_bot теперь отправляет:
- 👁 Уведомление о новом просмотре объявления (раз в час)
- ❤️ Уведомление когда кто-то добавил в избранное
- ⚡ Уведомление об активации буста
- ⏰ Напоминание о скором истечении буста

**Команды бота:**
- /start - Приветствие + кнопка открыть Mini App
- /notifications - Включить/отключить уведомления
- /stats - Статистика (для бизнес-аккаунтов)
- /help - Справка

## Рабочие URL
- **Frontend (HTTPS)**: https://storage.yandexcloud.net/mapchap-frontend/
- **Frontend (HTTP)**: http://mapchap-frontend.website.yandexcloud.net
- **API**: https://d5djdb4t6ohnfrpfaaic.ql6wied2.apigw.yandexcloud.net
- **Telegram Bot**: @mapchap_bot

## Yandex Cloud ресурсы
- **Folder ID**: b1gfh042gbr60ukjqqi0
- **Function ID**: d4ekri024dh40qmoh0m5
- **API Gateway ID**: d5djdb4t6ohnfrpfaaic
- **MongoDB Cluster ID**: c9q57kp6i9hmo0gbi3p3
- **Object Storage Bucket**: mapchap-frontend
- **CDN Origin Group**: 1291160975207484542

## API Endpoints
```
GET  /api/health              - проверка
GET  /api/db-test             - тест MongoDB
GET  /api/categories          - категории
POST /api/auth/telegram       - авторизация
POST /api/verification/manual - ручная верификация (единственная!)
GET  /api/users/{id}          - профиль
PUT  /api/users/{id}          - обновление
GET  /api/users/{id}/favorites - избранное
PUT  /api/users/{id}/favorites - добавить/удалить + push-уведомление
GET  /api/offers              - список
POST /api/offers              - создание
GET  /api/offers/{id}         - детали + push-уведомление о просмотре
PUT  /api/offers/{id}         - обновление
DELETE /api/offers/{id}       - удаление
GET  /api/offers/user/{id}    - объявления пользователя
POST /api/offers/{id}/boost   - буст + push-уведомление
GET  /api/analytics/dashboard/{id} - аналитика
GET  /api/analytics/offer/{id}     - статистика
POST /api/telegram/webhook    - webhook бота
```

## Telegram Bot функции
- Приветственное сообщение с кнопкой Mini App
- Push-уведомления владельцам бизнесов
- Команды: /start, /notifications, /stats, /help
- Inline-кнопки для быстрых действий
- Callback обработка (boost, toggle notifications)

## Следующие шаги (опционально)
- [ ] Добавить свой домен с HTTPS
- [ ] Интеграция оплаты через Telegram Stars
- [ ] Расширить аналитику (воронка конверсий)
