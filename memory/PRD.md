# MapChap - Telegram Mini App для бизнес-объявлений на карте

## Дата: 22 февраля 2026

## Описание проекта
MapChap - платформа для размещения бизнес-объявлений на интерактивной карте, интегрированная с Telegram как Mini App.

## Технический стек
- **Frontend**: Vue.js 3, Vite, Pinia, Vue Router, Яндекс Карты
- **Backend**: FastAPI (Python), Motor (async MongoDB)
- **База данных**: MongoDB (Local + Yandex Managed MongoDB)

## Что реализовано

### Backend API (100% работает)
- ✅ Аутентификация через Telegram
- ✅ CRUD операции для пользователей
- ✅ CRUD операции для объявлений (offers)
- ✅ Верификация бизнеса (ИНН + Manual)
- ✅ Избранное
- ✅ Категории (13 категорий)
- ✅ Бусты (монетизация через Telegram Stars)
- ✅ **АНАЛИТИКА ДЛЯ БИЗНЕСА** (НОВОЕ)

### Аналитика (НОВОЕ)
- ✅ **Dashboard** - общая статистика по всем объявлениям
  - Всего просмотров, уникальных посетителей
  - Тренд по сравнению с прошлым периодом
  - Топ-объявления и требующие внимания
  - График просмотров по дням
- ✅ **Детальная аналитика по объявлению**
  - Просмотры по дням и часам
  - Пиковое время активности
  - Конверсия в избранное
  - Статус буста
- ✅ **Умные рекомендации**
  - Когда купить буст
  - Когда обновить контент
  - Оповещения о снижении интереса

### Frontend (100% работает)
- ✅ Интерактивная карта Яндекс
- ✅ Фильтрация по категориям
- ✅ Профиль пользователя
- ✅ Бизнес-панель с кнопкой "Аналитика"
- ✅ Страница аналитики /analytics

### Яндекс Облако (частично настроено)
- ✅ Cloud Function создана
- ✅ API Gateway настроен
- ✅ Managed MongoDB создан
- ✅ Security Group создана
- ⚠️ Cloud Function не подключается к MongoDB (требуется Serverless Connector)

## API Endpoints аналитики

```
GET /api/analytics/dashboard/{telegram_id}?period=7d|30d|90d
GET /api/analytics/offer/{offer_id}?telegram_id={id}&period=7d|30d|90d
GET /api/analytics/compare/{telegram_id}?offer_ids=id1,id2,id3
```

## Конфигурация Yandex Cloud
- Folder ID: b1gfh042gbr60ukjqqi0
- Function ID: d4ekri024dh40qmoh0m5
- MongoDB Cluster: c9q57kp6i9hmo0gbi3p3
- Security Group: enphdkq66kg4elgf9dvf

## Бэклог

### P0 - Критично
- [ ] Настроить Serverless Connector для MongoDB в Yandex Cloud

### P1 - Важно
- [ ] Добавить отзывы и рейтинги
- [ ] Push-уведомления о новых местах

### P2 - Желательно
- [ ] Экспорт аналитики в PDF
- [ ] Сравнение периодов
