Title: Alarm Pattern (ST)

VAR
    PV : REAL; High : REAL; AlarmHigh : BOOL;
END_VAR

AlarmHigh := PV > High;
(* Add delay_on if needed with TON *)
