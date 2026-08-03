# RFC 018 — BASH_ENV for Claude Code

**Status:** Draft
**Created:** 2026-02-23

## Problem

Claude Code's Bash tool runs non-interactive bash. Non-interactive
bash does not source `~/.bashrc` or `~/.bash_profile` (POSIX
behavior). This means version managers that initialize in
`.bashrc` — asdf, mise, nvm, rbenv, pyenv, etc. — are invisible
to the Bash tool.

Workaround: prefix every command with
`source ~/.bashrc 2>/dev/null; ...`. This is tedious, fragile,
and easy to forget.

## Solution

Bash has a built-in mechanism: when the environment variable
`BASH_ENV` is set, non-interactive bash sources that file before
running any command.

Claude Code supports user-level environment variables in
`~/.claude/settings.json`:

```json
{
  "env": {
    "BASH_ENV": "/absolute/path/to/.bashrc"
  }
}
```

Use the absolute path (not `$HOME` or `~`) since JSON values
are not shell-expanded.

After saving, restart Claude Code. The Bash tool will now source
`.bashrc` automatically.

## Verification

```bash
# Should resolve to the version manager's shim, not "not found"
which mix     # asdf/mise — Elixir
which node    # nvm/mise — Node
which ruby    # rbenv/mise — Ruby
which python  # pyenv/mise — Python
```

## Notes

- Claude Code's documentation says "the shell environment is
  initialized from the user's profile." In practice this does
  not always work — particularly in container environments
  (Distrobox, toolbox, Docker) or when `.bashrc` guards itself
  behind an interactivity check (`[[ $- == *i* ]]`).
- `BASH_ENV` is the correct POSIX mechanism for this. It is not
  a hack.
- If `.bashrc` has an early-exit guard for non-interactive shells,
  the `BASH_ENV` approach will hit that guard and fail. In that
  case, either remove the guard or extract version-manager init
  into a separate file and point `BASH_ENV` at that instead.
- This setting is per-machine (not per-project), which is
  appropriate since version managers are per-machine.

## Future

If smrti grows a machine-bootstrap or dotfile-setup tool, this
should be part of it. Could also become a Claude Code hook or
a `/doctor` diagnostic check.
