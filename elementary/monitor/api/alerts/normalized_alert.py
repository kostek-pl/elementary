import copy
from typing import List, Optional

from elementary.utils.json_utils import try_load_json
from elementary.utils.log import get_logger

logger = get_logger(__name__)

TABLE_FIELD = "table"
COLUMN_FIELD = "column"
DESCRIPTION_FIELD = "description"
OWNERS_FIELD = "owners"
TAGS_FIELD = "tags"
SUBSCRIBERS_FIELD = "subscribers"
RESULT_MESSAGE_FIELD = "result_message"
TEST_PARAMS_FIELD = "test_parameters"
TEST_QUERY_FIELD = "test_query"
TEST_RESULTS_SAMPLE_FIELD = "test_results_sample"
DEFAULT_ALERT_FIELDS = [
    TABLE_FIELD,
    COLUMN_FIELD,
    DESCRIPTION_FIELD,
    OWNERS_FIELD,
    TAGS_FIELD,
    SUBSCRIBERS_FIELD,
    RESULT_MESSAGE_FIELD,
    TEST_PARAMS_FIELD,
    TEST_QUERY_FIELD,
    TEST_RESULTS_SAMPLE_FIELD,
]


class NormalizedAlert:
    def __init__(self, alert: dict) -> None:
        self.alert = alert
        self.test_meta = self._flatten_meta("test_meta")
        self.model_meta = self._flatten_meta("model_meta")
        self.normalized_alert = self._normalize_alert()

    def get_normalized_alert(self) -> dict:
        return self.normalized_alert

    def _flatten_meta(self, node_meta_field: str) -> dict:
        # backwards compatibility for alert configuration
        meta = try_load_json(self.alert.get(node_meta_field)) or {}
        return {**meta, **meta.get("alerts_config", {})}

    def _normalize_alert(self):
        try:
            normalized_alert = copy.deepcopy(self.alert)
            normalized_alert["subscribers"] = self._get_alert_subscribers()
            normalized_alert["slack_channel"] = self._get_alert_chennel()
            normalized_alert[
                "alert_suppression_interval"
            ] = self._get_alert_suppression_interval()
            normalized_alert["alert_fields"] = self._get_alert_fields()
            return normalized_alert
        except Exception:
            logger.error(
                f"Failed to extract alert subscribers and alert custom slack channel {self.alert.get('id')}. Ignoring it for now and main slack channel will be used"
            )
            return self.alert

    def _get_alert_subscribers(self) -> List[Optional[str]]:
        subscribers = []
        test_subscribers = self.test_meta.get("subscribers", [])
        model_subscribers = self.model_meta.get("subscribers", [])
        if isinstance(test_subscribers, list):
            subscribers.extend(test_subscribers)
        else:
            subscribers.append(test_subscribers)

        if isinstance(model_subscribers, list):
            subscribers.extend(model_subscribers)
        else:
            subscribers.append(model_subscribers)
        return subscribers

    def _get_alert_chennel(self) -> Optional[str]:
        model_slack_channel = self.model_meta.get("channel")
        test_slack_channel = self.test_meta.get("channel")
        return test_slack_channel or model_slack_channel

    def _get_alert_suppression_interval(self) -> int:
        model_alert_suppression_interval = self.model_meta.get(
            "alert_suppression_interval"
        )
        test_alert_suppression_interval = self.test_meta.get(
            "alert_suppression_interval"
        )
        if test_alert_suppression_interval is not None:
            return test_alert_suppression_interval
        elif model_alert_suppression_interval is not None:
            return model_alert_suppression_interval
        else:
            return 0

    def _get_alert_fields(self) -> Optional[List[str]]:
        # If there is no alerts_fields in the test meta object,
        # we return the model alerts_fields from the model meta object.
        # The fallback is DEFAULT_ALERT_FIELDS.
        return (
            self.test_meta.get("alert_fields")
            if self.test_meta.get("alert_fields")
            else self.model_meta.get("alert_fields", DEFAULT_ALERT_FIELDS)
        )
