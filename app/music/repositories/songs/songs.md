app/
├── routes/
│   └── music/
│       └── songs/
│           ├── router.py
│           ├── presenter.py
│           ├── constants.py
│           └── __init__.py
│
├── repositories/
│   └── songs/
│       ├── __init__.py
│       ├── types.py
│       ├── songs.py
│       ├── channels.py
│       ├── artists.py
│       ├── statistics.py
│       ├── search.py
│       ├── filters.py
│       ├── bulk.py
│       └── duplicate.py
│
├── services/
│   └── songs/
│       ├── __init__.py
│       ├── service.py
│       ├── validator.py
│       ├── formatter.py
│       ├── search.py
│       ├── filter.py
│       ├── duplicate.py
│       ├── statistics.py
│       ├── create.py
│       ├── update.py
│       ├── delete.py
│       ├── bulk.py
│       └── importer.py
│
├── templates/
│   └── songs/
│       ├── index.html
│       ├── list.html
│       ├── form.html
│       ├── detail.html
│       ├── components/
│       │   ├── modal_create.html
│       │   ├── modal_edit.html
│       │   ├── modal_delete.html
│       │   ├── modal_export.html
│       │   ├── modal_bulk.html
│       │   └── statistics.html
│       └── partials/
│           ├── table.html
│           ├── filters.html
│           └── pagination.html
│
├── static/
│   ├── js/
│   │   └── songs/
│   │       ├── songs.js
│   │       ├── api.js
│   │       ├── table.js
│   │       ├── filters.js
│   │       ├── export.js
│   │       ├── bulk.js
│   │       └── statistics.js
│   │
│   └── css/
│       └── songs.css
│
└── export/
    ├── repositories/
    ├── services/
    └── ...