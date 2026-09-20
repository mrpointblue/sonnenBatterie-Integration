// Run from repository root with JavaScriptCore jsc or node.
if (typeof load === 'undefined') {
    globalThis.load = path => require('node:vm').runInThisContext(require('node:fs').readFileSync(path, 'utf8'));
    globalThis.print = console.log;
    globalThis.quit = code => process.exit(code);
}
globalThis.HTMLElement = class {};
globalThis.Option = class { constructor(text, value) { this.text = text; this.value = value; } };
let Card;
globalThis.customElements = {define: (_, value) => { Card = value; }};
globalThis.alert = () => {};
load('custom_components/sonnenbatterie/card_resources/sonnenbatteriecard.js');
function assert(value, message) { if (!value) throw new Error(message); }
const entity = (id, battery, device = battery) => ({entity_id: id, config_entry_id: battery, device_id: device, platform: 'sonnenbatterie'});
const devices = ['a', 'b'].map(id => ({id, name_by_user: `Batterie ${id}`, identifiers: [['sonnenbatterie', id]]}));
function card(entities, states, config = {}) {
    const c = new Card();
    c.setConfig(config);
    c.content = {};
    const nodes = new Map();
    c.querySelector = selector => {
        if (!nodes.has(selector)) nodes.set(selector, {replaceChildren(...items) { this.items = items; }, append(item) { this.items.push(item); }});
        return nodes.get(selector);
    };
    c._registryEntities = entities;
    c._registryDevices = new Map(devices.map(d => [d.id, d]));
    c._hass = {states: Object.fromEntries(Object.entries(states).map(([id, state]) => [id, {state, attributes: {}}])),
        callService: async (...args) => { c.sent = args; }};
    c._renderBatteries();
    return c;
}
(async () => {
    const a = entity('sensor.renamed_a', 'a'), b = entity('sensor.renamed_b', 'b');
    let c = card([a], {[a.entity_id]: '50'});
    assert(c.querySelector('#battery_row').hidden, 'Single battery: selector hidden');
    assert(!c.querySelector('#set_power').disabled, 'Single battery: automatic selection');
    await c._sendCommand('set_battery_power', {direction: 'charge', watts: 1000});
    assert(c.sent[2].entity_id === a.entity_id, 'Single battery command has explicit target');

    c = card([a, entity('sensor.second_a', 'a'), b], {[a.entity_id]: '50', 'sensor.second_a': '200', [b.entity_id]: '60'});
    assert(c._batteries().length === 2, 'Group by battery, not number of sensors');
    assert(!c.querySelector('#battery_row').hidden, 'Multiple batteries: selector shown');
    assert(c.querySelector('#set_power').disabled, 'No arbitrary default with multiple batteries');
    await c._sendCommand('set_battery_power', {watts: 1});
    assert(!c.sent, 'Unselected target cannot send');
    c._selectedBattery = 'b'; c._renderBatteries();
    await c._sendCommand('set_battery_power', {direction: 'charge', watts: 0});
    assert(c.sent[2].entity_id === b.entity_id && c.sent[2].watts === 0, 'Selected second battery receives zero setpoint');
    await c._sendCommand('set_em_operating_mode', {mode: 2});
    assert(c.sent[1] === 'set_em_operating_mode' && c.sent[2].entity_id === b.entity_id, 'Mode uses same selection');
    delete c._hass.states[b.entity_id]; c._renderBatteries();
    assert(c.querySelector('#set_power').disabled && c._selectedBattery === 'b', 'Removed battery must not redirect commands');
    c._hass.states[b.entity_id] = {state: '60', attributes: {}}; c._renderBatteries();
    assert(!c.querySelector('#set_power').disabled, 'Selection survives reconnect');
    c._hass.states[b.entity_id].state = 'unavailable'; c._renderBatteries();
    assert(c.querySelector('#set_power').disabled, 'Unavailable selection cannot send');

    c = card([a, b], {[a.entity_id]: '50', [b.entity_id]: '60'}, {entity: b.entity_id});
    assert(c._selectedBattery === 'b', 'Existing entity configuration preselects battery');
    c._hass.states[a.entity_id].attributes.restored = true;
    assert(c._batteries().length === 1, 'Ignore orphaned restored entities');
    c._registryError = true; c._renderBatteries();
    assert(c.querySelector('#set_power').disabled, 'Discovery failure blocks commands');

    c = card([], {});
    assert(c.querySelector('#set_power').disabled, 'No batteries: commands disabled');
    c._hass.callWS = async ({type}) => type.includes('entity_registry') ? [a, b] : devices;
    c._hass.states = {[a.entity_id]: {state: '50'}, [b.entity_id]: {state: '60'}};
    await c._loadBatteries();
    assert(c._batteries().length === 2, 'WebSocket discovery populates batteries');
    c._hass.callWS = async () => { throw new Error('offline'); };
    await c._loadBatteries();
    assert(c._registryError, 'WebSocket failure is visible');
    print('Card regression checks passed');
})().catch(error => { print(error.stack); quit(1); });
