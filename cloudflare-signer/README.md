# LARA Cloudflare Signer

Автоматическая подпись IPA через Cloudflare Workers (бесплатно, без GitHub Actions минут)

## 🚀 Деплой на Cloudflare

### Вариант 1: Через Dashboard (самый простой)

1. Зайди на https://dash.cloudflare.com/
2. Workers & Pages → Create Application → Create Worker
3. Назови: `lara-signer`
4. Скопируй содержимое `worker.js` в редактор
5. Deploy
6. Готово! Твой URL: `https://lara-signer.YOUR-SUBDOMAIN.workers.dev`

### Вариант 2: Через CLI

```bash
# Установи Wrangler
npm install -g wrangler

# Логин в Cloudflare
wrangler login

# Деплой
cd cloudflare-signer
wrangler deploy
```

## 📱 Использование

После деплоя открой URL воркера на iPhone:
```
https://lara-signer.YOUR-SUBDOMAIN.workers.dev
```

Следуй инструкциям на странице:
1. Скачай ESign
2. Скачай LARA IPA
3. Подпиши в ESign своим Apple ID
4. Установи

## ✨ Преимущества

- ✅ **Бесплатно** - 100,000 запросов/день на Cloudflare
- ✅ **Не тратит GitHub Actions** минуты
- ✅ **Быстро** - CDN по всему миру
- ✅ **Просто** - один файл worker.js

## 🔧 Настройка

Воркер автоматически:
- Скачивает последний IPA с GitHub Releases
- Предоставляет красивый UI для подписи
- Перенаправляет на ESign/Scarlet

## 📊 Лимиты Cloudflare (Free Plan)

- 100,000 запросов/день
- 10ms CPU time на запрос
- Достаточно для личного использования

## 🌐 Custom Domain (опционально)

Можешь привязать свой домен:
1. Workers & Pages → lara-signer → Settings → Triggers
2. Add Custom Domain
3. Введи свой домен (например: sign.yourdomain.com)

---

**Готово!** Теперь можешь подписывать IPA удалённо без компьютера.
