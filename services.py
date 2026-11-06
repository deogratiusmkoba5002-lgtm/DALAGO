from .models import FareTable, FareOverride


def fare_between(board, alight):
    """
    Fare in TZS for riding one route from RouteStop `board` to RouteStop `alight`.
    Returns None when we have no fare data. We never guess a price.
    """
    if board.route_id != alight.route_id:
        raise ValueError("Both stops must be on the same route")
    if alight.sequence <= board.sequence:
        raise ValueError("Alighting stop must come after the boarding stop")

    override = FareOverride.objects.filter(board_stop=board, alight_stop=alight).first()
    if override:
        return override.amount_tzs

    crossed = alight.fare_stage - board.fare_stage
    row = (
        FareTable.objects
        .filter(route_id=board.route_id, stages_crossed__lte=crossed)
        .order_by("-stages_crossed")
        .first()
    )
    return row.amount_tzs if row else None
