# Окружение

Требуется: Python 3.11+

Зависимости ставятся в виртуальное окружение:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate

pip3 install -r requirements-dev.txt # runtime + тесты

# либо только runtime:
# pip3 install -r requirements.txt
```

## Тесты

```bash
cd backend
python3 -m pytest # конфигурация в pyproject.toml
```
