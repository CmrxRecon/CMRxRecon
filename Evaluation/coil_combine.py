import numpy as np

def rss(data: np.ndarray, dim: int = 0) -> np.ndarray:
    """
    Compute the Root Sum of Squares (RSS).

    RSS is computed assuming that dim is the coil dimension.

    Args:
        data: The input array
        dim: The dimensions along which to apply the RSS transform

    Returns:
        The RSS value.
    """
    return np.sqrt((data**2).sum(dim))


def rss_complex(data: np.ndarray, dim: int = 0) -> np.ndarray:
    """
    Compute the Root Sum of Squares (RSS) for complex inputs.

    RSS is computed assuming that dim is the coil dimension.

    Args:
        data: The input array
        dim: The dimensions along which to apply the RSS transform

    Returns:
        The RSS value.
    """
    return np.sqrt(np.sum(np.abs(data)**2, axis=dim))