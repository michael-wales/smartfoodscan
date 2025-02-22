default: pylint pytest

install:
	pip install -e .
	pip install -r requirements.txt

pylint:
	@find . -iname "*.py" -not -path "./tests/*" | xargs -n1 -I {}  pylint --output-format=colorized {}; true

pytest:
	@PYTHONDONTWRITEBYTECODE=1 pytest -v --color=yes
