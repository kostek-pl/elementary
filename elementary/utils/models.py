from elementary.monitor.alerts.model import ModelAlert
from elementary.monitor.alerts.source_freshness import SourceFreshnessAlert
from elementary.monitor.alerts.test import TestAlert, ElementaryTestAlert


def get_shortened_model_name(model):
    return model
    if model is None:
        # this can happen for example when a Singular test is failing for having no refs.
        return None
    return ".".join(model.split(".")[1:])


def alert_to_concise_name(alert):
    if isinstance(alert, ElementaryTestAlert):
        return f"{alert.test_short_name or alert.test_name} - {alert.test_sub_type_display_name}"
    if isinstance(alert, TestAlert):
        return f"{alert.test_short_name or alert.test_name}"
    if isinstance(alert, SourceFreshnessAlert):
        return f"source freshness alert - {alert.source_name}.{alert.identifier}"
    if isinstance(alert, ModelAlert):
        if alert.materialization == "snapshot":
            text = "snapshot"
        else:
            text = "model"
        return f"dbt {text} alert - {alert.alias}"
    return "Alert"  # used only in Unit Tests


