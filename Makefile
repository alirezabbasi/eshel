.PHONY: session-bootstrap wiki-index wiki-lint wiki-health new-task file-query ingest-initial validate-governance wrw

session-bootstrap:
	python3 tools/session_bootstrap.py

wiki-index:
	python3 tools/wiki_index.py

wiki-lint:
	python3 tools/wiki_lint.py

validate-governance:
	python3 tools/validate_governance.py

wiki-health: wiki-index wiki-lint validate-governance

new-task:
	python3 tools/new_task.py

file-query:
	python3 tools/file_query.py

ingest-initial:
	python3 tools/ingest.py raw/sources/initial-source.md --title "Initial source import" --kind source

wrw:
	python3 tools/wrw.py
