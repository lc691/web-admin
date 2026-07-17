app/
│
├── core/
│   ├── config.py
│   ├── logging_setup.py
│   ├── middleware.py
│   └── routes.py
│
├── db/
│   ├── connect.py
│   └── migration/
│
├── routes/
│   │
│   ├── dashboard.py
│   ├── channels.py
│   ├── artists.py
│   │
│   └── songs/
│       ├── __init__.py
│       ├── list.py
│       ├── export.py
│       ├── usage.py
│       ├── batch.py
│       └── preview.py
│
├── services/
│   │
│   ├── songs/
│   │   ├── __init__.py
│   │   ├── repository.py
│   │   ├── service.py
│   │   └── types.py
│   │
│   ├── export/
│   │   ├── __init__.py
│   │   ├── repository.py
│   │   ├── service.py
│   │   ├── selector.py
│   │   ├── formatter.py
│   │   ├── blacklist.py
│   │   ├── validators.py
│   │   ├── youtube.py
│   │   ├── labels.py
│   │   └── types.py
│   │
│   ├── usage/
│   │   ├── __init__.py
│   │   ├── repository.py
│   │   ├── service.py
│   │   └── types.py
│   │
│   └── shared/
│       ├── database.py
│       ├── pagination.py
│       ├── response.py
│       └── utils.py
│
├── templates/
│   ├── base.html
│   ├── dashboard/
│   ├── channels/
│   ├── artists/
│   └── songs/
│
├── static/
│   ├── css/
│   ├── js/
│   ├── img/
│   └── vendor/
│
└── main.py