# 1.1.1 — stable

- Remove automatic reauthentication on HTTP 401/403 and the reauthentication flow.
- Keep the stored token unchanged; retry failed endpoints through normal polling.
- Continue reading successful endpoints when another endpoint rejects access.
- Keep real HTTP failures visible as unavailable data or failed commands.
- Resource URL remains `/local/sonnenbatteriecard.js`.

# 1.1.0 — stable

- Promote the compatibility and battery-selection changes from rc.1 and rc.2 to stable.
- Keep the dashboard JavaScript module URL permanently at `/local/sonnenbatteriecard.js`.
- Existing resources and cards can be reused; no card recreation is required.
- The user confirmed the card test. JavaScript regression checks and 14 isolated
  Python tests pass; these do not replace validation across all battery models.

# 1.1.0-rc.2 — battery selection in the control card

- Automatically select the only battery; show a device-name selector only for multiple batteries.
- Resolve targets through HA registry membership without requiring sensor IDs.
- Block commands for missing/unavailable selections and preserve existing entity presets.
- Display the inverter limit belonging to the selected battery.
- Add JavaScript regression checks for discovery, selection and command routing.

# 1.1.0-rc.1 — compatibility pre-release

- Use SensorEntity native values, preserve energy precision and parse timestamps.
- Declare API endpoints explicitly and report unavailable endpoints correctly.
- Retry setup after total connection failure; support token reauthentication.
- Reuse Home Assistant HTTP sessions with bounded request timeouts.
- Reload on options changes; consolidate the options flow.
- Freeze legacy entity/device identity before changes to host or name prefix.
- Resolve command targets per call; reject ambiguous multiple-battery commands.
- Propagate command errors and accept zero-watt setpoints consistently.
- Remove services after unloading the last battery.
- Find publishable sensors via the entity registry rather than a name prefix.
- Add card target configuration and refresh its optional power label.
- Move translations to translations/ and provide English and German forms.
- Correct installation instructions and modernize template YAML examples.
- Add isolated regression tests and a CI workflow for them.

## Installation and validation notes

Version 1.1.0 is the planned minor release after stable 1.0.10, combining
compatibility fixes with new control/configuration capabilities. This is a
release candidate for testing. Version 1.0.10 remains the stable release.

The optional card is copied in an executor. Its resource must be configured
manually as documented in README; existing resource registrations remain usable.

Local validation: 14 isolated unittest cases pass, Python syntax compilation,
JSON parsing and git diff whitespace checks pass. Home Assistant interfaces are
stubbed in these tests. HA 2026.9.3 runtime, hassfest and real battery commands
have not been executed locally. Before release, test setup, polling, options
reload, card resource loading, target selection and API writes on a real device.
