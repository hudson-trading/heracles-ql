"""Set of utilities for writing alert projects"""

from __future__ import annotations

import collections
import importlib
import logging
import os
import pathlib
import pkgutil
from types import ModuleType
from typing import Any

import pydantic
import yaml

from heracles import config, ql

log = logging.getLogger(__name__)


class _MultilineDumper(yaml.Dumper):
    def represent_str(self, data: str) -> yaml.ScalarNode:
        if "\n" in data:
            return self.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        return self.represent_scalar("tag:yaml.org,2002:str", data)


_MultilineDumper.add_representer(str, _MultilineDumper.represent_str)


class ConfigFactory:
    def config_from_bundles(self, *bundles: config.RuleBundle) -> PrometheusRulesConfig:
        return PrometheusRulesConfig.from_bundles(*bundles)


class PrometheusRulesConfig(pydantic.BaseModel):
    groups: list[PrometheusRuleGroup]

    def as_yaml(self) -> str:
        return yaml.dump(
            self.model_dump(exclude_none=True),
            Dumper=_MultilineDumper,
            sort_keys=False,
        )

    @staticmethod
    def from_bundles(*bundles: config.RuleBundle) -> PrometheusRulesConfig:
        groups = []
        for b in sorted(bundles, key=lambda b: b.name):
            groups.append(
                PrometheusRuleGroup(
                    name=b.name, rules=list(b.dump()), interval=b.evaluation_interval
                )
            )
        return PrometheusRulesConfig(groups=groups)

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        return super().model_dump(serialize_as_any=True, **kwargs)


class PrometheusRuleGroup(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        serialize_by_alias=True,
    )
    name: str
    rules: list[config.RealizedRule]
    interval: ql.Duration | None

    @pydantic.field_serializer("interval")
    def _serialize_renderable(self, expr: ql.Renderable | None) -> str | None:
        if expr is None:
            return None
        return expr.render()


class HeraclesProject:
    def __init__(
        self,
        *modules: ModuleType,
        config_factory: ConfigFactory | None = None,
    ) -> None:
        self.rules_bundles: collections.defaultdict[str, list[config.RuleBundle]] = (
            collections.defaultdict(list)
        )
        self.config_factory = config_factory or ConfigFactory()
        for m in modules:
            self.register_module(m)

    def register_module(self, module: ModuleType) -> None:
        self._add_module_rules(module)
        modules = pkgutil.walk_packages(module.__path__, prefix=f"{module.__name__}.")
        for m in modules:
            imported_module = importlib.import_module(m.name)
            self._add_module_rules(imported_module)

    def _add_module_rules(self, module: ModuleType) -> None:
        for attr in module.__dict__.values():
            if isinstance(attr, config.RuleBundle):
                self.rules_bundles[module.__name__].append(attr)
                log.info("rules bundle '{}' found in '{}'", attr.name, module.__name__)
        else:
            log.debug("no rules bundle found in '{}'", module.__name__)

    def generate_files(
        self, target_dir: pathlib.Path, file_extension: str = "rules.yml"
    ) -> list[pathlib.Path]:
        files: list[pathlib.Path] = []
        os.makedirs(target_dir, exist_ok=True)
        for module, bundles in self.rules_bundles.items():
            file_path = target_dir / f"{module}.{file_extension}"
            config_data = self.config_factory.config_from_bundles(*bundles).as_yaml()
            with open(file_path, "w") as output_file:
                output_file.write(config_data)
            files.append(file_path)
        return files
