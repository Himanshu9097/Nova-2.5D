"""Initial motion-based dynamic probability calculation."""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class DynamicProbabilityConfig:
    """Speed thresholds used to map speed to a probability."""

    stationary_speed: float = 0.2
    moving_speed: float = 1.0

    def __post_init__(self) -> None:
        if self.stationary_speed < 0 or self.moving_speed <= self.stationary_speed:
            raise ValueError("moving_speed must be greater than stationary_speed")


def dynamic_probability(
    velocity: tuple[float, float, float],
    config: DynamicProbabilityConfig | None = None,
) -> float:
    """Map estimated speed smoothly from low probability to high probability."""
    settings = config or DynamicProbabilityConfig()
    speed = math.sqrt(sum(component * component for component in velocity))
    if speed <= settings.stationary_speed:
        return 0.0
    if speed >= settings.moving_speed:
        return 1.0
    normalized = ((speed - settings.stationary_speed) /
                  (settings.moving_speed - settings.stationary_speed))
    return normalized * normalized * (3.0 - 2.0 * normalized)
