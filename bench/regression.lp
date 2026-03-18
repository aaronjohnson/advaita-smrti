% bench/regression.lp — Cross-run regression detection for smṛti-bench
%
% Compares two runs (previous vs current) of the same platform/arm/model.
% Python supplies per-prompt grades from both runs as scoped facts.
%
% Facts supplied by Python:
%
%   run_grade(previous, prompt_01_fact_recall, pass).
%   run_grade(current, prompt_01_fact_recall, fail).

% ─── Regression and improvement ─────────────────────────────────────────────

regression(P) :-
    run_grade(previous, P, pass),
    run_grade(current, P, fail).

improvement(P) :-
    run_grade(previous, P, fail),
    run_grade(current, P, pass).

% Went from a definite grade to ambiguous
became_unsure(P) :-
    run_grade(previous, P, pass),
    run_grade(current, P, unsure).

became_unsure(P) :-
    run_grade(previous, P, fail),
    run_grade(current, P, unsure).

% New errors
new_error(P) :-
    run_grade(current, P, error),
    run_grade(previous, P, G),
    G != error.

% ─── Run-level summary ──────────────────────────────────────────────────────

has_regression :- regression(_).
has_improvement :- improvement(_).

% Net regression: at least one regression with no improvements to offset
net_regression :- has_regression, not has_improvement.

% Stable: no regressions, no improvements
stable :- not has_regression, not has_improvement, not new_error(_).

% ─── Show directives ───────────────────────────────────────────────────────

#show regression/1.
#show improvement/1.
#show became_unsure/1.
#show new_error/1.
#show net_regression/0.
#show stable/0.
