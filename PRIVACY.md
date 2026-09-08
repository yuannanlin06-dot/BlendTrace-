# Privacy

BlendTrace v0.1.1 is designed as an offline-first Blender extension.

## Data it reads

While recording is active, BlendTrace reads:

- the active undo-stack step name and index exposed by Blender;
- the name of the active Blender object.

These values are used only to display the local timeline inside the current Blender session.

## Data it does not access or transmit

This release contains no code for:

- network connections or HTTP requests;
- telemetry or analytics;
- AI or cloud APIs;
- API keys, tokens, passwords or account credentials;
- browser history or browser data;
- clipboard access;
- arbitrary scanning of files or directories;
- background uploads.

BlendTrace v0.1.1 does not transmit user data.

## Future versions

If a future version introduces optional network or AI features, those features should be documented separately, request only the permissions they need, and remain distinguishable from the offline recorder.
