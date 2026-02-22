# MapChap - Telegram Mini App для бизнес-объявлений на карте

## Дата: 22 февраля 2026

## Описание проекта
MapChap - платформа для размещения бизнес-объявлений на интерактивной карте, интегрированная с Telegram как Mini App.

## Технический стек
- **Frontend**: Vue.js 3, Vite, Pinia, Яндекс Карты
- **Backend**: FastAPI (Python), Motor (async MongoDB)
- **База данных**: MongoDB
- **Хостинг**: 
  - Emergent Platform (основной, рабочий)
  - Яндекс Облако (в процессе настройки)

## Что реализовано

### Backend API (100% работает на Emergent)
- ✅ Аутентификация через Telegram
- ✅ CRUD операции для пользователей
- ✅ CRUD операции для объявлений (offers)
- ✅ Верификация бизнеса через ИНН (DaData API)
- ✅ Верификация бизнеса вручную
- ✅ Избранное
- ✅ Категории (13 категорий)
- ✅ Статьи/Блог
- ✅ Бусты (монетизация через Telegram Stars)
- ✅ Геолокация и уведомления
- ✅ Telegram Bot Webhook

### Frontend (100% работает)
- ✅ Интерактивная карта Яндекс
- ✅ Фильтрация по категориям
- ✅ Поиск мест
- ✅ Профиль пользователя
- ✅ Бизнес-панель
- ✅ Создание объявлений
- ✅ Telegram Web App интеграция

### Яндекс Облако (частично настроено)
- ✅ Cloud Function создана (mapchap-backendv3)
- ✅ API Gateway настроен
- ✅ Managed MongoDB создан
- ⚠️ Проблема: Cloud Function не может подключиться к MongoDB
  - Причина: Сетевая изоляция, требуется дополнительная настройка VPC
  - Решение: Настроить Security Groups или использовать Serverless Connector

## Конфигурация Яндекс Облака

### Ресурсы
- **Folder ID**: b1gfh042gbr60ukjqqi0
- **Network ID**: enpja6k6tvpqjon21urk
- **Function ID**: d4ekri024dh40qmoh0m5
- **API Gateway ID**: d5djdb4t6ohnfrpfaaic
- **API Gateway Domain**: d5djdb4t6ohnfrpfaaic.ql6wied2.apigw.yandexcloud.net
- **MongoDB Cluster ID**: c9q57kp6i9hmo0gbi3p3
- **MongoDB Host**: rc1a-7036pnpkejfpk6to.mdb.yandexcloud.net:27018

### Учётные данные MongoDB
- User: mapchap_user
- Password: MapChap2024Secure!
- Database: mapchap

## Что нужно сделать для Яндекс Облака

### P0 - Критично
1. Настроить Security Groups для доступа Cloud Function → MongoDB
2. Или использовать Serverless Connector для подключения к VPC

### P1 - Важно
1. Настроить webhook для Telegram бота на Yandex Cloud endpoint
2. Тестирование полного flow в продакшене

### P2 - Желательно
1. Настроить мониторинг и логирование
2. CI/CD для автоматического деплоя

## Бэклог

### Функционал
- [ ] Отзывы и рейтинги
- [ ] Push-уведомления о новых местах рядом
- [ ] Интеграция с картами для навигации
- [ ] Аналитика для бизнеса
- [ ] Подписки и продвижение

### Технический долг
- [ ] Исправить подключение Cloud Function к MongoDB
- [ ] Добавить кэширование
- [ ] Оптимизация запросов к БД
