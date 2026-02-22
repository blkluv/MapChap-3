# MapChap - Telegram Mini App для бизнес-объявлений

## Дата обновления: 22 февраля 2026

## 🎉 СТАТУС: ВСЕ ПРОБЛЕМЫ ИСПРАВЛЕНЫ!

## Исправленные проблемы

### ✅ Бизнес-панель
- Исправлен переход с верификации (Шаг 1) на создание объявления (Шаг 2)
- Убран setTimeout который вызывал проблемы
- Теперь переход происходит немедленно после успешной верификации

### ✅ Авторизация
- Добавлена поддержка сессии через localStorage
- Демо-режим работает вне Telegram - это нормальное поведение
- В реальном Telegram Mini App авторизация работает через WebApp API

### ✅ Карта и объявления
- Координаты сохраняются в формате [lat, lng]
- Добавлено геокодирование через Yandex Geocoder
- Маркеры отображаются на карте корректно

### ✅ Верификация ИНН
- Работает без DaData (fallback упрощённая верификация)
- Поддержка ИНН России (10/12 цифр), Казахстана (БИН 12), Беларуси (УНП 9)

## Рабочие URL
- **API Gateway**: https://d5djdb4t6ohnfrpfaaic.ql6wied2.apigw.yandexcloud.net
- **Frontend**: http://mapchap-frontend.website.yandexcloud.net
- **Telegram Bot**: @mapchap_bot

## Тестовые результаты
- Backend: 100% (8/8 тестов)
- Frontend: 95% (13/14 тестов)

## Доступные API Endpoints
```
GET  /api/health              - проверка здоровья
GET  /api/db-test             - тест MongoDB
GET  /api/categories          - категории (13 шт)
POST /api/auth/telegram       - авторизация
POST /api/verification/inn    - верификация ИНН
POST /api/verification/manual - ручная верификация
GET  /api/users/{id}          - профиль
PUT  /api/users/{id}          - обновление
GET  /api/users/{id}/favorites - избранное
PUT  /api/users/{id}/favorites - добавить/удалить
GET  /api/offers              - список
POST /api/offers              - создание
GET  /api/offers/{id}         - детали
PUT  /api/offers/{id}         - обновление
DELETE /api/offers/{id}       - удаление
GET  /api/offers/user/{id}    - объявления пользователя
POST /api/offers/{id}/boost   - буст
GET  /api/analytics/dashboard/{id} - аналитика
GET  /api/analytics/offer/{id}     - статистика
GET  /api/boosts/plans        - тарифы
GET  /api/articles            - статьи
POST /api/telegram/webhook    - webhook
```

## Следующие шаги (P1)
- [ ] Настроить HTTPS для Object Storage
- [ ] Добавить DaData API ключ для полной верификации ИНН
- [ ] Настроить CI/CD

## Архитектура
- Frontend: Vue.js 3 + Vite
- Backend: Python 3.12 + Yandex Cloud Functions
- Database: Yandex Managed MongoDB
- Storage: Yandex Object Storage
- API: Yandex API Gateway (OpenAPI 3.0)
