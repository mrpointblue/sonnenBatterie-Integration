class SonnenBatteryCard extends HTMLElement {
    // Konfigurationsmethode
    setConfig(config) {
        console.log("Konfiguration empfangen:", config);
        this.config = config; // Speichere die Konfiguration
    }

    // Wird aufgerufen, wenn Home Assistant-Daten aktualisiert werden
    set hass(hass) {
        if (!this.content) {
            // Initialisiere die Karte
            this.innerHTML = `
                <ha-card header="${this._localize(hass, 'ui.card_title', 'Sonnen Battery Control')}">
                    <div class="card-content">
                        <!-- Operating Mode -->
                        <div>
                            <label for="em_operating_mode">${this._localize(hass, 'ui.em_operating_mode', 'Operating Mode')}:</label>
                            <select id="em_operating_mode">
                                <option value="1">${this._localize(hass, 'ui.manuell', 'Manuell')}</option>
                                <option value="2">${this._localize(hass, 'ui.optimization', 'Eigenverbrauchsoptimierung')}</option>
                                <option value="4">${this._localize(hass, 'ui.test_mode', 'Testbetrieb')}</option>
                                <option value="6">${this._localize(hass, 'ui.extension_mode', 'Erweiterungsmodus')}</option>
                                <option value="10">${this._localize(hass, 'ui.time_of_use', 'Time Of Use')}</option>
                                <option value="11">${this._localize(hass, 'ui.automatic_optimization', 'Automatik')}</option>
                            </select>
                            <button id="set_em_mode">${this._localize(hass, 'ui.apply', 'Setzen')}</button>
                        </div>

                        <!-- Leistung und Richtung -->
                        <div>
                            <label for="direction">${this._localize(hass, 'ui.direction', 'Richtung')}:</label>
                            <select id="direction">
                                <option value="charge">${this._localize(hass, 'ui.charge', 'Laden')}</option>
                                <option value="discharge">${this._localize(hass, 'ui.discharge', 'Entladen')}</option>
                            </select>
                        </div>
                        <div>
                            <label id="watts_label" for="watts">${this._localize(hass, 'ui.power', 'Leistung')}:</label>
                            <input type="number" id="watts" min="0" value="1000" />
                            <button id="set_power">${this._localize(hass, 'ui.apply', 'Setzen')}</button>
                        </div>
                    </div>
                </ha-card>
            `;
            this.content = this.querySelector('ha-card');

            const emSelect = this.querySelector('#em_operating_mode');
            const wattsInput = this.querySelector('#watts');
            const wattsLabel = this.querySelector('#watts_label');

            // Hole die maximale Leistung aus Home Assistant und aktualisiere das Label
            this._updateMaxPowerLabel(hass, wattsLabel);

            // Event-Handler für Operating Mode
            this.querySelector('#set_em_mode').addEventListener('click', () => {
                const emMode = parseInt(emSelect.value, 10);
                console.log('Setze Mode:', emMode);

                hass.callService('sonnenbatterie', 'set_em_operating_mode', {
                    mode: emMode,
                }).then(() => {
                    console.log(`EM_OperatingMode wurde auf ${emMode} gesetzt.`);
                    alert(this._localize(hass, 'ui.mode_set_success', 'Modus wurde erfolgreich gesetzt.'));
                }).catch((error) => {
                    console.error('Fehler beim Setzen des EM_OperatingMode:', error);
                    alert(this._localize(hass, 'ui.mode_set_error', 'Fehler beim Setzen des Modus.'));
                });
            });

            // Event-Handler für Richtung und Leistung
            this.querySelector('#set_power').addEventListener('click', () => {
                const direction = this.querySelector('#direction').value;
                const watts = parseInt(wattsInput.value, 10);
                const maxPower = parseInt(wattsLabel.dataset.maxPower, 10);

                console.log(`Leistung anwenden: Richtung=${direction}, Leistung=${watts}, MaxPower=${maxPower}`);

                // Eingabevalidierung
                if (isNaN(watts) || watts < 0) {
                    alert(this._localize(hass, 'ui.invalid_power', 'Ungültige Leistung. Bitte geben Sie einen gültigen Wert ein.'));
                    return;
                }

                if (watts > maxPower) {
                    alert(this._localize(hass, 'ui.power_exceeds_max', 'Die Leistung überschreitet die maximale Grenze von {max} W.').replace('{max}', maxPower));
                    return;
                }

                hass.callService('sonnenbatterie', 'set_battery_power', {
                    direction: direction,
                    watts: watts,
                }).then(() => {
                    console.log(`Batterie wird ${direction} mit ${watts} W gesteuert.`);
                    alert(this._localize(hass, 'ui.power_set_success', 'Leistung wurde erfolgreich gesetzt.'));
                }).catch((error) => {
                    console.error('Fehler beim Setzen der Batterie-Leistung:', error);
                    alert(this._localize(hass, 'ui.power_set_error', 'Fehler beim Setzen der Leistung.'));
                });
            });
        }
    }

    async _updateMaxPowerLabel(hass, wattsLabel) {
        try {
            // Hole die maximale Leistung aus einem Sensor in Home Assistant
            const maxPowerEntity = 'sensor.sonnen_max_inverter_power';
            const state = hass.states[maxPowerEntity];

            if (state) {
                const maxPower = state.state;
                wattsLabel.innerHTML = `${this._localize(hass, 'ui.power', 'Leistung')} Max ${maxPower} W:`;
                wattsLabel.dataset.maxPower = maxPower; // Speichere Maximalwert für spätere Validierung
            } else {
                wattsLabel.innerHTML = `${this._localize(hass, 'ui.power', 'Leistung')} Max: ${this._localize(hass, 'ui.unknown', 'Unbekannt')}`;
                wattsLabel.dataset.maxPower = "0"; // Setze 0, falls der Maximalwert unbekannt ist
                console.warn('Maximale Leistung konnte nicht gefunden werden.');
            }
        } catch (error) {
            console.error('Fehler beim Abrufen der maximalen Leistung:', error);
            wattsLabel.innerHTML = `${this._localize(hass, 'ui.power', 'Leistung')} Max: ${this._localize(hass, 'ui.error', 'Fehler')}`;
            wattsLabel.dataset.maxPower = "0"; // Setze 0 als Fallback
        }
    }

    _localize(hass, key, fallback) {
        return hass.localize(`custom_component.sonnenbatterie.${key}`) || fallback;
    }

    getCardSize() {
        return 3;
    }
}

// Karte registrieren
customElements.define('sonnenbatterie-card', SonnenBatteryCard);