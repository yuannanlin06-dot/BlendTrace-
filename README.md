# BlendTrace

**BlendTrace** is a small, offline Blender extension that turns undoable modeling history into a readable timeline and adds a **semantic cursor** inside the 3D View.

> See how a model was made — not just the final model.

## What v0.2.0 does

- Adds a **BlendTrace** tab to the 3D View sidebar (`N`).
- Starts and stops local operation recording.
- Reads Blender's current undo-stack step and turns it into a simple timeline.
- Shows the active object name for each captured step.
- Adds short Chinese explanations for common modeling operations.
- Draws a **semantic teaching cursor** at the active object's origin and labels it with the latest captured operation.
- Lets the user turn the semantic cursor on or off.
- Runs locally with **no network access, no account, no API key, no analytics and no cloud storage**.

## Semantic cursor privacy model

The semantic cursor is **not** a system mouse recorder. It does not read global mouse coordinates or monitor input outside Blender. It uses the active object's Blender scene position and the current 3D View state to draw a local overlay.

## Install

1. Download the install ZIP from the repository release.
2. In Blender, open **Edit → Preferences → Extensions/Add-ons**.
3. Choose **Install from Disk**.
4. Select the BlendTrace install ZIP and enable it.
5. Return to the 3D View and press `N`.
6. Open the **BlendTrace** tab and click **Start Recording**.
7. Perform a few undoable modeling operations and watch the timeline and semantic cursor update.

## Privacy and security

BlendTrace v0.2.0 is intentionally offline. It contains no networking, telemetry, analytics, AI/API integrations, clipboard access, browser access, credential access, global input capture, subprocess execution, or arbitrary file scanning.

See [PRIVACY.md](PRIVACY.md) and [SECURITY.md](SECURITY.md).

## Current limitations

This is an MVP. Blender's undo stack is not a complete stream of every UI action, so this version does not capture every click, selection change, exact mouse path, modal sub-step, or complete operator parameter set. The semantic cursor currently points to the active object's origin rather than individual selected vertices/edges/faces.

## Compatibility

- Blender 4.3 or newer
- No third-party Python packages required

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).
