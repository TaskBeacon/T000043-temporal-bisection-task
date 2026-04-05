from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Any

from psyflow.sim.contracts import Action, Feedback, Observation, SessionInfo


def _obs_get(obs: Observation | dict[str, Any], key: str, default: Any = None) -> Any:
    if isinstance(obs, dict):
        return obs.get(key, default)
    if hasattr(obs, key):
        value = getattr(obs, key)
        if value is not None:
            return value
    return default


def _obs_phase(obs: Observation | dict[str, Any]) -> str:
    phase = _obs_get(obs, "phase", "") or _obs_get(obs, "stage", "")
    return str(phase).strip().lower()


def _obs_keys(obs: Observation | dict[str, Any]) -> list[str]:
    raw = _obs_get(obs, "valid_keys", []) or []
    return [str(key).strip().lower() for key in list(raw)]


def _obs_factors(obs: Observation | dict[str, Any]) -> dict[str, Any]:
    factors = _obs_get(obs, "task_factors", {}) or {}
    if not isinstance(factors, dict):
        return {}
    return dict(factors)


def _sigmoid(value: float) -> float:
    value = max(-60.0, min(60.0, float(value)))
    return 1.0 / (1.0 + math.exp(-value))


@dataclass
class TaskSamplerResponder:
    """Temporal-bisection sampler for QA/simulation."""

    mode: str = "sampled"
    short_key: str = "left"
    long_key: str = "right"
    space_key: str = "space"
    midpoint_ms: float = 800.0
    slope: float = 6.0
    rt_mean_s: float = 0.42
    rt_sd_s: float = 0.08
    rt_min_s: float = 0.16
    no_response_rate: float = 0.01

    def __post_init__(self) -> None:
        self.mode = str(self.mode or "sampled").strip().lower()
        if self.mode not in {"scripted", "sampled", "sampler"}:
            self.mode = "sampled"
        if self.mode == "sampler":
            self.mode = "sampled"
        self.short_key = str(self.short_key or "left").strip().lower()
        self.long_key = str(self.long_key or "right").strip().lower()
        self.space_key = str(self.space_key or "space").strip().lower()
        self.midpoint_ms = float(self.midpoint_ms)
        self.slope = float(self.slope)
        self.rt_mean_s = float(self.rt_mean_s)
        self.rt_sd_s = max(1e-6, float(self.rt_sd_s))
        self.rt_min_s = max(0.0, float(self.rt_min_s))
        self.no_response_rate = min(1.0, max(0.0, float(self.no_response_rate)))
        self._rng: Any = None
        self._session: SessionInfo | None = None

    def start_session(self, session: SessionInfo, rng: Any) -> None:
        self._session = session
        self._rng = rng

    def end_session(self) -> None:
        self._session = None
        self._rng = None

    def on_feedback(self, fb: Feedback) -> None:
        return None

    def _random(self) -> float:
        rng = self._rng
        if hasattr(rng, "random"):
            return float(rng.random())
        return random.random()

    def _normal(self, mean: float, sd: float) -> float:
        rng = self._rng
        if hasattr(rng, "normal"):
            return float(rng.normal(mean, sd))
        if hasattr(rng, "gauss"):
            return float(rng.gauss(mean, sd))
        return float(random.gauss(mean, sd))

    def _sample_rt(self, *, valid_keys: list[str]) -> float:
        rt = self._normal(self.rt_mean_s, self.rt_sd_s)
        if self.space_key in valid_keys:
            rt = max(rt, self.rt_min_s)
        return max(self.rt_min_s, rt)

    def _choose_space(self, valid_keys: list[str], phase: str) -> Action:
        key = self.space_key if self.space_key in valid_keys else (valid_keys[0] if valid_keys else None)
        return Action(
            key=key,
            rt_s=self._sample_rt(valid_keys=valid_keys),
            meta={"source": "task_sampler", "phase": phase, "kind": "continue"},
        )

    def _choose_response(self, valid_keys: list[str], factors: dict[str, Any], phase: str) -> Action:
        duration = factors.get("stimulus_ms", self.midpoint_ms)
        try:
            duration_f = float(duration)
        except Exception:
            duration_f = float(self.midpoint_ms)

        if self.mode == "scripted":
            choose_long = duration_f >= self.midpoint_ms
        else:
            centered = (duration_f - self.midpoint_ms) / max(self.midpoint_ms, 1.0)
            p_long = _sigmoid(self.slope * centered)
            choose_long = self._random() < p_long

        if self._random() < self.no_response_rate:
            return Action(key=None, rt_s=None, meta={"source": "task_sampler", "phase": phase, "kind": "timeout_bias"})

        key = self.long_key if choose_long else self.short_key
        if key not in valid_keys:
            key = valid_keys[0] if valid_keys else None
        return Action(
            key=key,
            rt_s=self._sample_rt(valid_keys=valid_keys),
            meta={
                "source": "task_sampler",
                "phase": phase,
                "kind": "choice",
                "stimulus_ms": duration_f,
                "p_long": _sigmoid(self.slope * ((duration_f - self.midpoint_ms) / max(self.midpoint_ms, 1.0))),
                "chosen_side": "long" if choose_long else "short",
            },
        )

    def act(self, obs: Observation | dict[str, Any]) -> Action:
        valid_keys = _obs_keys(obs)
        phase = _obs_phase(obs)
        factors = _obs_factors(obs)

        if not valid_keys:
            return Action(key=None, rt_s=None, meta={"source": "task_sampler", "phase": phase, "kind": "no_valid_keys"})

        if phase in {"instruction", "good_bye", "goodbye"} or phase.endswith("intro") or phase.endswith("label"):
            if self.space_key in valid_keys:
                return self._choose_space(valid_keys, phase)

        if self.space_key in valid_keys and not any(k in valid_keys for k in (self.short_key, self.long_key)):
            return self._choose_space(valid_keys, phase)

        if any(k in valid_keys for k in (self.short_key, self.long_key)):
            return self._choose_response(valid_keys, factors, phase)

        return Action(
            key=valid_keys[0],
            rt_s=self._sample_rt(valid_keys=valid_keys),
            meta={"source": "task_sampler", "phase": phase, "kind": "fallback"},
        )


__all__ = ["TaskSamplerResponder"]
