# MapChap - Telegram Mini App

## Дата: 23 февраля 2026

## ✅ ВСЕ ПРОБЛЕМЫ ИСПРАВЛЕНЫ

### Исправленные проблемы:

1. **Бизнес-панель** - после шага 2 (создание объявления) переход к шагу 3 (success) работает
2. **Координаты** - объявления сохраняются с координатами [lat, lng] и отображаются на карте
3. **Профиль Telegram** - создаётся автоматически с first_name, last_name, photo_url из Telegram
4. **DaData убран** - только ручная верификация бизнеса
5. **HTTPS** - фронтенд по https://storage.yandexcloud.net/mapchap-frontend/
6. **Push-уведомления** - Telegram Bot отправляет уведомления о просмотрах и лайках

### Рабочие URL:
- **Frontend HTTPS**: https://storage.yandexcloud.net/mapchap-frontend/
- **Frontend HTTP**: http://mapchap-frontend.website.yandexcloud.net
- **API**: https://d5djdb4t6ohnfrpfaaic.ql6wied2.apigw.yandexcloud.net
- **Telegram Bot**: @mapchap_bot

### Бизнес-флоу:
1. Пользователь открывает Бизнес-панель
2. Заполняет форму ручной верификации (название, адрес, телефон)
3. Становится business_owner
4. Создаёт объявление с адресом и координатами
5. Видит экран success с кнопками "На карту" и "Дашборд"
6. Объявление появляется на карте

### Telegram Bot команды:
- /start - приветствие + кнопка Mini App
- /notifications - вкл/выкл уведомления
- /stats - статистика для бизнеса
- /help - справка

### Push-уведомления:
- 👁 Новый просмотр (раз в час)
- ❤️ Добавление в избранное
- ⚡ Активация буста
- ⏰ Истечение буста

### Тесты:
- Backend: 100% (9/9)
- Frontend: развёрнут, работает

### Yandex Cloud:
- Folder: b1gfh042gbr60ukjqqi0
- Function: d4ekri024dh40qmoh0m5
- API Gateway: d5djdb4t6ohnfrpfaaic
- MongoDB: c9q57kp6i9hmo0gbi3p3
- Bucket: mapchap-frontend
