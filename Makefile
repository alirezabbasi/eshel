.PHONY: session-bootstrap wiki-index wiki-lint wiki-health new-task file-query ingest-initial validate-governance wrw init-wizard init-project

CORE_DIR := echel-core

session-bootstrap:
	$(MAKE) -C $(CORE_DIR) session-bootstrap

wiki-index:
	$(MAKE) -C $(CORE_DIR) wiki-index

wiki-lint:
	$(MAKE) -C $(CORE_DIR) wiki-lint

validate-governance:
	$(MAKE) -C $(CORE_DIR) validate-governance

wiki-health:
	$(MAKE) -C $(CORE_DIR) wiki-health

new-task:
	$(MAKE) -C $(CORE_DIR) new-task

file-query:
	$(MAKE) -C $(CORE_DIR) file-query

ingest-initial:
	$(MAKE) -C $(CORE_DIR) ingest-initial

wrw:
	$(MAKE) -C $(CORE_DIR) wrw

init-wizard:
	$(MAKE) -C $(CORE_DIR) init-wizard

init-project:
	$(MAKE) -C $(CORE_DIR) init-project
