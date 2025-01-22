# Sonnen Battery Energy Sensors Integration

This repository contains a custom Home Assistant integration to retrieve and display energy data from a Sonnen battery system. The integration includes sensors for charge and discharge energy and works seamlessly with the Home Assistant energy dashboard.

---

## Features

- **Charge Energy Sensor**: Tracks the energy charged into the battery in kWh.
- **Discharge Energy Sensor**: Tracks the energy discharged from the battery in kWh.
- Seamless integration with Home Assistant's energy dashboard.

## Installation

1. **Manual Installation**:
   - Download the contents of this repository.
   - Place the files in your `custom_components/sonnen_battery` directory.

2. **Via HACS**:
   - Add this repository to HACS as a custom repository.
   - Install the integration through HACS.

3. Restart Home Assistant after installation.

## Configuration

### Configuration via UI

1. Navigate to **Settings > Devices & Services** in Home Assistant.
2. Click **Add Integration**.
3. Search for `Sonnen Battery` and follow the on-screen instructions to configure the IP and Token.

### YAML Configuration (Optional)

Below is an example YAML configuration for template sensors:

```yaml
# Example configuration for Sonnen battery charge and discharge energy sensors
sensor:
  - name: "sonnen_charge_energy"
    unique_id: "sonnen_charge_energy"
    unit_of_measurement: "kWh"
    device_class: energy
    state_class: total_increasing
    state: >
      {% if states('sensor.sonnen_ac_power')|float < 0 %}
        {{ (states('sensor.sonnen_ac_power')|float * -1 / 1000 / 60 / 60) | round(2) }}
      {% else %}
        0
      {% endif %}
    attributes:
      direction: "charge"

  - name: "sonnen_discharge_energy"
    unique_id: "sonnen_discharge_energy"
    unit_of_measurement: "kWh"
    device_class: energy
    state_class: total_increasing
    state: >
      {% if states('sensor.sonnen_ac_power')|float > 0 %}
        {{ (states('sensor.sonnen_ac_power')|float / 1000 / 60 / 60) | round(2) }}
      {% else %}
        0
      {% endif %}
    attributes:
      direction: "discharge"
```

## Usage

- After configuring the integration, you will see the following sensors:
  - `sensor.sonnen_charge_energy`: Displays the total energy charged into the battery.
  - `sensor.sonnen_discharge_energy`: Displays the total energy discharged from the battery.
- These sensors can be added to the energy dashboard for detailed energy monitoring.

## Troubleshooting

### Common Issues

- **State `unavailable`**: Ensure the IP address and token are correctly configured.
- **Energy Dashboard Integration**: Make sure the `state_class` and `device_class` are correctly set in the sensor configuration.

### Logs

- Check Home Assistant logs under **Settings > System > Logs** for any error messages related to the integration.

## Contributing

Contributions are welcome! If you encounter issues or have ideas for new features, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

