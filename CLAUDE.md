# CLAUDE.md — CRM Кримпал (faracrm fork)

## Проект
Форк open-source CRM: https://github.com/shurshilov/faracrm  
Наш форк: https://github.com/Pomogachcoin/faracrm  
Рабочая ветка: `crimpal-prod`  
Домен прода: https://crm.crimpalsert.ru

## Сервер (VPS #2)
- IP: 185.244.51.110
- SSH: `ssh root@185.244.51.110`
- Пароль: в C:\Users\1\.claude\projects\C--Users-1\memory\reference_vps2_crm.md
- Папка проекта: /opt/faracrm/

## Git workflow
```
upstream = https://github.com/shurshilov/faracrm    (исходник, не трогаем)
origin   = git@github.com:Pomogachcoin/faracrm.git  (наш форк, пушим сюда)
```

### Правила
1. Все правки — только в ветку `crimpal-prod`, никогда не в master
2. Редактировать локально в D:\faracrm\ → git push origin crimpal-prod
3. На сервере деплоить через /opt/faracrm/deploy/deploy_prod.sh
4. Тестировать сначала на staging (см. ниже)

### Получить обновления от автора
```bash
git fetch upstream
git checkout master
git merge upstream/master
git checkout crimpal-prod
git merge master
# разрешить конфликты если есть
git push origin crimpal-prod
```

## Деплой на ПРОД
```bash
ssh root@185.244.51.110
cd /opt/faracrm
bash deploy/deploy_prod.sh
```

## Деплой на STAGING
```bash
ssh root@185.244.51.110
cd /opt/faracrm
bash deploy/deploy_staging.sh
```
Staging доступен по: http://185.244.51.110:8081

## Стек
| Слой | Технологии |
|------|-----------|
| Backend | Python 3.12+, FastAPI, asyncpg, PostgreSQL |
| Frontend | React 18, TypeScript, Mantine UI v8 |
| Real-time | WebSocket + PostgreSQL LISTEN/NOTIFY |
| Интеграции | Telegram, WhatsApp, Avito, Email (IMAP/SMTP) |

## Порты
| Сервис | Прод | Staging |
|--------|------|---------|
| Frontend (nginx) | 8080 | 8081 |
| Backend (FastAPI) | 8000 | 8001 |
| PostgreSQL | внутренний | внутренний |

Nginx reverse proxy: 80 → 8080 (прод), 8181 → 8081 (staging, если настроен vhost)

## БД
| | Прод | Staging |
|-|------|---------|
| Имя | fara | fara_staging |
| User | openpg | openpg |
| Password | openpgpwd | openpgpwd |

## Что НЕ трогать в коде (настраивается через UI CRM)
- Коннекторы мессенджеров (Telegram, WhatsApp, Email, Avito) — через /settings/connectors
- Стадии лидов — через /settings/lead-stages
- Типы контактов — через /settings/contact-types
- Кастомные поля — через /settings/custom-fields
- Права пользователей — через /settings/roles

## Наши кастомные изменения (vs upstream)
Все изменения зафиксированы в коммитах ветки `crimpal-prod`. Смотреть:
```bash
git log upstream/master..crimpal-prod --oneline
```
