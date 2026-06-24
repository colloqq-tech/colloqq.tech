# Структура

| Часть | Где лежит | Что это |
| --- | --- | --- |
| Landing | В корне: `index.html`, `assets/`, `styles/`, `scripts/` | страница |
| SPA | `frontend/` | продуктовый интерфейс |

```text
├── index.html
├── styles/                 # Landing CSS
├── scripts/                # Landing JS
│
├── assets/
│
├── frontend/               # SPA
|
├── infra/                  # docker-compose, деплой, шаблоны переменных окружения
|
├── docs/
├── README.md
|
└── .github/workflows/      # CI
```
