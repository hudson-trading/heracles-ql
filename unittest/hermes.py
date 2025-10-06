import datetime
import json
import pathlib
import subprocess
from typing import Annotated

import pydantic

from heracles import ql


class Sample(pydantic.BaseModel):
    timestamp: datetime.datetime
    value: float


class Timeseries(pydantic.BaseModel):
    labels: dict[str, str]
    samples: list[Sample]


class TestRuleConfig(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        serialize_by_alias=True,
    )

    alert: str | None = None
    expr: str | ql.InstantVector
    for_: Annotated[datetime.timedelta | None, pydantic.Field(alias="for")] = None
    keep_firing_for: datetime.timedelta | None = None
    labels: dict[str, str] | None = None
    annotations: dict[str, str] | None = None

    @pydantic.field_serializer("for_", "keep_firing_for")
    def serialize_duration(self, duration: datetime.timedelta) -> int:
        return int(duration.total_seconds() * 1000)

    @pydantic.field_serializer("expr")
    def serialize_expr(self, expr: str | ql.InstantVector) -> str:
        if isinstance(expr, str):
            return expr
        return expr.render()


class TestCase(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        serialize_by_alias=True,
    )

    rule: TestRuleConfig | None = None
    expression: str | None = None
    initial_series: list[Timeseries]
    interval: datetime.timedelta
    start_after: datetime.timedelta = datetime.timedelta()
    steps: int

    @pydantic.field_serializer("interval", "start_after")
    def serialize_duration(self, duration: datetime.timedelta) -> int:
        return int(duration.total_seconds() * 1000)


class OutputAlert(pydantic.BaseModel):
    labels: dict[str, str]
    annotations: dict[str, str]
    state: str
    active_at: datetime.datetime
    resolved_at: datetime.datetime
    value: float
    at: datetime.datetime


class AlertTestResult(pydantic.BaseModel):
    alerts: list[list[OutputAlert]]


class ExpressionTestResult(pydantic.BaseModel):
    timeseries: list[Timeseries]


class HermesError(Exception):
    """Base exception for Hermes-related errors."""

    pass


class Hermes:
    """Python API for running tests using the Hermes binary."""

    def __init__(self, binary_path: str | pathlib.Path):
        """
        Initialize the HermesRunner.

        Args:
            binary_path: Path to the hermes binary executable
        """
        self.binary_path = pathlib.Path(binary_path)

        if not self.binary_path.exists():
            raise HermesError(f"Hermes binary not found at {self.binary_path}")

        if not self.binary_path.is_file():
            raise HermesError(f"Path {self.binary_path} is not a file")

    def _run_test(self, test_case: TestCase) -> AlertTestResult | ExpressionTestResult:
        """
        Run a single test case.

        Args:
            test_case: The test case to execute

        Returns:
            AlertTestResult if test_case.rule is set,
            ExpressionTestResult if test_case.expression is set

        Raises:
            HermesError: If the test execution fails
            ValueError: If the test case is invalid
        """
        if not test_case.rule and not test_case.expression:
            raise ValueError("TestCase must have either 'rule' or 'expression' set")

        if test_case.rule and test_case.expression:
            raise ValueError("TestCase cannot have both 'rule' and 'expression' set")

        test_json = test_case.model_dump_json(by_alias=True, exclude_none=True)

        try:
            result = subprocess.run(
                [str(self.binary_path)],
                input=test_json,
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise HermesError(
                f"Hermes execution failed with code {e.returncode}\n"
                f"stdout: {e.stdout}\n"
                f"stderr: {e.stderr}"
            ) from e
        except Exception as e:
            raise HermesError(f"Failed to execute Hermes: {e}") from e

        try:
            output_data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise HermesError(
                f"Failed to parse Hermes output as JSON: {e}\n"
                f"Output: {result.stdout}"
            ) from e

        if test_case.rule:
            return AlertTestResult.model_validate(output_data)
        else:
            return ExpressionTestResult.model_validate(output_data)

    def run_alert_test(
        self,
        rule: TestRuleConfig,
        initial_series: list[Timeseries],
        interval: datetime.timedelta,
        start_after: datetime.timedelta = datetime.timedelta(),
        steps: int = 1,
    ) -> AlertTestResult:
        """
        Run an alert test case.

        Args:
            rule: The alert rule configuration
            initial_series: Initial time series data
            interval: Time interval between evaluation steps
            start_after: Time to wait before starting evaluation
            steps: Number of evaluation steps to run

        Returns:
            AlertTestResult containing the alert evaluation results

        Raises:
            HermesError: If the test execution fails
        """
        test_case = TestCase(
            rule=rule,
            initial_series=initial_series,
            interval=interval,
            start_after=start_after,
            steps=steps,
        )
        result = self._run_test(test_case)
        if not isinstance(result, AlertTestResult):
            raise HermesError("hermes returned an unexpected result")
        return result

    def run_expression_test(
        self,
        expression: str | ql.InstantVector,
        initial_series: list[Timeseries],
        interval: datetime.timedelta,
        start_after: datetime.timedelta = datetime.timedelta(),
        steps: int = 1,
    ) -> ExpressionTestResult:
        """
        Run an expression test case.

        Args:
            expression: The PromQL expression to evaluate (string or InstantVector)
            initial_series: Initial time series data
            interval: Time interval between evaluation steps
            start_after: Time to wait before starting evaluation
            steps: Number of evaluation steps to run

        Returns:
            ExpressionTestResult containing the expression evaluation results

        Raises:
            HermesError: If the test execution fails
        """
        if isinstance(expression, str):
            rendered_expression = expression
        else:
            rendered_expression = expression.render()

        test_case = TestCase(
            expression=rendered_expression,
            initial_series=initial_series,
            interval=interval,
            start_after=start_after,
            steps=steps,
        )
        result = self._run_test(test_case)
        if not isinstance(result, ExpressionTestResult):
            raise HermesError("hermes returned an unexpected result")
        return result
