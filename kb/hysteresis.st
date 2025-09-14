Title: Hysteresis Control Template

VAR
    PV : REAL; (* Process value *)
    Cmd : BOOL; (* Output command *)
    High : REAL; Low : REAL; (* thresholds *)
END_VAR

IF (PV > High) THEN
    Cmd := TRUE;
ELSIF (PV < Low) THEN
    Cmd := FALSE;
END_IF;
