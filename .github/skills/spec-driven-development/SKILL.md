---
name: spec-driven-development
description: "Create or evolve a Spec-Driven Development (SDD) workflow: discover a project's product rules, architecture, data/API contracts, UX, tests, and roadmap; write modular specifications before implementing changes. Use when asked for SDD, specs, specification-first development, or reusable project engineering guidance."
argument-hint: "Describe the project or feature to specify"
user-invocable: true
---

# Spec-Driven Development

Use this workflow to create and maintain project specifications that are useful to
developers and coding agents. The skill is portable: adapt its process to the current
repository and technology stack instead of copying another project's assumptions.

## Principles

- Treat specifications as the agreed reference for expected behavior and acceptance, not
  as proof that undocumented behavior exists.
- Distinguish observed facts, proposed requirements, and unresolved questions.
- Never invent product rules, API behavior, test coverage, architecture, or stack versions.
- Keep specs and implementation synchronized when a change is delivered.
- Do not put credentials, tokens, private production endpoints, or personal data in specs.

## Workflow

1. **Clarify deliverables and scope.** Determine whether the request is a project-specific
   SDD guide, a reusable template, feature specifications, or all of these. Ask about
   placement when it affects portability (workspace vs personal skill).
2. **Inspect the repository.** Read the package/dependency manifest, routes, application
   bootstrap, domain models, service/API calls, feature pages, and existing tests. Do not
   assume the example supplied by the user matches this project.
3. **Record evidence and gaps.** For every technical fact, identify its source. Mark unknown
   backend behavior as a question to confirm. Check whether listed scripts and test files
   actually exist.
4. **Create a small, navigable spec set.** Prefer a master index plus only the relevant
   modular documents:
   - Product scope and business rules
   - Architecture and stack
   - Data/domain models
   - API/backend contracts
   - UI/UX and accessibility
   - Testing and quality gates
   - Roadmap and Definition of Done
5. **Make requirements testable.** State actor, trigger, expected result, failure/empty
   states, and measurable acceptance criteria. Separate current behavior from desired work.
6. **Apply SDD to implementation requests.** Read governing specs, update them when scope
   changes, implement the smallest complete change, add or update targeted tests, and run
   the narrowest relevant build/lint/test commands. Do not claim passing checks that were
   not run.
7. **Review and summarize.** Check links, filenames, stack versions, examples, and
   consistency against the repository. Report created/updated files, validation results,
   and unresolved questions.

## Suggested project layout

```text
specs/
  README.md
  01-product-specification.md
  02-architecture-and-tech-stack.md
  03-data-models-and-contracts.md
  04-api-and-backend-contracts.md
  05-ui-ux-specification.md
  06-testing-and-quality.md
  07-implementation-roadmap.md
```

Use the subset that fits the project; do not create empty documents just to match this
layout. When bootstrapping specs, use the [specification outline](./assets/spec-outline.md)
as a prompt for the information each section should contain.

## Reuse in another project

Copy the entire `spec-driven-development` skill folder (including `assets/`) into that
project's `.github/skills/` directory. Keep the folder name and frontmatter `name` aligned.
The skill contains no Mybox-specific stack assumptions; inspect the destination repository
before applying its workflow.

## Definition of Done

- Requirements and acceptance criteria reflect confirmed product decisions.
- Architecture and contracts are verified against the repository and authoritative backend
  documentation.
- Tests cover acceptance behavior or missing coverage is explicitly noted.
- Applicable validation commands have been run and their outcomes reported.
- Spec links resolve and no secrets or unverified claims were added.
