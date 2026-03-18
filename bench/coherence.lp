% bench/coherence.lp — Cross-prompt coherence checks for smṛti-bench
%
% Per-prompt grading (scoring.lp) evaluates each response in isolation.
% This program loads prompt-scoped facts from ALL responses in a run
% and derives coherence warnings that span multiple prompts.
%
% Facts supplied by Python (one set per prompt in the run):
%
%   arm(baseline|smrti).
%   prompt_grade(prompt_01_fact_recall, pass).
%   prompt_contains(prompt_02_decision_rationale, bloc).
%   prompt_admits_ignorance(prompt_03_task_status).

% ─── Baseline: selective hallucination ──────────────────────────────────────
% Agent admits ignorance on some prompts but hallucinates on others.
% Not necessarily wrong, but indicates inconsistent behavior worth flagging.

selective_hallucination(Pass, Fail) :-
    arm(baseline),
    prompt_grade(Pass, pass),
    prompt_grade(Fail, fail),
    Pass != Fail.

% ─── smṛti: partial recall ─────────────────────────────────────────────────
% Agent passes some prompts but fails others — may indicate partial tool usage
% (called memory tools for some prompts but not all).

partial_recall(Fail) :-
    arm(smrti),
    prompt_grade(Fail, fail),
    prompt_grade(_, pass).

% ─── PROMPT_02 ↔ PROMPT_04 alignment ───────────────────────────────────────
% Both test architecture decisions.  PROMPT_02 asks about decision rationale
% (Supabase choice), PROMPT_04 asks about state management coherence (BLoC).
% If the agent mentions BLoC on one but not the other, it may be confabulating
% rather than recalling from a consistent memory.

p02_p04_gap :-
    arm(smrti),
    prompt_contains(prompt_04_coherence, bloc),
    not prompt_contains(prompt_02_decision_rationale, bloc).

p02_p04_gap :-
    arm(smrti),
    prompt_contains(prompt_02_decision_rationale, bloc),
    not prompt_contains(prompt_04_coherence, bloc).

% ─── PROMPT_03 ↔ PROMPT_05 consistency ──────────────────────────────────────
% Both relate to deferred work.  PROMPT_03 asks what tasks are open,
% PROMPT_05 asks about deferred decisions.  If one mentions the offline-sync
% deferral but the other doesn't, the agent's recall is inconsistent.

p03_p05_gap :-
    arm(smrti),
    prompt_contains(prompt_05_deferred_recall, deferred),
    not prompt_contains(prompt_03_task_status, deferred).

p03_p05_gap :-
    arm(smrti),
    prompt_contains(prompt_03_task_status, deferred),
    not prompt_contains(prompt_05_deferred_recall, deferred).

% ─── Show directives ───────────────────────────────────────────────────────

#show selective_hallucination/2.
#show partial_recall/1.
#show p02_p04_gap/0.
#show p03_p05_gap/0.
