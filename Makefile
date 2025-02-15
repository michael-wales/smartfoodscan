default: pylint pytest

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

pylint:
    find . -iname "*.py" -not -path "./tests/*" | xargs -n1 -I {}  pylint --output-format=colorized {}; true

pytest:
    PYTHONDONTWRITEBYTECODE=1 pytest -v --color=yes
