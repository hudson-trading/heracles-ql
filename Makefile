VM_VERSION=v1.109.1
GO ?= go

venv:
	uv sync --all-extras


dist:
	uv build

download-docs:
	mkdir -p dist/vm-docs
	wget "https://raw.githubusercontent.com/VictoriaMetrics/VictoriaMetrics/refs/tags/$(VM_VERSION)/docs/MetricsQL.md" -O "dist/vm-docs/docs-$(VM_VERSION).md"

generate_funcs:
	$(MAKE) download-docs
	uv run --all-extras codegen/markdown.py "dist/vm-docs/docs-$(VM_VERSION).md" heracles/ql/funcs
	ruff format --config pyproject.toml heracles/ql/funcs/__init__.py
	ruff format --config pyproject.toml heracles/ql/funcs/generated.py
	ruff check --fix --config pyproject.toml heracles/ql/funcs/__init__.py
	ruff check --fix --config pyproject.toml heracles/ql/funcs/generated.py

check_generated_funcs:
	$(MAKE) generate_funcs
	$(MAKE) format-lib
	./codegen/no-changes.sh

test:
	uv run --all-extras pytest ./test

format-lib:
	mkdir -p pkg
	$(GO) build -C formatter -buildmode=c-shared -o ../pkg/formatter.so formatter.go


clean:
	rm --one-file-system -r .venv
	rm --one-file-system -r dist
	rm --one-file-system -r pkg
	rm --one-file-system -r wheelhouse

.PHONY: venv dist download-docs generate_funcs test clean format-lib check_generated_funcs
