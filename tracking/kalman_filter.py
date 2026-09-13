"""A small constant-velocity Kalman filter with no external dependencies."""

from typing import Iterable


def _identity(size: int) -> list[list[float]]:
    return [[1.0 if row == column else 0.0 for column in range(size)] for row in range(size)]


def _matmul(left: list[list[float]], right: list[list[float]]) -> list[list[float]]:
    return [
        [sum(left[row][inner] * right[inner][column] for inner in range(len(right)))
         for column in range(len(right[0]))]
        for row in range(len(left))
    ]


def _transpose(matrix: list[list[float]]) -> list[list[float]]:
    return [list(column) for column in zip(*matrix)]


def _inverse(matrix: list[list[float]]) -> list[list[float]]:
    """Invert a small square matrix using Gauss-Jordan elimination."""
    size = len(matrix)
    augmented = [
        list(row) + [1.0 if row_index == column else 0.0 for column in range(size)]
        for row_index, row in enumerate(matrix)
    ]

    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) < 1e-12:
            raise ValueError("Kalman innovation matrix is singular")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        augmented[column] = [value / divisor for value in augmented[column]]

        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(augmented[row], augmented[column])
            ]

    return [row[size:] for row in augmented]


class KalmanFilter:
    """Constant-velocity filter for the state [x, y, z, vx, vy, vz]."""

    STATE_SIZE = 6

    def __init__(
        self,
        initial_position: Iterable[float] = (0.0, 0.0, 0.0),
        process_noise: float = 1.0,
        measurement_noise: float = 1.0,
        initial_position_variance: float = 1.0,
        initial_velocity_variance: float = 10.0,
    ):
        position = tuple(float(value) for value in initial_position)
        if len(position) != 3:
            raise ValueError("initial_position must contain exactly three values")
        if process_noise < 0 or measurement_noise <= 0:
            raise ValueError("process_noise must be non-negative and measurement_noise positive")

        self.state = [position[0], position[1], position[2], 0.0, 0.0, 0.0]
        self.process_noise = float(process_noise)
        self.measurement_noise = float(measurement_noise)
        self.covariance = [
            [0.0 for _ in range(self.STATE_SIZE)] for _ in range(self.STATE_SIZE)
        ]
        for index in range(3):
            self.covariance[index][index] = float(initial_position_variance)
            self.covariance[index + 3][index + 3] = float(initial_velocity_variance)

    def predict(self, dt: float) -> tuple[float, float, float]:
        """Advance the state by dt seconds and return the predicted position."""
        if dt < 0:
            raise ValueError("dt must be non-negative")

        transition = _identity(self.STATE_SIZE)
        for axis in range(3):
            transition[axis][axis + 3] = float(dt)

        self.state = [
            sum(transition[row][column] * self.state[column] for column in range(self.STATE_SIZE))
            for row in range(self.STATE_SIZE)
        ]
        process_covariance = [
            [0.0 for _ in range(self.STATE_SIZE)] for _ in range(self.STATE_SIZE)
        ]
        for axis in range(3):
            process_covariance[axis][axis] = self.process_noise * max(dt ** 4 / 4.0, 1e-9)
            process_covariance[axis + 3][axis + 3] = self.process_noise * max(dt ** 2, 1e-9)
            process_covariance[axis][axis + 3] = self.process_noise * dt ** 3 / 2.0
            process_covariance[axis + 3][axis] = process_covariance[axis][axis + 3]

        self.covariance = [
            [value + process_covariance[row][column]
             for column, value in enumerate(covariance_row)]
            for row, covariance_row in enumerate(
                _matmul(_matmul(transition, self.covariance), _transpose(transition))
            )
        ]
        return self.position

    def update(self, measured_position: Iterable[float]) -> tuple[float, float, float]:
        """Update the filter with an observed (x, y, z) position."""
        measurement = [float(value) for value in measured_position]
        if len(measurement) != 3:
            raise ValueError("measured_position must contain exactly three values")

        observation = [[1.0 if column == axis else 0.0 for column in range(self.STATE_SIZE)]
                       for axis in range(3)]
        innovation = [
            measurement[row] - sum(observation[row][column] * self.state[column]
                                   for column in range(self.STATE_SIZE))
            for row in range(3)
        ]
        innovation_covariance = _matmul(
            _matmul(observation, self.covariance), _transpose(observation)
        )
        for axis in range(3):
            innovation_covariance[axis][axis] += self.measurement_noise

        kalman_gain = _matmul(
            _matmul(self.covariance, _transpose(observation)),
            _inverse(innovation_covariance),
        )
        self.state = [
            value + sum(kalman_gain[row][column] * innovation[column] for column in range(3))
            for row, value in enumerate(self.state)
        ]
        identity = _identity(self.STATE_SIZE)
        self.covariance = _matmul(
            [[identity[row][column] - sum(kalman_gain[row][inner] * observation[inner][column]
                                          for inner in range(3))
              for column in range(self.STATE_SIZE)]
             for row in range(self.STATE_SIZE)],
            self.covariance,
        )
        return self.position

    @property
    def position(self) -> tuple[float, float, float]:
        """Return the estimated position."""
        return tuple(self.state[:3])

    @property
    def velocity(self) -> tuple[float, float, float]:
        """Return the estimated velocity."""
        return tuple(self.state[3:])
