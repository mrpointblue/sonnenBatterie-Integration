class SonnenBatteryCard extends HTMLElement {
    setConfig(config) {
        if (config.entity && typeof config.entity !== 'string') {
            throw new Error('entity muss eine Entitäts-ID der Batterie sein.');
        }
        this.config = config;
        this._selectedBattery = null;
        this._selectionInitialized = false;
    }

    set hass(hass) {
        this._hass = hass;
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

                    [hidden] { display: none !important; }
                    button:disabled { opacity: 0.5; cursor: default; }

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

                    <div id="battery_row" class="row" hidden>
                        <label for="battery">Batterie:</label>
                        <select id="battery" aria-label="Batterie auswählen"></select>
                    </div>
                    <p id="battery_status" role="status" aria-live="polite"></p>

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

            this.querySelector('#battery').addEventListener('change', (event) => {
                this._selectedBattery = event.target.value || null;
                this._selectionInitialized = true;
                this._renderBatteries();
            });

            // Event-Handler für Betriebsmodus
            this.querySelector('#set_em_mode').addEventListener('click', () => {
                const emMode = parseInt(this.querySelector('#em_operating_mode').value, 10);
                this._sendCommand('set_em_operating_mode', {mode: emMode});
            });

            // Event-Handler für Leistung und Richtung
            this.querySelector('#set_power').addEventListener('click', () => {
                const direction = this.querySelector('#direction').value;
                const watts = Number(this.querySelector('#watts').value);
                if (!Number.isInteger(watts) || watts < 0) {
                    alert('Bitte eine ganze, nicht negative Wattzahl eingeben.');
                    return;
                }
                this._sendCommand('set_battery_power', {direction, watts});
            });
        }
        this._renderBatteries();
        // Registry data changes less often than sensor states. Recheck on
        // reconnect and periodically, without querying on every state update.
        if (this._connection !== hass.connection || !this._lastRegistryFetch ||
            Date.now() - this._lastRegistryFetch > 30000) {
            this._loadBatteries();
        }
    }

    async _loadBatteries() {
        if (this._loadingBatteries) return;
        this._loadingBatteries = true;
        const hass = this._hass;
        this._lastRegistryFetch = Date.now();
        this._connection = hass.connection;
        try {
            const [entities, devices] = await Promise.all([
                hass.callWS({type: 'config/entity_registry/list'}),
                hass.callWS({type: 'config/device_registry/list'}),
            ]);
            if (this._hass.connection !== hass.connection) {
                this._lastRegistryFetch = 0;
                return;
            }
            this._registryEntities = entities;
            this._registryDevices = new Map(devices.map(device => [device.id, device]));
            this._registryError = false;
        } catch (error) {
            this._registryError = true;
        } finally {
            this._loadingBatteries = false;
            this._renderBatteries();
        }
    }

    _batteries() {
        const groups = new Map();
        for (const entity of this._registryEntities || []) {
            if (entity.platform !== 'sonnenbatterie' || entity.disabled_by ||
                !entity.config_entry_id) continue;
            const state = this._hass.states[entity.entity_id];
            // Restored states belong to entities no longer supplied by HA.
            if (!state || state.attributes?.restored) continue;
            const device = this._registryDevices.get(entity.device_id);
            if (device?.disabled_by) continue;
            let battery = groups.get(entity.config_entry_id);
            if (!battery) {
                const address = device?.identifiers?.find(([domain]) => domain === 'sonnenbatterie')?.[1];
                const name = device?.name_by_user || device?.name || 'sonnenBatterie';
                battery = {id: entity.config_entry_id, name: address && !name.includes(address)
                    ? `${name} (${address})` : name, entities: [], available: false};
                groups.set(battery.id, battery);
            }
            battery.entities.push(entity);
            battery.available ||= state.state !== 'unavailable';
        }
        return [...groups.values()].sort((a, b) => a.name.localeCompare(b.name) || a.id.localeCompare(b.id));
    }

    _renderBatteries() {
        if (!this.content) return;
        const batteries = this._batteries();
        if (!this._selectionInitialized && batteries.length) {
            const configured = batteries.find(b => b.entities.some(e => e.entity_id === this.config.entity));
            this._selectedBattery = configured?.id || (!this.config.entity && batteries.length === 1
                ? batteries[0].id : null);
            this._selectionInitialized = true;
        }
        const selected = batteries.find(b => b.id === this._selectedBattery);
        const select = this.querySelector('#battery');
        const signature = JSON.stringify(batteries.map(b => [b.id, b.name, b.available]));
        if (signature !== this._batteryOptions) {
            this._batteryOptions = signature;
            select.replaceChildren(new Option('Bitte Batterie auswählen', ''));
            for (const battery of batteries) {
                const option = new Option(battery.name + (battery.available ? '' : ' – nicht verfügbar'), battery.id);
                option.disabled = !battery.available;
                select.append(option);
            }
        }
        select.value = selected?.id || '';
        this.querySelector('#battery_row').hidden = batteries.length <= 1;
        // Never silently redirect a previously selected target to another battery.
        const ready = Boolean(selected?.available && !this._registryError && !this._sending);
        this.querySelector('#set_em_mode').disabled = !ready;
        this.querySelector('#set_power').disabled = !ready;
        select.disabled = Boolean(this._sending);
        let message = '';
        if (this._registryError) message = 'Batterien konnten nicht geladen werden. Bitte die Karte neu laden.';
        else if (!this._registryEntities) message = 'Batterien werden geladen …';
        else if (!batteries.length) message = 'Keine aktive sonnenBatterie gefunden. Bitte die Integration prüfen.';
        else if (!selected && batteries.length > 1) message = 'Bitte die Batterie auswählen, die gesteuert werden soll.';
        else if (!selected) message = 'Die gewählte Batterie ist nicht mehr vorhanden. Bitte die Karte neu laden.';
        else if (!selected.available) message = 'Die gewählte Batterie ist nicht verfügbar.';
        else if (this._sending) message = `Befehl an ${selected.name} wird gesendet …`;
        this.querySelector('#battery_status').textContent = message;
        const maxEntity = selected?.entities.find(e => e.entity_id === this.config.max_power_entity) ||
            selected?.entities.find(e => e.original_name?.endsWith('_Max Inverter Power'));
        const power = this._hass.states[maxEntity?.entity_id]?.state;
        this.querySelector('#max_power_label').textContent = power && Number.isFinite(Number(power))
            ? `Maximale Leistung: ${power} W` : 'Maximale Leistung: Nicht verfügbar';
    }

    async _sendCommand(service, data) {
        const battery = this._batteries().find(b => b.id === this._selectedBattery);
        if (this._sending || this._registryError || !battery?.available) {
            this._renderBatteries();
            return;
        }
        const entity = battery.entities.find(e => this._hass.states[e.entity_id]?.state !== 'unavailable');
        this._sending = true;
        this._renderBatteries();
        try {
            await this._hass.callService('sonnenbatterie', service, {...data, entity_id: entity.entity_id});
            alert(`Befehl an ${battery.name} erfolgreich ausgeführt.`);
        } catch (error) {
            alert(`Befehl an ${battery.name} fehlgeschlagen: ${error.message || 'Bitte Verbindung und API-Berechtigungen prüfen.'}`);
        } finally {
            this._sending = false;
            this._renderBatteries();
        }
    }

    getCardSize() {
        return 3;
    }
}

customElements.define('sonnenbatterie-card', SonnenBatteryCard);