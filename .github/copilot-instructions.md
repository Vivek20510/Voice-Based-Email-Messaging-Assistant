# Workspace Copilot Instructions

## Purpose
This file enables GitHub Copilot Chat to understand project intent and conventions for the `Voice-Based Email & Messaging Assistant` repository.

## Project Overview
- Project name: Voice-Based Email & Messaging Assistant
- Goal: Build an assistant that uses voice input/output to send and manage email and messaging conversations.
- Current workspace has: `Project_Requirements.xlsx`, `Voice-Based Email & Messaging Assistant .pdf` (no source code yet).

## Getting started
1. Open the workspace in VS Code.
2. Inspect `Project_Requirements.xlsx` and project PDF for product requirements and architectures.
3. Create standard folders when code is added:
   - `src/` for application code
   - `test/` for tests
   - `docs/` for architecture and onboarding docs

## Build and test commands
> Add actual commands here when your language/framework is chosen.
- `npm install` / `npm test` (JavaScript/TypeScript)
- `pip install -r requirements.txt` / `pytest` (Python)
- `dotnet restore` / `dotnet test` (.NET)

## Development process
- Use feature branches: `feature/<ticket>`
- Run formatting and linting before commit.
- Add/extend tests for each behavior.

## Agent/Chat guidance
- Use Copilot for:
  - scaffolding new components
  - generating tests and fixtures
  - drafting README and API documentation
  - summarizing requirements from provided documents

- Do not use Copilot for:
  - making production design decisions without human review
  - modifying behavior without a spec or test case in repo

## Links (add as available)
- `CONTRIBUTING.md`
- `ARCHITECTURE.md`
- `README.md`

## Next steps
- Add project source code and language-specific instructions to this file.
- Add `.github/AGENTS.md` or file-level instructions for area-specific behavior as repository matures.
