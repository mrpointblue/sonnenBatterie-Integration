class SonnenBatteryCard extends HTMLElement {
    setConfig(config) {
        this.config = config;
    }

    set hass(hass) {
        if (!this.content) {
            this.innerHTML = `
                <style>
                    ha-card {
                        padding: 16px;
                        border-radius: 10px;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                        background-color: var(--card-background-color, white);
                        color: var(--primary-text-color, black);
                    }

                    .header {
                        font-size: 1.5em;
                        font-weight: bold;
                        margin-bottom: 16px;
                    }

                    .row {
                        display: flex;
                        align-items: center;
                        margin-bottom: 16px;
                        gap: 12px;
                    }

                    label {
                        font-size: 1em;
                        font-weight: 500;
                        flex: 1;
                    }

                    select, input {
                        flex: 2;
                        padding: 8px;
                        font-size: 1em;
                        border: 1px solid var(--divider-color, #ccc);
                        border-radius: 5px;
                        background-color: var(--input-background-color, var(--card-background-color, white));
                        color: var(--primary-text-color, black);
                    }

                    button {
                        padding: 8px 12px;
                        font-size: 1em;
                        font-weight: bold;
                        color: var(--text-primary-color, white);
                        background-color: var(--primary-color, #007bff);
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                        transition: background-color 0.3s ease;
                    }

                    button:hover {
                        background-color: var(--primary-color-hover, #0056b3);
                    }

                    .section {
                        margin-bottom: 24px;
                    }

                    .max-power {
                        font-size: 0.9em;
                        color: var(--secondary-text-color, gray);
                        margin-top: -12px;
                        margin-bottom: 16px;
                    }
                </style>

                <ha-card>
                    <div class="header">Sonnen Battery Control</div>

                    <!-- Operating Mode Section -->
                    <div class="section">
                        <div class="row">
                            <label for="em_operating_mode">Betriebsmodus:</label>
                            <select id="em_operating_mode">
                                <option value="1">Manuell</option>
                                <option value="2">Eigenverbrauchsoptimierung</option>
                                <option value="6">Erweiterungsmodus</option>
                                <option value="10">Time Of Use</option>
                            </select>
                        </div>
                        <button id="set_em_mode">Modus Anwenden</button>
                    </div>

                    <!-- Power and Direction Section -->
                    <div class="section">
                        <div class="row">
                            <label for="direction">Richtung:</label>
                            <select id="direction">
                                <option value="charge">Laden</option>
                                <option value="discharge">Entladen</option>
                            </select>
                        </div>

                        <div class="row">
                            <label for="watts">Leistung (W):</label>
                            <input type="number" id="watts" min="0" value="1000" />
                        </div>
                        <div id="max_power_label" class="max-power">Maximale Leistung: Lade...</div>

                        <button id="set_power">Leistung Anwenden</button>
                    </div>
                </ha-card>
            `;
            this.content = this.querySelector('ha-card');

            const maxPowerLabel = this.querySelector("#max_power_label");

            // Hole die maximale Leistung und aktualisiere das Label
            this._updateMaxPowerLabel(hass, maxPowerLabel);

            // Event-Handler für Betriebsmodus
            this.querySelector('#set_em_mode').addEventListener('click', () => {
                const emMode = parseInt(this.querySelector('#em_operating_mode').value, 10);
                hass.callService('sonnenbatterie', 'set_em_operating_mode', {
                    mode: emMode,
                }).then(() => {
                    alert('Modus erfolgreich angewendet!');
                }).catch(() => {
                    alert('Fehler beim Anwenden des Modus!');
                });
            });

            // Event-Handler für Leistung und Richtung
            this.querySelector('#set_power').addEventListener('click', () => {
                const direction = this.querySelector('#direction').value;
                const watts = parseInt(this.querySelector('#watts').value, 10);
                hass.callService('sonnenbatterie', 'set_battery_power', {
                    direction: direction,
                    watts: watts,
                }).then(() => {
                    alert('Leistung erfolgreich angewendet!');
                }).catch(() => {
                    alert('Fehler beim Anwenden der Leistung!');
                });
            });
        }
    }

    _updateMaxPowerLabel(hass, label) {
        const maxPowerEntity = 'sensor.sonnen_max_inverter_power';
        const state = hass.states[maxPowerEntity];

        if (state && state.state) {
            label.textContent = `Maximale Leistung: ${state.state} W`;
        } else {
            label.textContent = "Maximale Leistung: Nicht verfügbar";
        }
    }

    getCardSize() {
        return 3;
    }
}

customElements.define('sonnenbatterie-card', SonnenBatteryCard);