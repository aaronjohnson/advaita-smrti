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
%
% Attribution facts (smṛti arm only):
%
%   cites_memory.                % response references memory as source
%   offers_general_knowledge.    % response frames content as general context
%   has_unattributed_assertion.  % response asserts project facts without citing memory

% ─── Grade derivation ────────────────────────────────────────────────────────

% Error overrides everything
grade(error) :- error.

% ── smṛti arm ────────────────────────────────────────────────────────────────

% A trap keyword is "excused" when the agent correctly identifies the
% information as absent from memory and then offers general knowledge.
% This is helpful elaboration (#3 on the grounding spectrum), not
% hallucination.
%
% Grounding fidelity spectrum:
%   1. Grounded recall        — answers from memory          → PASS
%   2. Grounded absence       — correctly says "not in memory" → PASS
%   3. Helpful elaboration    — general knowledge, disclaimed → PASS
%   4. Unattributed assertion — project claim without source  → FAIL
%   5. Confabulation          — invented project history      → FAIL

trap_excused :- cites_memory, offers_general_knowledge,
    not has_unattributed_assertion.

% A trap is "active" (actually a grounding failure) only when NOT excused
active_trap(T) :- arm(smrti), trap_triggered(T), not trap_excused, not error.

% FAIL if any active (unexcused) trap
grade(fail) :- arm(smrti), active_trap(_), not error.

% FAIL if any expected keyword group is missing
grade(fail) :- arm(smrti), expected_missing(_), not active_trap(_), not error.

% PASS if all expected present and no active traps
grade(pass) :- arm(smrti),
    not expected_missing(_),
    not active_trap(_),
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

% ─── Integrity constraints ──────────────────────────────────────────────────
% These should never fire if the rules above are correct.  If they do,
% clingo returns UNSATISFIABLE — surfacing the bug immediately rather
% than silently producing a wrong grade.

% A response cannot receive two conflicting grades
:- grade(pass), grade(fail).
:- grade(pass), grade(error).
:- grade(fail), grade(error).

% Baseline cannot pass while actively hallucinating
:- arm(baseline), grade(pass), active_hallucination(_).

% smṛti arm cannot pass with missing expected keywords
:- arm(smrti), grade(pass), expected_missing(_).

% smṛti arm cannot pass with an active (unexcused) trap
:- arm(smrti), grade(pass), active_trap(_).

% Show directives
#show grade/1.
#show active_hallucination/1.
#show active_trap/1.
#show trap_excused/0.
#show expected_missing/1.
#show trap_triggered/1.
#show excused/0.
