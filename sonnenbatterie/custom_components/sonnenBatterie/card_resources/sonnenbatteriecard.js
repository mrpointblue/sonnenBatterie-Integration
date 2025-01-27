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
                <ha-card header="Sonnen Battery Control">
                    <div class="card-content">
                        <!-- Operating Mode -->
                        <div>
                            <label for="em_operating_mode">OperatingMode:</label>
                            <select id="em_operating_mode">
                                <option value="1">Manuell</option>
                                <option value="2">Eigenverbrauchsoptimierung</option>
                                <option value="4">Testbetrieb</option>
                                <option value="6">Erweiterungsmodus</option>
                                <option value="10">Time Of Use</option>
                            </select>
                            <button id="set_em_mode">Modus Setzen</button>
                        </div>

                        <!-- Leistung und Richtung -->
                        <div>
                            <label for="direction">Richtung:</label>
                            <select id="direction">
                                <option value="charge">Laden</option>
                                <option value="discharge">Entladen</option>
                            </select>
                        </div>
                        <div>
                            <label for="watts">Leistung (W):</label>
                            <input type="number" id="watts" min="0" value="1000" />
                            <button id="set_power">Leistung Setzen</button>
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
                    alert('EM_OperatingMode wurde gesetzt.');
                }).catch((error) => {
                    console.error('Fehler beim Setzen des EM_OperatingMode:', error);
                    alert('Fehler beim Setzen des EM_OperatingMode.');
                });
            });

            // Event-Handler für Richtung und Leistung
            this.querySelector('#set_power').addEventListener('click', () => {
                const direction = this.querySelector('#direction').value;
                const watts = parseInt(this.querySelector('#watts').value, 10);
                const emMode = parseInt(emSelect.value, 10);

                console.log(`Leistung anwenden: Mode=${emMode}, Richtung=${direction}, Leistung=${watts}`);

                // Eingabevalidierung
                if (isNaN(watts) || watts < 0) {
                    alert('Bitte gib eine gültige Leistung (W) ein.');
                    return;
                }

                // Service-Aufruf für Batterie-Leistung
                hass.callService('sonnenbatterie', 'set_battery_power', {
                    direction: direction,
                    watts: watts,
                    mode: emMode,
                }).then(() => {
                    console.log(`Batterie wird ${direction} mit ${watts} W im Modus ${emMode} gesteuert.`);
                    alert('Leistung und Richtung wurde gesetzt.');
                }).catch((error) => {
                    console.error('Fehler beim Setzen der Batterie-Leistung:', error);
                    alert('Fehler beim Setzen der Batterie-Leistung.');
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