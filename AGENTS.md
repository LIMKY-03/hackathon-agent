# CofA hackathon orchestration instructions

This repository is a generic, prewritten framework. Never add a real contest
problem, contest file, solution, result, credential, or post-submission answer
to version control or any external service.

## Runtime policy

- Use only the Codex instance supplied inside the contest platform.
- Allowed models are `gpt-6.1-sol`, `gpt-5.6-terra`, `gpt-6-luna`, and
  `gpt-6-sol`. Never use Astra or any other model.
- Never use OpenRouter, an external model API, a personal API key, Computer
  Use, an external browser, remote control, file upload, `git push`, or any
  mechanism that transfers the problem, code, files, logs, or results outside
  the contest workspace.
- Public materials may be brought in only through contest-permitted read-only
  mechanisms such as `git clone`, Skills, MCP, or Plugins. Do not use these
  mechanisms for outbound transfer.
- Stop all AI work as soon as the submission is finalized. Do not assist with
  post-submission written questions.

## Orchestration contract

Read `TASK.json`, `.cofa/plan.json`, and `.cofa/prompts/` before acting. The
root coordinator owns the final response and delegates bounded work to these
roles when multi-agent tools are available:

1. `planner`: read-only data audit and edge-case analysis first, then requirement
   decomposition, traceability, risks, MVP, and plan. Write `.cofa/data-audit.md`
   and `.cofa/edge-cases.md` before handing work to the implementer.
2. `implementer`: implementation only after the plan is ready.
3. `tester`: tests, execution evidence, and defect reports.
4. `reviewer`: independent requirement, safety, and regression review.
5. `packager`: local submission manifest and final file checks only.

Prefer independent parallel work only when agents will not edit the same
files. The implementer is the primary code writer. The tester and reviewer
must not silently repair implementation defects; they report defects to the
coordinator, which reassigns fixes to the implementer and requests retesting.
The packager runs only after tests and review pass.

Keep all roles on the requested Fast service tier where the platform supports it.
Fast speed is separate from the `fast` model-routing profile. Do not silently change
models or reduce reasoning effort to simulate Fast mode.

During data preflight preserve source files, distinguish measurements from assumptions,
label sample-based findings, and turn edge cases into expected behavior and tests.
Resolve blocking data questions before implementing the affected functionality.

If multi-agent tools are unavailable, follow the role packets sequentially in
dependency order and write every handoff under `.cofa/handoffs/`.

Do not declare completion unless each requirement and output has evidence in
the traceability matrix and the local submission manifest contains no missing
item. Never push, upload, publish, or transmit the generated work.

