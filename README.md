![HASS Build](https://github.com/mrpointblue/sonnenBatterie-Integration/workflows/hassfest/badge.svg)
[![hacs][hacs-shield]][hacs]

# SonnenBatterie Integration for Home Assistant

This custom integration allows you to monitor and control your SonnenBatterie system via Home Assistant. It provides detailed sensor data such as power consumption, production, and battery state.

## Features
- Live power consumption and production data.
- Detailed power meter data.
- State of charge (SOC) monitoring for the battery.
- Energy import/export monitoring.
- Integrates custom prefix
- Write OperatingMode & power for charge or discharge

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
3. Enable `JSON API for Reading`.
4. Copy the token provided for use in the Home Assistant UI.

<img width="1438" alt="Bildschirmfoto 2025-01-23 um 00 45 32" src="https://github.com/user-attachments/assets/25fd5801-0086-43df-82dd-cebf0da51496" />


## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=mrpointblue&repository=sonnenBatterie-Integration&category=integration)

1. Clone this repository into your Home Assistant `custom_components` directory:
   ```bash
   git clone https://github.com/mrpointblue/sonnenBatterie custom_components/sonnen_battery
   ```
2. Restart Home Assistant.

## Configuration in Home Assistant
1. Go to `Settings` > `Integrations`.
2. Click `Add Integration` and search for `SonnenBatterie`.
3. Enter the IP address of your SonnenBatterie and the token obtained from the dashboard.
4. If you want: Create a custom prefix. For example use your serialnumber of the battery system. Default is "sonnen".

## Custom Card
Integration comes with a custom card to set Operating Mode, charge or discharge power

<img width="447" alt="Bildschirmfoto 2025-01-28 um 23 25 55" src="https://github.com/user-attachments/assets/b4b2be9c-0ad9-4911-a16b-6726fb3b68c8" />


Add the card manually to your dashboard.

```yaml
type: custom:sonnenbatterie-card

```
service example via YAML:
action: sonnenbatterie.set_em_operating_mode
mode: 1

Modes:
- "1": "Manuall",
- "2": "Self Consumption",
- "6": "Extension Mode",
- "10": "Time Of Use",

## Overview supported sensors

The following sensors can be read from various API endpoints. Each sensor includes the name, the key (key), the unit, and an optional device class (device_class).

---

### **Sensors from `/api/v2/latestdata`**
- House Consumption (`Consumption_W`): W (device_class: `power`)
- Solar Production (`Production_W`): W (device_class: `power`)
- Grid Feed-In (`GridFeedIn_W`): W (device_class: `power`)
- Battery State of Charge (`USOC`): % (device_class: `battery`)
- AC Power (`Pac_total_W`): W (device_class: `power`)

---

### **Sensors from `/api/v2/status`**
- Apparent Output (`Apparent_output`): VA
- Backup Buffer (`BackupBuffer`): % (device_class: `battery`)
- Battery Charging (`BatteryCharging`)
- Battery Discharging (`BatteryDischarging`)
- System Status (`SystemStatus`)
- AC Voltage (`Uac`): V (device_class: `voltage`)
- Battery Voltage (`Ubat`): V (device_class: `voltage`)
- Frequency (`Fac`): Hz
- Flow Consumption Battery (`FlowConsumptionBattery`)
- Flow Consumption Grid (`FlowConsumptionGrid`)
- Flow Consumption Production (`FlowConsumptionProduction`)
- Flow Grid Battery (`FlowGridBattery`)
- Flow Production Battery (`FlowProductionBattery`)
- Flow Production Grid (`FlowProductionGrid`)
- Grid Feed-In Power (`GridFeedIn_W`): W (device_class: `power`)
- Total Power Consumption (`Consumption_W`): W (device_class: `power`)
- Total Power Production (`Production_W`): W (device_class: `power`)
- Remaining State of Charge (`RSOC`): % (device_class: `battery`)
- State of Charge (`USOC`): % (device_class: `battery`)
- Total Active Power (`Pac_total_W`): W (device_class: `power`)
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
- Battery Current (`ibat`): A (device_class: `current`)
- PV Current (`ipv`): A (device_class: `current`)
- Microgrid Power (`pac_microgrid`): W (device_class: `power`)
- Total Power (`pac_total`): W (device_class: `power`)
- Battery Power (`pbat`): W (device_class: `power`)
- Apparent Power Total (`sac_total`)
- AC Voltage (`uac`): V (device_class: `voltage`)
- Battery Voltage (`ubat`): V (device_class: `voltage`)
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
- Full Charge Capacity (`fullchargecapacity`): Ah (device_class: `energy`)
- Remaining Capacity (`remainingcapacity`): Ah (device_class: `energy`)
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
- Production Energy Exported (`kwh_exported`): kWh (device_class: `energy`, state_class: `total_increasing`, direction: `production`)
- Production Energy Imported (`kwh_imported`): kWh (device_class: `energy`, state_class: `total_increasing`, direction: `production`)

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
- Consumption Energy Exported (`kwh_exported`): kWh (device_class: `energy`, state_class: `total_increasing`, direction: `consumption`)
- Consumption Energy Imported (`kwh_imported`): kWh (device_class: `energy`, state_class: `total_increasing`, direction: `consumption`)

## Example YAML Configuration (Manual)
If you want a sensor for charge and discharge energy for using in energy dashboard, add the following to your `configuration.yaml` file:

```yaml (Ensure to change the prefix if using own customized prefix)
sensor:
  - name: "Sonnen Charge Power"
      unique_id: "sonnen_charge_power"
      unit_of_measurement: "W"
      device_class: power
      state_class: measurement
      state: >
        {% if states('sensor.sonnen_ac_power') | float < 0 %}
          {{ (states('sensor.sonnen_ac_power') | float) | abs }}
        {% else %}
          0
        {% endif %}

    - name: "Sonnen Discharge Power"
      unique_id: "sonnen_discharge_power"
      unit_of_measurement: "W"
      device_class: power
      state_class: measurement
      state: >
        {% if states('sensor.sonnen_ac_power') | float > 0 %}
          {{ (states('sensor.sonnen_ac_power') | float) }}
        {% else %}
          0
        {% endif %}

    - platform: integration
      source: sensor.sonnen_charge_power
      name: "Sonnen Charge Energy"
      unit_prefix: k
      round: 2
      method: trapezoidal

    - platform: integration
      source: sensor.sonnen_discharge_power
      name: "Sonnen Discharge Energy"
      unit_prefix: k
      round: 2
      method: trapezoidal

```

## Known Issues
- No Data >> Ensure the `JSON API for Reading` is enabled in the SonnenBatterie dashboard.
- No Data >> If no data appears, verify the IP address and token entered in the integration.
- Charging / Discharging not possible Ensure the `JSON API for Write` is enabled in the SonnenBatterie dashboard.
- Mode 11 and 4 not supported by API
- The current card can only control one battery. Multiple batteries are not supported and may cause control issues.

## Contribution
Feel free to open issues or create pull requests to contribute to this project.
