class SonnenBatteryCard extends HTMLElement {
    // Konfigurationsmethode
    setConfig(config) {
        console.log("Konfiguration empfangen:", config);
        this.config = config; // Speichere die Konfiguration
    }

    // Wird aufgerufen, wenn Home Assistant-Daten aktualisiert werden
    set hass(hass) {
        if (!this.content) {
            this.innerHTML = `
                <ha-card header="${hass.localize('ui.card_title')}">
                    <div class="card-content">
                        <!-- Operating Mode -->
                        <div>
                            <label for="em_operating_mode">${hass.localize('ui.em_operating_mode')}:</label>
                            <select id="em_operating_mode">
                                <option value="1">${hass.localize('ui.manuell')}</option>
                                <option value="2">${hass.localize('ui.optimization')}</option>
                                <option value="4">${hass.localize('ui.test_mode')}</option>
                                <option value="6">${hass.localize('ui.extension_mode')}</option>
                                <option value="10">${hass.localize('ui.time_of_use')}</option>
                            </select>
                            <button id="set_em_mode">${hass.localize('ui.apply')}</button>
                        </div>

                        <!-- Leistung und Richtung -->
                        <div>
                            <label for="direction">${hass.localize('ui.direction')}:</label>
                            <select id="direction">
                                <option value="charge">${hass.localize('ui.charge')}</option>
                                <option value="discharge">${hass.localize('ui.discharge')}</option>
                            </select>
                        </div>
                        <div>
                            <label for="watts">${hass.localize('ui.power')}:</label>
                            <input type="number" id="watts" min="0" value="1000" />
                            <button id="set_power">${hass.localize('ui.apply')}</button>
                        </div>
                    </div>
                </ha-card>
            `;
            this.content = this.querySelector('ha-card');

            const emSelect = this.querySelector('#em_operating_mode');

            // Event-Handler für Operating Mode
            this.querySelector('#set_em_mode').addEventListener('click', () => {
                const emMode = parseInt(emSelect.value, 10);
                console.log('Setze Mode:', emMode);

                // Service-Aufruf für den EM_OperatingMode
                hass.callService('sonnenbatterie', 'set_em_operating_mode', {
                    mode: emMode,
                }).then(() => {
                    console.log(`EM_OperatingMode wurde auf ${emMode} gesetzt.`);
                    alert(hass.localize('ui.mode_set_success'));
                }).catch((error) => {
                    console.error('Fehler beim Setzen des EM_OperatingMode:', error);
                    alert(hass.localize('ui.mode_set_error'));
                });
            });

            // Event-Handler für Richtung und Leistung
            this.querySelector('#set_power').addEventListener('click', () => {
                const direction = this.querySelector('#direction').value;
                const watts = parseInt(this.querySelector('#watts').value, 10);

                console.log(`Leistung anwenden: Richtung=${direction}, Leistung=${watts}`);

                // Eingabevalidierung
                if (isNaN(watts) || watts < 0) {
                    alert(hass.localize('ui.invalid_power'));
                    return;
                }

                // Service-Aufruf für Batterie-Leistung
                hass.callService('sonnenbatterie', 'set_battery_power', {
                    direction: direction,
                    watts: watts,
                }).then(() => {
                    console.log(`Batterie wird ${direction} mit ${watts} W gesteuert.`);
                    alert(hass.localize('ui.power_set_success'));
                }).catch((error) => {
                    console.error('Fehler beim Setzen der Batterie-Leistung:', error);
                    alert(hass.localize('ui.power_set_error'));
                });
            });
        }
    }

    getCardSize() {
        return 3; // Größe der Karte in Reihen
    }
}

// Karte registrieren - Der Name muss exakt mit dem YAML-Typ übereinstimmen
customElements.define('sonnenbatterie-card', SonnenBatteryCard);