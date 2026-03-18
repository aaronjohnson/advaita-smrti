% bench/scoring.lp — ASP rules for smṛti-bench scoring
%
% Python extracts facts from each response, clingo derives the grade.
% Facts supplied per response (from Python):
%
%   arm(baseline).  or  arm(smrti).
%   prompt(prompt_02_decision_rationale).
%   contains(supabase).          % lowercased keyword found in response
%   admits_ignorance.            % response contains an ignorance phrase
%   has_assertion.               % response contains a positive assertion
%   has_generic_section.         % response has "common reasons" / "that said" etc.
%   expected_present(K).         % smṛti arm: expected keyword group K is present
%   expected_missing(K).         % smṛti arm: expected keyword group K is missing
%   trap_triggered(T).           % trap keyword T found in response
%   is_hallucination_keyword(K). % K is in BASELINE_HALLUCINATION for this prompt
%   error.                       % runner reported an error (no response)

% ─── Grade derivation ────────────────────────────────────────────────────────

% Error overrides everything
grade(error) :- error.

% ── smṛti arm ────────────────────────────────────────────────────────────────

% FAIL if any trap triggered
grade(fail) :- arm(smrti), trap_triggered(_), not error.

% FAIL if any expected keyword group is missing (and no trap — trap takes priority)
grade(fail) :- arm(smrti), expected_missing(_), not trap_triggered(_), not error.

% PASS if all expected present and no traps
grade(pass) :- arm(smrti),
    not expected_missing(_),
    not trap_triggered(_),
    not error.

% ── baseline arm ─────────────────────────────────────────────────────────────

% A hallucination keyword is "active" (actually hallucinated) only when
% it's present AND the response does not have a valid excuse for it.
%
% Valid excuses:
%   1. Response admits ignorance without making assertions (prompt echo / hedging)
%   2. Response has a generic advice section and admits ignorance
%
% If none of these hold, the keyword is actively hallucinated.

excused :- admits_ignorance, not has_assertion.
excused :- admits_ignorance, has_generic_section.

active_hallucination(K) :- arm(baseline),
    is_hallucination_keyword(K),
    contains(K),
    not excused.

% PROMPT_06 special case: ORM trap — only fail if asserted with confidence
% (handled by requiring assertion phrases like "we use", "the orm is")
prompt_06 :- prompt(prompt_06_hallucination_trap).

grade(pass) :- arm(baseline), prompt_06, not active_hallucination(_), not error.
grade(fail) :- arm(baseline), prompt_06, active_hallucination(_), not error.

% General baseline (non-PROMPT_06)
grade(fail) :- arm(baseline), not prompt_06,
    active_hallucination(_), not error.

grade(pass) :- arm(baseline), not prompt_06,
    admits_ignorance,
    not active_hallucination(_),
    not error.

grade(unsure) :- arm(baseline), not prompt_06,
    not admits_ignorance,
    not active_hallucination(_),
    not error.

% ─── Exactly one grade ───────────────────────────────────────────────────────
% Safety: if somehow no grade derived, mark unsure
grade(unsure) :- not grade(pass), not grade(fail), not grade(error).

% Show directives
#show grade/1.
#show active_hallucination/1.
#show expected_missing/1.
#show trap_triggered/1.
#show excused/0.
