# Safety policy

This framework is intentionally inbound-only during a contest run.

## Allowed

- Clone this already-public, generic repository before or during the contest
  when the event rules permit public GitHub downloads.
- Enter the live task only inside the contest-provided workspace.
- Use the contest-provided Codex CLI with one of the four allowed models.
- Use public Skills, MCP servers, Plugins, algorithms, and source references
  only when the contest rules permit them and only for inbound assistance.
- Create code, tests, plans, logs, and submission files locally.

## Prohibited

- Astra, OpenRouter, Claude Code, external model APIs, personal API keys, or
  personal paid AI subscriptions.
- Computer Use, browser automation, remote control, or evasion of monitoring,
  upload, network, or platform restrictions.
- Uploading personal files into the contest environment.
- Sending the task, files, code, outputs, screenshots, logs, or results out of
  the contest workspace, including through `git push`.
- AI assistance after the main submission is finalized, including written
  follow-up questions.

`cofa-orchestrator lock` creates a local post-submission lock. All execution
commands refuse to run while that lock exists.

