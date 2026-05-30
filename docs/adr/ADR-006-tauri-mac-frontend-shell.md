# ADR-006: Tauri as Mac Desktop Frontend Shell

Status: Accepted
Date: 2026-05-30
Owner: User

## Context

OmniVia needs a Mac frontend direction that supports the local-first desktop product while preserving a future path to OmniVia Cloud.

The main options considered were a local web app, Electron, Tauri, and native SwiftUI. The product direction favours a reusable web frontend that can run locally in a desktop shell first and later support a cloud/browser deployment.

## Decision

Adopt Tauri as the Mac desktop application shell for OmniVia.

The frontend should be implemented as a reusable web frontend so the same UI foundation can later support OmniVia Cloud.

## Rationale

Tauri provides a lighter desktop shell than Electron while still allowing OmniVia to use a web frontend. This fits the local-first product direction without locking the interface into Mac-only SwiftUI.

Using a shared web frontend also keeps the future OmniVia Cloud path open. The desktop app can wrap the frontend in Tauri, while a future cloud version can serve the same core interface in a browser with cloud-backed services.

## Consequences

Frontend implementation tasks should assume:

- A reusable web UI as the primary frontend layer.
- Tauri as the Mac desktop shell.
- Local-first desktop runtime remains the MVP priority.
- OmniVia Cloud can later reuse the frontend rather than starting again.

Claude should not choose Electron, SwiftUI, or a browser-only frontend for the main Mac shell unless this decision is explicitly revisited.

## Review Trigger

Revisit only if Tauri blocks core local-first capabilities, creates unacceptable packaging complexity, or OmniVia Cloud requirements prove incompatible with the shared frontend approach.
