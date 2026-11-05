def evaluate(*args, **kwargs):
    from .check import evaluate as implementation
    return implementation(*args, **kwargs)


def improving_incumbents(result, minimize=True):
    """A readiness check for runners that report incumbents: the evaluation was accepted, and on every instance
    the runner reported at least one incumbent, each strictly better than the one before, the last equal to
    the reference's optimum (the fixture's objective must be the reference's)."""
    if not result.get("accepted"):
        return False
    for item in result.get("instances", []):
        found = [objective for _, objective in item.get("incumbents", [])]
        better = (lambda a, b: b < a) if minimize else (lambda a, b: b > a)
        if not found or not all(better(a, b) for a, b in zip(found, found[1:])) or found[-1] != item.get("optimum"):
            return False
    return True


__all__ = ["evaluate", "improving_incumbents"]
