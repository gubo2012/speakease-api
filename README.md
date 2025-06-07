# speakease-api
speakease backend

## Dev
---
poetry run uvicorn app.main:app --reload

$env:TEST_ENV="dev"; pytest tests/test_main.py -v -s