"""
Opt-in telemetry stub. No network calls — writes to a local file pending consent.
"""

import json
import os
import time
from utils import config


TELEMETRY_FILE = "navecraft_telemetry.jsonl"


class TelemetrySystem:
    @staticmethod
    def is_enabled():
        return bool(config.get('telemetry', 'enabled', default=False)
                    and config.get('telemetry', 'consented', default=False))

    @staticmethod
    def consent(yes=True):
        config.set('telemetry', 'consented', yes)
        config.set('telemetry', 'enabled', yes)
        config.save()

    @staticmethod
    def log_event(event_type, payload):
        if not TelemetrySystem.is_enabled():
            return
        entry = {'t': time.time(), 'type': event_type, 'payload': payload}
        try:
            with open(TELEMETRY_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass

    @staticmethod
    def log_crash(stack_trace, context=None):
        if not TelemetrySystem.is_enabled():
            return
        TelemetrySystem.log_event('crash', {'stack': stack_trace, 'context': context or {}})

    @staticmethod
    def log_death(cause, run_stats):
        TelemetrySystem.log_event('death', {'cause': cause, 'stats': run_stats})

    @staticmethod
    def log_tutorial_step(step_id, completed):
        TelemetrySystem.log_event('tutorial_step', {'step': step_id, 'completed': completed})


telemetry = TelemetrySystem()
