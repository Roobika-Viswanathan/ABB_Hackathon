Title: IEC 61131-3 ST Syntax Core

- Assignments: `Var := Expr;`
- Boolean ops: `AND OR NOT`
- Comparators: `= <> > < >= <=`
- Blocks must end with `END_IF; END_CASE; END_FOR; END_WHILE;`
- Vars declared inside `VAR ... END_VAR`
- Types: `BOOL, INT, DINT, REAL, TIME`
- Edge detection: store prev state; rising := cur AND NOT prev;
