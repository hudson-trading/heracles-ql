from heracles import config, ql


def multi_threshold(
    vector: ql.InstantVector,
    start: ql.ConstantOrVector,
    stop: ql.ConstantOrVector,
) -> config.ExprFunc:
    return hysteresis(start=vector > start, stop=vector < stop)


def hysteresis(start: ql.InstantVector, stop: ql.InstantVector) -> config.ExprFunc:
    """
    Define an alert with seperate start and stop conditions.
    """

    v = ql.Selector()

    def hysteresis_expr(alert: config.RealizedAlert) -> ql.InstantVector:
        return start | (
            (
                ql.absent(stop) & v.ALERTS(alertname=alert.name, alertstate="firing")
            ).ignoring("alertname", "alertstate", *(alert.labels or {}).keys())
        )

    return hysteresis_expr
