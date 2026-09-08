# BlendTrace

**BlendTrace** is a tiny, offline Blender extension that turns Blender's undoable modeling history into a readable timeline.

> See how a model was made — not just the final model.

## What v0.1.1 does

- Adds a **BlendTrace** tab to the 3D View sidebar (`N`).
- Starts and stops local operation recording.
- Reads Blender's current undo-stack step and turns it into a simple timeline.
- Shows the active object name for each captured step.
- Adds short Chinese explanations for common modeling operations such as Move, Scale, Rotate, Extrude, Inset, Bevel and Loop Cut.
- Runs locally with **no network access, no account, no API key, no analytics and no cloud storage**.

## Install

1. Download the install ZIP from the repository release, or zip the extension files with `__init__.py` and `blender_manifest.toml` at the archive root.
2. In Blender, open **Edit → Preferences → Extensions/Add-ons**.
3. Choose **Install from Disk**.
4. Select the BlendTrace install ZIP and enable it.
5. Return to the 3D View and press `N`.
6. Open the **BlendTrace** tab and click **Start Recording**.
7. Perform a few undoable modeling operations and watch the timeline update.

## Privacy

BlendTrace v0.1.1 is intentionally offline. It reads only the Blender runtime information needed for the visible timeline: the current undo-step label/index and the active object's name.

It does **not** include networking code, telemetry, analytics, AI/API integrations, clipboard access, browser access, credential access, or arbitrary file scanning. It does not transmit data.

See [PRIVACY.md](PRIVACY.md) and [SECURITY.md](SECURITY.md).

## Current limitations

This is a proof of concept, not a full event recorder. Blender's undo stack is not a complete stream of every UI action, so this version does not capture every click, selection change, exact mouse path, modal sub-step, or complete operator parameter set. It is designed to validate the core idea before deeper event capture is added.

## Compatibility

- Blender 4.3 or newer
- No third-party Python packages required

## Project status

Early prototype / MVP. The next logical milestone is richer semantic capture and visual step indicators without sacrificing the offline-first privacy model.

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).
