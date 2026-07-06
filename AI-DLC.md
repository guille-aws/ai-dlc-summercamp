# AI-DLC (AI-Driven Development Life Cycle)

AI-DLC is an intelligent software development workflow that adapts to your needs, maintains quality standards, and keeps you in control of the process. It is fundamentally a **methodology**, not a tool: the agent proposes, and you approve every critical decision.

This document describes how AI-DLC is set up and used for this workshop with **Kiro**. For the full upstream project (including other IDEs and supporting tools), see [awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows).

## Table of Contents

1. [How It Works in Kiro](#how-it-works-in-kiro)
2. [Rule Layout](#rule-layout)
3. [Usage](#usage)
4. [Three-Phase Adaptive Workflow](#three-phase-adaptive-workflow)
5. [Key Features](#key-features)
6. [Extensions](#extensions)
7. [Generated `aidlc-docs/`](#generated-aidlc-docs)
8. [Tenets](#tenets)

## How It Works in Kiro

AI-DLC uses [Kiro Steering Files](https://kiro.dev/docs/cli/steering/) within your project workspace. The rules are split into two parts:

- **`aws-aidlc-rules/`** — the core AI-DLC workflow rules (orchestration logic). The entry point is `core-workflow.md`, which overrides Kiro's built-in workflows when you invoke AI-DLC.
- **`aws-aidlc-rule-details/`** — detailed rules loaded on demand by the core workflow, so only the relevant guidance enters context for each phase.

For this workshop these folders are kept current by `code/update-from-repo.sh`, which pulls them from the upstream repo into the locations below.

Run AI-DLC in Kiro **Vibe mode**. If Kiro nudges you to switch to Spec mode, select **No** to stay in Vibe mode so the AI-DLC workflow stays in control.

To verify the rules are loaded, open the steering panel and confirm you see a `core-workflow` entry under **Workspace** (IDE), or run `/context show` and look for `.kiro/steering/aws-aidlc-rules` (CLI).

## Rule Layout

```text
.kiro/
├── steering/
│   └── aws-aidlc-rules/        # Core workflow rules (entry point: core-workflow.md)
└── aws-aidlc-rule-details/     # Detailed rules, loaded on demand
    ├── common/
    ├── inception/
    ├── construction/
    ├── extensions/
    └── operations/
```

## Usage

1. Start any development task by stating your intent beginning with **"Using AI-DLC, ..."** in the chat.
2. The AI-DLC workflow activates automatically and guides you from there.
3. Answer the structured questions AI-DLC asks (these are written into plan files using `[Answer]:` tags, not just chat).
4. Carefully review every plan the AI generates — your oversight and validation are part of the process.
5. Review the execution plan to see which stages will run.
6. Review the artifacts and approve each stage to stay in control.
7. All artifacts are generated in the `aidlc-docs/` directory.

## Three-Phase Adaptive Workflow

AI-DLC follows a structured three-phase approach that adapts to your project's complexity. The workflow only executes the stages that add value to your specific request.

### 🔵 Inception — *what* to build and *why*

- Requirements analysis and validation
- User story creation (when applicable)
- Application design and decomposition into units of work for parallel development
- Risk assessment and complexity evaluation
- Reverse engineering for brownfield projects (existing codebases)

### 🟢 Construction — *how* to build it

- Functional (business logic) design
- Non-functional requirements and NFR design
- Infrastructure design
- Code generation and implementation
- Build, test, and quality validation

### 🟡 Operations — deployment and monitoring (future)

- Deployment automation and infrastructure
- Monitoring and observability
- Production readiness validation

## Key Features

| Feature | Description |
| --- | --- |
| **Adaptive Intelligence** | Only executes stages that add value to your request |
| **Context-Aware** | Analyzes existing codebase and complexity requirements |
| **Risk-Based** | Complex changes get comprehensive treatment; simple changes stay efficient |
| **Question-Driven** | Structured questions captured in files with `[Answer]:` tags, not just chat |
| **Always in Control** | Review execution plans and approve each phase |
| **Extensible** | Layer custom rules (security, compliance, resiliency) on top of the core workflow |

## Extensions

AI-DLC supports an extension system that layers additional rules on top of the core workflow. Extensions live under `aws-aidlc-rule-details/extensions/`, grouped by category (e.g. `security/`, `testing/`, `resiliency/`).

Each extension has two files in the same directory:

- A **rules file** (e.g. `security-baseline.md`) containing the rules.
- An **opt-in file** (e.g. `security-baseline.opt-in.md`) containing a multiple-choice prompt shown during Requirements Analysis.

At workflow start, AI-DLC loads only the lightweight `*.opt-in.md` files. When you opt in, the matching rules file is loaded (strip `.opt-in.md`, append `.md`); when you opt out, it is never loaded. Extensions without an opt-in file are always enforced. Once enabled, extension rules are blocking — each stage verifies compliance before proceeding.

> The bundled security and resiliency extensions are directional references. Each organization should build, customize, and thoroughly test its own rules before using them in production workflows.

## Generated `aidlc-docs/`

When you run the workflow, artifacts are generated under an `aidlc-docs/` directory at the workspace root. The exact files depend on project type (greenfield vs brownfield), complexity, and which stages run. Application code is never placed in `aidlc-docs/` — only markdown documentation lives here; code goes to the workspace root.

```text
aidlc-docs/
├── aidlc-state.md          # Workflow state — project info, stage progress, current status
├── audit.md                # Append-only audit trail of every interaction (ISO 8601 timestamps)
│
├── inception/              # 🔵 WHAT to build and why
│   ├── plans/              # Execution plan + per-stage plans with [Answer]: tags and checkboxes
│   ├── reverse-engineering/# Brownfield only — analysis of an existing codebase
│   ├── requirements/       # requirements.md + requirement-verification-questions.md
│   ├── user-stories/       # stories.md + personas.md (if the stage runs)
│   └── application-design/ # components, services, dependencies, units of work
│
├── construction/           # 🟢 HOW to build it
│   ├── plans/              # Per-unit functional/NFR/infrastructure/code-generation plans
│   ├── {unit-name}/        # Per-unit functional-design, nfr-*, infrastructure-design, code summaries
│   └── build-and-test/     # Build + test instructions and readiness summary
│
└── operations/             # 🟡 Placeholder for future expansion
```

For the complete artifact reference, see [docs/GENERATED_DOCS_REFERENCE.md](https://github.com/awslabs/aidlc-workflows/blob/main/docs/GENERATED_DOCS_REFERENCE.md) in the upstream repo.

## Tenets

- **No duplication.** The source of truth lives in one place. Files for specific tools are generated from the source rather than maintained as separate copies.
- **Methodology first.** AI-DLC is a methodology, not a tool — you shouldn't need to install anything to get started.
- **Reproducible.** Rules are explicit enough that different models produce similar outcomes.
- **Agnostic.** The methodology works with any IDE, agent, or model.
- **Human in the loop.** Critical decisions require explicit user confirmation. The agent proposes; the human approves.
