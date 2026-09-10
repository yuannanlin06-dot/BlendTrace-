# Security

BlendTrace v0.2.0 follows a minimal-permission, offline-first design.

- No network access is implemented.
- No third-party Python packages are bundled or required.
- No subprocess, shell-command, dynamic-code download, or remote execution feature is implemented.
- No arbitrary file read/write feature is implemented.
- No credential, clipboard, browser, or global-input access is implemented.
- The semantic cursor is drawn only inside Blender's 3D View using Blender's drawing APIs.
- Tracking failures are handled without modifying the user's scene.

For important Blender projects, normal backup/versioning practices are still recommended because any third-party add-on runs inside Blender's process and software can contain unforeseen defects.
