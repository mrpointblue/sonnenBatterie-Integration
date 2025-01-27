# Domain name for the integration
DOMAIN = "sonnenbatterie"
DEFAULT_PREFIX = "sonnen"

# Definition of sensors and their corresponding keys
SENSORS = [
    # Sensors from /api/v2/latestdata
    {"name": "House Consumption", "key": "Consumption_W", "unit": "W", "device_class": "power"},
    {"name": "Solar Production", "key": "Production_W", "unit": "W", "device_class": "power"},
    {"name": "Grid Feed-In", "key": "GridFeedIn_W", "unit": "W", "device_class": "power"},
    {"name": "Battery State of Charge", "key": "USOC", "unit": "%", "device_class": "battery"},
    {"name": "AC Power", "key": "Pac_total_W", "unit": "W", "device_class": "power"},

    # Sensors from /api/v2/status
    {"name": "Apparent Output", "key": "Apparent_output", "unit": "VA", "device_class": None},
    {"name": "Backup Buffer", "key": "BackupBuffer", "unit": "%", "device_class": "battery"},
    {"name": "Battery Charging", "key": "BatteryCharging", "unit": None, "device_class": None},
    {"name": "Battery Discharging", "key": "BatteryDischarging", "unit": None, "device_class": None},
    {"name": "System Status", "key": "SystemStatus", "unit": None, "device_class": None},
    {"name": "AC Voltage", "key": "Uac", "unit": "V", "device_class": "voltage"},
    {"name": "Battery Voltage", "key": "Ubat", "unit": "V", "device_class": "voltage"},
    {"name": "Frequency", "key": "Fac", "unit": "Hz", "device_class": None},
    {"name": "Flow Consumption Battery", "key": "FlowConsumptionBattery", "unit": None, "device_class": None},
    {"name": "Flow Consumption Grid", "key": "FlowConsumptionGrid", "unit": None, "device_class": None},
    {"name": "Flow Consumption Production", "key": "FlowConsumptionProduction", "unit": None, "device_class": None},
    {"name": "Flow Grid Battery", "key": "FlowGridBattery", "unit": None, "device_class": None},
    {"name": "Flow Production Battery", "key": "FlowProductionBattery", "unit": None, "device_class": None},
    {"name": "Flow Production Grid", "key": "FlowProductionGrid", "unit": None, "device_class": None},
    {"name": "Grid Feed-In Power", "key": "GridFeedIn_W", "unit": "W", "device_class": "power"},
    {"name": "Total Power Consumption", "key": "Consumption_W", "unit": "W", "device_class": "power"},
    {"name": "Total Power Production", "key": "Production_W", "unit": "W", "device_class": "power"},
    {"name": "Remaining State of Charge", "key": "RSOC", "unit": "%", "device_class": "battery"},
    {"name": "State of Charge", "key": "USOC", "unit": "%", "device_class": "battery"},
    {"name": "Total Active Power", "key": "Pac_total_W", "unit": "W", "device_class": "power"},
    {"name": "Discharge Not Allowed", "key": "dischargeNotAllowed", "unit": None, "device_class": None},
    {"name": "Generator Auto Start", "key": "generator_autostart", "unit": None, "device_class": None},
    {"name": "Timestamp", "key": "Timestamp", "unit": None, "device_class": "timestamp"},
    {"name": "System Installation Status", "key": "IsSystemInstalled", "unit": None, "device_class": None},
    {"name": "Operating Mode", "key": "OperatingMode", "unit": None, "device_class": None},

    # Sensors from /api/v2/inverter
    {"name": "AC Frequency", "key": "fac", "unit": "Hz", "device_class": None},
    {"name": "AC Current", "key": "iac_total", "unit": "A", "device_class": "current"},
    {"name": "PV Power", "key": "ppv", "unit": "W", "device_class": "power"},
    {"name": "Inverter Temperature", "key": "tmax", "unit": "°C", "device_class": "temperature"},

    # Sensors from /api/v2/configurations
    {"name": "Operating Mode", "key": "EM_OperatingMode", "unit": None, "device_class": None},
    {"name": "Max Inverter Power", "key": "IC_InverterMaxPower_w", "unit": "W", "device_class": "power"},
    {"name": "Power Factor Cos Phi", "key": "NVM_PfcFixedCosPhi", "unit": None, "device_class": None},
    {"name": "Software Version", "key": "DE_Software", "unit": None, "device_class": None},
    {"name": "Installed Batterys", "key": "IC_BatteryModules", "unit": None, "device_class": None},

    # Sensors from /api/v2/battery
    {"name": "Battery Voltage", "key": "systemdcvoltage", "unit": "V", "device_class": "voltage"},
    {"name": "System Current", "key": "systemcurrent", "unit": "A", "device_class": "current"},
    {"name": "Charge Current Limit", "key": "chargecurrentlimit", "unit": "A", "device_class": None},
    {"name": "Discharge Current Limit", "key": "dischargecurrentlimit", "unit": "A", "device_class": None},
    {"name": "Full Charge Capacity", "key": "fullchargecapacity", "unit": "Ah", "device_class": "energy"},
    {"name": "Remaining Capacity", "key": "remainingcapacity", "unit": "Ah", "device_class": "energy"},
    {"name": "Maximum Cell Temperature", "key": "maximumcelltemperature", "unit": "°C", "device_class": "temperature"},
    {"name": "Minimum Cell Temperature", "key": "minimumcelltemperature", "unit": "°C", "device_class": "temperature"},
    {"name": "Charge Cycle Count", "key": "cyclecount", "unit": None, "device_class": None},

    #sensors from /api/v2/powermeter
    # Production Values
    {"name": "Production Power L1", "key": "w_l1", "unit": "W", "device_class": "power", "direction": "production"},
    {"name": "Production Power L2", "key": "w_l2", "unit": "W", "device_class": "power", "direction": "production"},
    {"name": "Production Power L3", "key": "w_l3", "unit": "W", "device_class": "power", "direction": "production"},
    {"name": "Production Total Power", "key": "w_total", "unit": "W", "device_class": "power", "direction": "production"},
    {"name": "Production Current L1", "key": "a_l1", "unit": "A", "device_class": "current", "direction": "production"},
    {"name": "Production Current L2", "key": "a_l2", "unit": "A", "device_class": "current", "direction": "production"},
    {"name": "Production Current L3", "key": "a_l3", "unit": "A", "device_class": "current", "direction": "production"},
    {"name": "Production Voltage L1-N", "key": "v_l1_n", "unit": "V", "device_class": "voltage", "direction": "production"},
    {"name": "Production Voltage L2-N", "key": "v_l2_n", "unit": "V", "device_class": "voltage", "direction": "production"},
    {"name": "Production Voltage L3-N", "key": "v_l3_n", "unit": "V", "device_class": "voltage", "direction": "production"},
    {"name": "Production Energy Exported", "key": "kwh_exported", "unit": "kWh", "device_class": "energy", "state_class": "total_increasing", "direction": "production"},
    {"name": "Production Energy Imported", "key": "kwh_imported", "unit": "kWh", "device_class": "energy", "state_class": "total_increasing", "direction": "production"},

    # Consumption Values
    {"name": "Consumption Power L1", "key": "w_l1", "unit": "W", "device_class": "power", "direction": "consumption"},
    {"name": "Consumption Power L2", "key": "w_l2", "unit": "W", "device_class": "power", "direction": "consumption"},
    {"name": "Consumption Power L3", "key": "w_l3", "unit": "W", "device_class": "power", "direction": "consumption"},
    {"name": "Consumption Total Power", "key": "w_total", "unit": "W", "device_class": "power", "direction": "consumption"},
    {"name": "Consumption Current L1", "key": "a_l1", "unit": "A", "device_class": "current", "direction": "consumption"},
    {"name": "Consumption Current L2", "key": "a_l2", "unit": "A", "device_class": "current", "direction": "consumption"},
    {"name": "Consumption Current L3", "key": "a_l3", "unit": "A", "device_class": "current", "direction": "consumption"},
    {"name": "Consumption Voltage L1-N", "key": "v_l1_n", "unit": "V", "device_class": "voltage", "direction": "consumption"},
    {"name": "Consumption Voltage L2-N", "key": "v_l2_n", "unit": "V", "device_class": "voltage", "direction": "consumption"},
    {"name": "Consumption Voltage L3-N", "key": "v_l3_n", "unit": "V", "device_class": "voltage", "direction": "consumption"},
    {"name": "Consumption Energy Exported", "key": "kwh_exported", "unit": "kWh", "device_class": "energy", "state_class": "total_increasing", "direction": "consumption"},
    {"name": "Consumption Energy Imported", "key": "kwh_imported", "unit": "kWh", "device_class": "energy", "state_class": "total_increasing", "direction": "consumption"},
]

# Mapping for EM_OperatingMode translation
OPERATING_MODES = {
    "1": "Manuell",
    "2": "Eigenverbrauchsoptimierung",
    "4": "Testbetrieb",
    "6": "Erweiterungsmodus",
    "10": "Time Of Use",
}
