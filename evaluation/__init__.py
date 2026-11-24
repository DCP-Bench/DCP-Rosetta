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


def incumbents_with_values(result, minimize=True):
    """A readiness check for runners that give incumbents their values (evaluate(..., incumbent_values=True)):
    improving_incumbents holds, and on every instance each incumbent carried values, which the evaluator checked."""
    return improving_incumbents(result, minimize) and all(
        item.get("incumbents_with_values") == len(item.get("incumbents", [])) for item in result.get("instances", []))


__all__ = ["evaluate", "improving_incumbents", "incumbents_with_values"]
