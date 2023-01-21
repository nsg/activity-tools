LAST_WHL := "$(shell ls -1t dist | head -1)"

.PHONY: run
run: .env/bin/python
	@.env/bin/python run.py

.PHONY: build
build:
	.env/bin/python -m build --wheel .

.PHONY: upload
upload:
	.env/bin/twine upload dist/${LAST_WHL}

.PHONY: docs
docs:
	pdoc src/activity_tools -o docs

.env/bin/twine:
	.env/bin/pip install -r requirements.txt

requirements:
	.env/bin/pip install -r requirements.txt

.env/bin/python:
	virtualenv .env
