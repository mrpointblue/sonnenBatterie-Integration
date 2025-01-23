# SonnenBatterie Integration for Home Assistant

This custom integration allows you to monitor and control your SonnenBatterie system via Home Assistant. It provides detailed sensor data such as power consumption, production, and battery state.

## Features
- Live power consumption and production data.
- Deatiled power meter data.
- State of charge (SOC) monitoring for the battery.
- Energy import/export monitoring.
- integartes entity names with "sonnen.*" 

## Not Supported
- Writing not possible / Only Reading

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
1. Clone this repository into your Home Assistant `custom_components` directory:
   ```bash
   git clone https://github.com/mrpointblue/sonnenBatterie custom_components/sonnen_battery
   ```
2. Restart Home Assistant.

## Configuration in Home Assistant
1. Go to `Settings` > `Integrations`.
2. Click `Add Integration` and search for `SonnenBatterie`.
3. Enter the IP address of your SonnenBatterie and the token obtained from the dashboard.

## Sensors Provided
This integration provides the following sensors:

- **Charge Energy**
  - Measures the energy used to charge the battery in kWh.
- **Discharge Energy**
  - Measures the energy discharged from the battery in kWh.
- **Battery State of Charge**
  - Displays the current charge percentage of the battery.
- **Production Energy Exported**
  - Tracks the total energy exported to the grid in kWh.
- **Production Energy Imported**
  - Tracks the total energy imported from the grid in kWh.

## Example YAML Configuration (Manual)
If you prefer manual configuration, add the following to your `configuration.yaml` file:

```yaml
sensor:
  - platform: template
    sensors:
      sonnen_charge_energy:
        unique_id: "sonnen_charge_energy"
        unit_of_measurement: "kWh"
        device_class: energy
        state_class: total_increasing
        state: >
          {% if states('sensor.sonnen_ac_power')|float < 0 %}
            {{ (states('sensor.sonnen_ac_power')|float * -1 / 1000) | round(2) }}
          {% else %}
            0
          {% endif %}
        attributes:
          direction: "charge"

      sonnen_discharge_energy:
        unique_id: "sonnen_discharge_energy"
        unit_of_measurement: "kWh"
        device_class: energy
        state_class: total_increasing
        state: >
          {% if states('sensor.sonnen_ac_power')|float > 0 %}
            {{ (states('sensor.sonnen_ac_power')|float / 1000) | round(2) }}
          {% else %}
            0
          {% endif %}
        attributes:
          direction: "discharge"
```

## Known Issues
- Ensure the `JSON API for Reading` is enabled in the SonnenBatterie dashboard.
- If no data appears, verify the IP address and token entered in the integration.

## Contribution
Feel free to open issues or create pull requests to contribute to this project.
