![HASS Build](https://github.com/mrpointblue/sonnenBatterie-Integration/workflows/hassfest/badge.svg) ![GitHub Downloads](https://img.shields.io/github/downloads/mrpointblue/sonnenBatterie-Integration/latest/total)

# SonnenBatterie Integration for Home Assistant

This custom integration allows you to monitor and control your SonnenBatterie system via Home Assistant. It provides detailed sensor data such as power consumption, production, and battery state.

## Development pre-release: 1.1.2-dev.2

[Download 1.1.2-dev.2](https://github.com/mrpointblue/sonnenBatterie-Integration/releases/tag/v1.1.2-dev.2).
This is a development pre-release. In HACS, enable pre-release versions in the download dialog
and select `1.1.2-dev.2`. For manual installation, extract the release ZIP into the HA configuration
directory so that the files are under `custom_components/sonnenbatterie`.
**Restart Home Assistant fully after updating** to load the changed Python code.

The 23 additional sensors are **disabled by default**. Open **Settings → Devices & services → Entities**,
filter by the SonnenBatterie integration, include disabled entities and enable the desired sensors.
Disabled sensors do not appear in Developer Tools → States. Entity names use your configured prefix.
If they are missing from the entity list, check the logs after restarting.
The diagnostic entity registration error found during testing is fixed in this release.

## Features
- Live power consumption and production data.
- Detailed power meter data.
- State of charge (SOC) monitoring for the battery.
- Energy import/export monitoring.
- Integrates custom prefix
- Write OperatingMode & power for charge or discharge
- Optional battery health and controller diagnostics.
- Timed site AC setpoints and grid/inverter/storage limits on supported firmware.

## Recommendation
- Best Dashbaord integration for energy flow with sonnenBatterie Integration>>
  https://github.com/flixlix/power-flow-card-plus

## Compatibility
This integration works with SonnenBatterie systems starting from the Eco8 generation and newer.
Actual known Hardware Systems (More possible):
- Eco 8.0
- Eco 8.13
- Eco 8.53
- Eco 9.53
- sonnenBatterie 10
- sonnenBatterie 10 Performance
- sonnenBatterie 10 Performance+

## Configuration of SonnenBatterie
1. Log in to your battery's dashboard.
2. Navigate to `Software Integration`.
3. Enable `JSON API for Reading`. If you want to control your battery system too, enable `JSON API for Writing`.
4. Copy the token provided for use in the Home Assistant UI.

<img width="1438" alt="Bildschirmfoto 2025-01-23 um 00 45 32" src="https://github.com/user-attachments/assets/25fd5801-0086-43df-82dd-cebf0da51496" />


## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=mrpointblue&repository=sonnenBatterie-Integration&category=integration)

1. Install through HACS, or download this repository and copy its
   `custom_components/sonnenbatterie` folder into
   `<HA configuration>/custom_components/sonnenbatterie`.
2. Restart Home Assistant.

## Configuration in Home Assistant
1. Go to `Settings` > `Integrations`.
2. Click `Add Integration` and search for `SonnenBatterie`.
3. Enter the IP address of your SonnenBatterie and the token obtained from the dashboard.
4. If you want: Create a custom prefix. For example use your serialnumber of the battery system. Default is "sonnen".

## Custom Card
Integration comes with a custom card to set Operating Mode, charge or discharge power (For control access, activate `API Write` in API settings)

<img width="447" alt="Bildschirmfoto 2025-01-28 um 23 25 55" src="https://github.com/user-attachments/assets/b4b2be9c-0ad9-4911-a16b-6726fb3b68c8" />


The integration copies the optional card to `www/sonnenbatteriecard.js`.
Add `/local/sonnenbatteriecard.js` as a JavaScript module under
Settings → Dashboards → Resources (advanced mode). Keep this resource URL for
future updates; do not register it twice. If an older URL contains `?v=...`,
remove that query suffix from the existing resource. After updating, reload the
integration and refresh the browser cache if the old card is still shown. If `www` was
created for the first time, restart HA to enable `/local` serving.
Then add the card to your dashboard:

```yaml
type: custom:sonnenbatterie-card
```

With one battery, the card selects it automatically and shows no battery selector.
With multiple batteries, a selector displays their Home Assistant device names.
Select the battery before sending an operating-mode or power command. No sensor
ID needs to be entered. Unavailable batteries cannot receive commands. The
selection stays in place during state updates; reopening the dashboard requires
selection again when multiple batteries exist. If the selected battery disappears,
commands remain disabled instead of switching to another battery.

Existing `entity` configurations remain supported as an initial selection.
`max_power_entity` is optional; it is used only if it belongs to the selected
battery. Otherwise the card looks up that battery's inverter-limit sensor.

Service example (use an actual entity ID from your installation):
```yaml
action: sonnenbatterie.set_em_operating_mode
data:
  entity_id: sensor.sonnen_ac_power
  mode: 1
```
Omitting `entity_id` is supported only when exactly one battery is loaded.
Commands that fail now report an error to Home Assistant and the card. Power
setpoints allow 0 W; the battery firmware must permit the requested command.

Modes:
- "1": "Manual",
- "2": "Self Consumption",
- "6": "Extension Mode",
- "10": "Time Of Use",
- "11": "Automatic optimization",

## Overview supported sensors

The following sensors can be read from various API endpoints. Each sensor includes the name, the key (key), the unit, and an optional device class (device_class).

---

### **Sensors from `/api/v2/latestdata`**
- House Consumption (`Consumption_W`): W (device_class: `power`)
- Solar Production (`Production_W`): W (device_class: `power`)
- Grid Feed-In (`GridFeedIn_W`): W (device_class: `power`)
- Battery State of Charge (`USOC`): % (device_class: `battery`)
- AC Power (`Pac_total_W`): W (device_class: `power`, positive = discharging, negative = charging)

---

### **Sensors from `/api/v2/status`**
- Apparent Output (`Apparent_output`): VA
- Backup Buffer (`BackupBuffer`): % (device_class: `battery`)
- Battery Charging (`BatteryCharging`): 1 when charging, 0 otherwise
- Battery Discharging (`BatteryDischarging`): 1 when discharging, 0 otherwise
- System Status (`SystemStatus`)
- AC Voltage (`Uac`): V (device_class: `voltage`)
- Battery Voltage (`Ubat`): V (device_class: `voltage`)
- Frequency (`Fac`): Hz
- Flow Consumption Battery (`FlowConsumptionBattery`): 1 if the home draws from the battery (else 0)
- Flow Consumption Grid (`FlowConsumptionGrid`): 1 if the home draws from the grid (else 0)
- Flow Consumption Production (`FlowConsumptionProduction`): 1 if the home uses solar directly (else 0)
- Flow Grid Battery (`FlowGridBattery`): 1 when charging the battery from the grid (else 0)
- Flow Production Battery (`FlowProductionBattery`): 1 when charging the battery from solar (else 0)
- Flow Production Grid (`FlowProductionGrid`): 1 when solar feeds into the grid (else 0)
- Grid Feed-In Power (`GridFeedIn_W`): W (device_class: `power`)
- Total Power Consumption (`Consumption_W`): W (device_class: `power`)
- Total Power Production (`Production_W`): W (device_class: `power`)
- Remaining State of Charge (`RSOC`): % (device_class: `battery`)
- State of Charge (`USOC`): % (device_class: `battery`)
- Total Active Power (`Pac_total_W`): W (device_class: `power`, positive = discharging, negative = charging)
- Discharge Not Allowed (`dischargeNotAllowed`)
- Generator Auto Start (`generator_autostart`)
- Timestamp (`Timestamp`) (device_class: `timestamp`)
- System Installation Status (`IsSystemInstalled`)
- Operating Mode (`OperatingMode`)

---

### **Sensors from `/api/v2/inverter`**
- AC Frequency (`fac`): Hz
- AC Current (`iac_total`): A (device_class: `current`)
- PV Power (`ppv`): W (device_class: `power`)
- Inverter Temperature (`tmax`): °C (device_class: `temperature`)
- PV Current (`ipv`): A (device_class: `current`)
- PV Voltage (`upv`): V (device_class: `voltage`)

---

### **Sensors from `/api/v2/configurations`**
- Operating Mode (`EM_OperatingMode`)
- Max Inverter Power (`IC_InverterMaxPower_w`): W (device_class: `power`)
- Power Factor Cos Phi (`NVM_PfcFixedCosPhi`)
- Software Version (`DE_Software`)
- Installed Batteries (`IC_BatteryModules`)

---

### **Sensors from `/api/v2/battery`**
- Battery Voltage (`systemdcvoltage`): V (device_class: `voltage`)
- System Current (`systemcurrent`): A (device_class: `current`)
- Charge Current Limit (`chargecurrentlimit`): A
- Discharge Current Limit (`dischargecurrentlimit`): A
- Full Charge Capacity (`fullchargecapacity`): Ah
- Remaining Capacity (`remainingcapacity`): Ah
- Maximum Cell Temperature (`maximumcelltemperature`): °C (device_class: `temperature`)
- Minimum Cell Temperature (`minimumcelltemperature`): °C (device_class: `temperature`)
- Charge Cycle Count (`cyclecount`)

---

### **Sensors from `/api/v2/powermeter`**

#### **Production Values**
- Production Power L1 (`w_l1`): W (device_class: `power`, direction: `production`)
- Production Power L2 (`w_l2`): W (device_class: `power`, direction: `production`)
- Production Power L3 (`w_l3`): W (device_class: `power`, direction: `production`)
- Production Total Power (`w_total`): W (device_class: `power`, direction: `production`)
- Production Current L1 (`a_l1`): A (device_class: `current`, direction: `production`)
- Production Current L2 (`a_l2`): A (device_class: `current`, direction: `production`)
- Production Current L3 (`a_l3`): A (device_class: `current`, direction: `production`)
- Production Voltage L1-N (`v_l1_n`): V (device_class: `voltage`, direction: `production`)
- Production Voltage L2-N (`v_l2_n`): V (device_class: `voltage`, direction: `production`)
- Production Voltage L3-N (`v_l3_n`): V (device_class: `voltage`, direction: `production`)
- Production Energy Exported (`kwh_exported`): kWh (device_class: `energy`, state_class: `total`, direction: `production`)
- Production Energy Imported (`kwh_imported`): kWh (device_class: `energy`, state_class: `total`, direction: `production`)

#### **Consumption Values**
- Consumption Power L1 (`w_l1`): W (device_class: `power`, direction: `consumption`)
- Consumption Power L2 (`w_l2`): W (device_class: `power`, direction: `consumption`)
- Consumption Power L3 (`w_l3`): W (device_class: `power`, direction: `consumption`)
- Consumption Total Power (`w_total`): W (device_class: `power`, direction: `consumption`)
- Consumption Current L1 (`a_l1`): A (device_class: `current`, direction: `consumption`)
- Consumption Current L2 (`a_l2`): A (device_class: `current`, direction: `consumption`)
- Consumption Current L3 (`a_l3`): A (device_class: `current`, direction: `consumption`)
- Consumption Voltage L1-N (`v_l1_n`): V (device_class: `voltage`, direction: `consumption`)
- Consumption Voltage L2-N (`v_l2_n`): V (device_class: `voltage`, direction: `consumption`)
- Consumption Voltage L3-N (`v_l3_n`): V (device_class: `voltage`, direction: `consumption`)
- Consumption Energy Exported (`kwh_exported`): kWh (device_class: `energy`, state_class: `total`, direction: `consumption`)
- Consumption Energy Imported (`kwh_imported`): kWh (device_class: `energy`, state_class: `total`, direction: `consumption`)

## Example YAML Configuration (Manual)
If you want a sensor for charge and discharge energy for using in energy dashboard, add the following to your `configuration.yaml` file:

```yaml
template:
  - sensor:
      - name: Sonnen Charge Power
        unique_id: sonnen_charge_power
        default_entity_id: sensor.sonnen_charge_power
        unit_of_measurement: W
        device_class: power
        state_class: measurement
        availability: "{{ is_number(states('sensor.sonnen_ac_power')) }}"
        state: "{{ [0, -(states('sensor.sonnen_ac_power') | float(0))] | max }}"
      - name: Sonnen Discharge Power
        unique_id: sonnen_discharge_power
        default_entity_id: sensor.sonnen_discharge_power
        unit_of_measurement: W
        device_class: power
        state_class: measurement
        availability: "{{ is_number(states('sensor.sonnen_ac_power')) }}"
        state: "{{ [0, states('sensor.sonnen_ac_power') | float(0)] | max }}"

sensor:
  - platform: integration
    source: sensor.sonnen_charge_power
    name: Sonnen Charge Energy
    unit_prefix: k
    round: 2
    method: trapezoidal
  - platform: integration
    source: sensor.sonnen_discharge_power
    name: Sonnen Discharge Energy
    unit_prefix: k
    round: 2
    method: trapezoidal
```

Use your actual source entity IDs. Replace legacy template definitions instead
of retaining both versions. Merge these sections with existing YAML sections.

## Troubleshooting
- **No sensor data:** Enable `JSON API for Reading` in the battery dashboard and check the configured IP address and token.
- **Charging or discharging fails:** Enable `JSON API for Writing`. Legacy power commands are time-limited outside manual mode (default 30 seconds); manual mode has no such timeout. VPP may reject commands, and PV affects the resulting battery flow on hybrid systems. Site commands require supported firmware/EM2. Check the Home Assistant logs for API errors.
- **Old card still displayed after updating:** Reload the integration or restart Home Assistant, then refresh the browser cache. Keep the resource URL `/local/sonnenbatteriecard.js`.

## Supported operating modes
The integration accepts modes **1, 2, 6, 10 and 11**. Mode 4 is not offered or accepted by the integration. Availability of the supported modes on a particular battery depends on its firmware and configuration.

For **sB10h**, use **11 — Automatic optimization** instead of mode 2 (Self Consumption). Mode 2 does not work for this model, as reported by the user. Select mode 11 in the control card or pass `mode: 11` to `sonnenbatterie.set_em_operating_mode`.

## Contribution
Feel free to open issues or create pull requests to contribute to this project.


## Additional sensors in 1.1.2-dev.2

All entries below are optional diagnostic entities, disabled by default. Existing entity identifiers
are preserved. Missing fields or endpoints are unavailable rather than replaced with zero.

| Sensor name (without prefix) | API source / field | Unit or meaning |
| --- | --- | --- |
| Battery State of Health | `/api/v2/battery` / `stateofhealth` | % |
| Full Charge Energy | `/api/v2/battery` / `fullchargecapacitywh` | Wh |
| Maximum Cell Voltage | `/api/v2/battery` / `maximumcellvoltage` | V |
| Minimum Cell Voltage | `/api/v2/battery` / `minimumcellvoltage` | V |
| Remaining Energy | `/api/v2/status` / `RemainingCapacity_Wh` | Wh |
| BMS State | `/api/v2/latestdata` / `ic_status → statebms` | Status |
| Controller State | `/api/v2/latestdata` / `ic_status → statecorecontrolmodule` | Status |
| Inverter State | `/api/v2/latestdata` / `ic_status → stateinverter` | Status |
| DC Shutdown Reason | `/api/v2/latestdata` / `ic_status → DC Shutdown Reason` | Active flag count |
| Standby Reason | `/api/v2/latestdata` / `ic_status → Standby Reason` | Active flag count |
| Full Charge Reason | `/api/v2/latestdata` / `ic_status → Full Charge Reason` | Active flag count |
| Setpoint Priority | `/api/v2/latestdata` / `ic_status → Setpoint Priority` | Active flag count |
| Microgrid Status | `/api/v2/latestdata` / `ic_status → Microgrid Status` | Active flag count |
| MISC Status Bits | `/api/v2/latestdata` / `ic_status → MISC Status Bits` | Active flag count |
| System Validation | `/api/v2/latestdata` / `ic_status → System Validation` | Active flag count |
| Eclipse Status | `/api/v2/latestdata` / `ic_status → Eclipse Led → Eclipse Status` | Status |
| Site Charge Current Limit | `/api/v2/site/limits` / `i_bess_storage_max_charge_limit` | A |
| Site Discharge Current Limit | `/api/v2/site/limits` / `i_bess_storage_max_discharge_limit` | A |
| Site Inverter Export Limit | `/api/v2/site/limits` / `p_bess_inv_max_export_limit` | W |
| Site Inverter Import Limit | `/api/v2/site/limits` / `p_bess_inv_max_import_limit` | W |
| Site Grid Export Limit | `/api/v2/site/limits` / `p_gcp_max_export_limit` | W |
| Site Grid Import Limit | `/api/v2/site/limits` / `p_gcp_max_import_limit` | W |
| Site AC Setpoint | `/api/v2/site/setpoint` / `p_bess_inv_export_import_setpoint` | W |

Diagnostic groups count flags that are true and expose the complete group in their `flags` attribute.
These counts are not error severity: flags such as `None`, `Disabled` or normal operating states
may also be true. Field availability depends on battery model and firmware.

## Timed site actions

`sonnenbatterie.set_site_setpoint` and `sonnenbatterie.set_site_limits` accept `duration`
in whole seconds (1–86400, default 30). The one-day maximum is an integration limit.
Use `entity_id` to select an entity belonging to the battery; it is required with multiple batteries.
The corresponding site read endpoint is checked before a write. This verifies read availability,
not write permission. Unsupported or rejected commands fail without falling back to legacy controls.
The manufacturer describes EM2 requirements but does not provide a complete model compatibility list.

```yaml
action: sonnenbatterie.set_site_setpoint
data:
  entity_id: sensor.your_battery_entity
  watts: 1500
  duration: 30
```

Replace the example entity ID with an existing entity of your battery.
Positive watts means **AC import**, negative watts means **AC export**, opposite to `Pac_total_W`.
Zero is an active command, not cancellation. On hybrid systems PV affects actual battery power;
the AC setpoint is not a direct battery-power target. The command expires after its duration.

```yaml
action: sonnenbatterie.set_site_limits
data:
  entity_id: sensor.your_battery_entity
  p_gcp_max_import_limit: 3000
  p_gcp_max_export_limit: 2000
  duration: 60
```

At least one limit is required. Zero means a zero limit, not clearing the limit.
Device constraints and priorities continue to apply.

| Limit field | Unit | Meaning |
| --- | --- | --- |
| `i_bess_storage_max_charge_limit` | A | Maximum storage charge current |
| `i_bess_storage_max_discharge_limit` | A | Maximum storage discharge current |
| `p_bess_inv_max_export_limit` | W | Maximum inverter AC export |
| `p_bess_inv_max_import_limit` | W | Maximum inverter AC import |
| `p_gcp_max_export_limit` | W | Maximum site grid export |
| `p_gcp_max_import_limit` | W | Maximum site grid import |

IO/standby, ToU changes and migration to site configuration writes are deferred.

### Validation status

The user confirmed that the additional entities appear in Home Assistant 2026.11.1 after the
EntityCategory fix. Local validation covers 19 isolated Python regression tests, including enum
category type, missing diagnostics, selected-battery routing, signed setpoints, durations and rejection
of unsupported site endpoints. These tests stub Home Assistant and do not replace hardware testing.
Site writes and real battery responses have not yet been confirmed. JavaScript card tests were not
run locally because Node.js was unavailable; the card is unchanged. Automated CI results are separate.
