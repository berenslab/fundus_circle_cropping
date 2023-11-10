from typing import Tuple
import numpy as np

def expectation(p: np.ndarray, w: np.ndarray) -> Tuple[float]:
    """Expectation step for finding circle in 2D image.

    Basically the 'least-squares circle fit' method.
    See https://dtcenter.org/sites/default/files/community-code/met/docs/write-ups/circle_fit.pdf
    for details.

    Args:
        p: Points on 2D plane.
        w: Point weights.

    Returns:
        Tuple of center points and radius of circle.
    """
    x, y = p
    x_mean = w.T @ x
    y_mean = w.T @ y
    u = x - x_mean
    v = y - y_mean
    S_uu = w.T @ (u**2)
    S_uv = w.T @ (u * v)
    S_vv = w.T @ (v**2)
    S_uuu = w.T @ (u**3)
    S_vvv = w.T @ (v**3)
    S_uvv = w.T @ (u * v**2)
    S_vuu = w.T @ (v * u**2)
    A_inv = np.array([[S_vv, -S_uv], [-S_uv, S_uu]]) / (S_uu * S_vv - S_uv**2)
    B = np.array([S_uuu + S_uvv, S_vvv + S_vuu]) / 2
    u_c, v_c = A_inv @ B
    x_c = u_c + x_mean
    y_c = v_c + y_mean
    alpha = u_c**2 + v_c**2 + S_uu + S_vv
    r = np.sqrt(alpha)
    return (x_c, y_c, r)


def maximization(
    p: np.ndarray,
    circle: Tuple[float],
    λ: float = 1.0,
) -> np.ndarray:
    """Maximization step for finding circle in 2D image.

    Adjust point weighting.

    Args:
        p: Points on 2D plane.
        circle: Tuple of center points and radius.
        λ: Decay constant of exponential function.

    Returns:
        Point weights.
    """
    x, y = p
    x_c, y_c, r = circle
    delta = λ * (np.sqrt((x - x_c) ** 2 + (y - y_c) ** 2) - r) ** 2
    delta = delta - delta.min()
    w = np.exp(-delta)
    w /= w.sum()
    return w


def circle_em(
    p: np.ndarray,
    circle_init: Tuple[float],
    num_steps: int = 100,
    λ: float = 0.1,
) -> Tuple[float]:
    """Iterative expectation-maximization algorithm to find circle in 2D plane.

    Use the domain knowledge that the circle we search for is the largest
        possible circle.
    Therefore, the algorithm can be started with an initial guess.

    Args:
        p: Points on 2D plane.
        circle_init: Initial circle guess.
        num_steps: Number of EM steps.
        λ: Decay constant of exponential function.

    Returns:
        Tuple of center points and radius of circle.
    """
    x_c, y_c, r = circle_init
    for step in range(num_steps):
        w = maximization(p, (x_c, y_c, r), λ / (num_steps - step))
        x_c, y_c, r = expectation(p, w)
    return (x_c, y_c, r)