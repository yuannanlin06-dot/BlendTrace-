# Privacy

BlendTrace v0.2.0 is designed to be offline and local-only.

## Data it reads

While recording, BlendTrace reads only the Blender runtime information needed for its visible features:

- the current undo-stack step name and index;
- the current active object's name;
- the current active object's world-space origin so the semantic cursor can be drawn in the 3D View;
- the current 3D View region/view state needed to project that point onto the screen.

## Data it does not read

BlendTrace v0.2.0 contains no code to read:

- operating-system mouse coordinates or global input events;
- clipboard contents;
- browser data or browser history;
- account credentials, passwords, tokens, cookies, or SSH keys;
- arbitrary files or folders on disk;
- email, contacts, cloud drives, or other applications.

## Networking and telemetry

BlendTrace v0.2.0 contains no networking code, telemetry, analytics, advertising SDK, AI/API integration, account system, or cloud-storage integration. It does not transmit recorded information.

The semantic cursor is a Blender viewport overlay. It is not a system cursor recorder.

## Storage

Trace items are kept in Blender runtime state for the current session. This version does not implement export, upload, synchronization, or background persistence.
