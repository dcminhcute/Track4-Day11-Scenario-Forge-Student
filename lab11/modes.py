"""Part D: name the failure. TODO 8."""
from __future__ import annotations

from avsim import core


def label_mode(R: core.Rollout, k: int, event: dict, contact_type) -> str:
    """Name the kind of failure behind one ego failure event (a collision, or a crosswalk block).

    'crosswalk_block' - the other party is the crossing pedestrian P1: the ego stopped with its body on the
                      crosswalk in P1's way (event["kind"] == "block"), or hit P1
    'rear_ended' - something ran into the ego from behind (use contact_type(R, k, event) == 'rear')
    'bus_bypass' - the ego hit C2 while C2 was squeezing past the stopped bus: at contact C2 is at x < 112 m
                   and slower than 6 m/s
    'cut_in'     - the ego hit C2 in any other situation
    'other'      - anything else
    Check in that order. Positions and speeds at contact: R.F[k, event["f"], core.IX["C2"]] (x is column 0, v is 4).
    """
    other = event["b"] if event["a"] == "ego" else event["a"]
    # crosswalk_block: P1 and event is a block, or collision with P1
    if other == "P1":
        return "crosswalk_block"
    # rear_ended: contact type is rear
    if contact_type(R, k, event) == "rear":
        return "rear_ended"
    # bus_bypass or cut_in: collision with C2
    if other == "C2":
        f = event["f"]
        c2_data = R.F[k, f, core.IX["C2"]]
        x, v = c2_data[0], c2_data[4]
        if x < 112.0 and v < 6.0:
            return "bus_bypass"
        return "cut_in"
    return "other"
