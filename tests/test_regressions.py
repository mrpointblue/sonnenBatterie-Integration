"""Isolated regression tests with HA interfaces stubbed; no HA runtime required.

Run: python3 -B -m unittest discover -s tests -v
These exercise integration behavior, not Home Assistant framework compatibility.
"""
import asyncio
import importlib
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import AsyncMock, Mock, patch

ROOT = Path(__file__).resolve().parents[1]


def module(name, **attrs):
    value = types.ModuleType(name)
    value.__dict__.update(attrs)
    sys.modules[name] = value
    return value


class HAError(Exception):
    pass


class AuthFailed(HAError):
    pass


class UpdateFailed(HAError):
    pass


class Coordinator:
    def __init__(self, hass, logger, **kwargs):
        self.data = None
        self.last_update_success = True
        self.update_interval = kwargs['update_interval']


class CoordinatorEntity:
    def __init__(self, coordinator):
        self.coordinator = coordinator

    @property
    def available(self):
        return self.coordinator.last_update_success


class Flow:
    def __init_subclass__(cls, **kwargs):
        pass

    def async_create_entry(self, **kwargs):
        return kwargs

    def async_abort(self, **kwargs):
        return kwargs

    def async_show_form(self, **kwargs):
        return kwargs


class Response:
    def __init__(self, status=200, data=None):
        self.status = status
        self.data = {'USOC': 50} if data is None else data

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    def raise_for_status(self):
        if self.status >= 400:
            raise ClientError()

    async def json(self):
        return self.data


class ClientError(Exception):
    pass


class Regressions(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.modules_patch = patch.dict(sys.modules)
        cls.modules_patch.start()
        module('homeassistant')
        module('homeassistant.core', HomeAssistant=object, callback=lambda f: f)
        module('homeassistant.config_entries', ConfigEntry=object, ConfigFlow=Flow, OptionsFlow=Flow)
        module('homeassistant.exceptions', HomeAssistantError=HAError, ConfigEntryAuthFailed=AuthFailed)
        module('homeassistant.components')
        module('homeassistant.components.sensor', SensorEntity=type('SensorEntity', (), {}))
        module('homeassistant.helpers')
        module('homeassistant.helpers.config_validation', string=str, entity_ids=list,
               config_entry_only_config_schema=lambda domain: {})
        module('homeassistant.helpers.entity_registry', async_get=lambda hass: hass.registry)
        module('homeassistant.helpers.aiohttp_client', async_get_clientsession=lambda hass: hass.session)
        module('homeassistant.helpers.update_coordinator', DataUpdateCoordinator=Coordinator,
               CoordinatorEntity=CoordinatorEntity, UpdateFailed=UpdateFailed)
        module('homeassistant.util')
        from datetime import datetime
        module('homeassistant.util.dt', parse_datetime=lambda value: datetime.fromisoformat(value))
        module('aiohttp', ClientError=ClientError, ClientTimeout=lambda **kwargs: kwargs)
        module('voluptuous', Schema=lambda value: value, Required=lambda key, **kw: key,
               Optional=lambda key, **kw: key, All=lambda *args: args,
               Coerce=lambda value: value, Range=lambda **kw: kw, In=lambda value: value)
        package = module('custom_components')
        package.__path__ = [str(ROOT / 'custom_components')]
        cls.integration = importlib.import_module('custom_components.sonnenbatterie')
        cls.sensor = importlib.import_module('custom_components.sonnenbatterie.sensor')
        cls.service = importlib.import_module('custom_components.sonnenbatterie.service')
        cls.control = importlib.import_module('custom_components.sonnenbatterie.battery_control')
        cls.options = importlib.import_module('custom_components.sonnenbatterie.options_flow')
        cls.flow = importlib.import_module('custom_components.sonnenbatterie.config_flow')

    @classmethod
    def tearDownClass(cls):
        cls.modules_patch.stop()

    def entry(self, entry_id='a', **data):
        return types.SimpleNamespace(entry_id=entry_id, data={
            'ip_address': '192.0.2.1', 'token': 'test',
            'identity_ip': '192.0.2.1', 'identity_prefix': 'sonnen', **data,
        }, options={}, async_on_unload=Mock(), add_update_listener=Mock())

    def coordinator(self, response):
        self.hass = types.SimpleNamespace(session=Mock(get=Mock(side_effect=response)))
        entry = self.entry()
        return self.sensor.SonnenDataUpdateCoordinator(self.hass, entry, entry.data)

    async def test_total_failure_raises_for_setup_retry(self):
        coordinator = self.coordinator(lambda *a, **kw: Response(503))
        with self.assertRaises(UpdateFailed):
            await coordinator._async_update_data()

    async def test_timeout_is_failed_update(self):
        coordinator = self.coordinator(lambda *a, **kw: (_ for _ in ()).throw(asyncio.TimeoutError()))
        with self.assertRaises(UpdateFailed):
            await coordinator._async_update_data()

    async def test_denied_endpoints_retry_with_unchanged_token(self):
        for status in (401, 403):
            coordinator = self.coordinator(lambda *a, **kw: Response(status))
            for _ in range(2):
                with self.assertRaises(UpdateFailed):
                    await coordinator._async_update_data()
            self.assertEqual(coordinator.token, 'test')
            for call in self.hass.session.get.call_args_list:
                self.assertEqual(call.kwargs['headers']['Auth-Token'], 'test')
            self.hass.session.get.side_effect = lambda url, **kw: Response(
                200, [{'direction': 'production'}] if url.endswith('/powermeter') else {'USOC': 50})
            result = await coordinator._async_update_data()
            self.assertEqual(result['/api/v2/latestdata']['USOC'], 50)

    async def test_single_denied_endpoint_does_not_block_other_data(self):
        for status in (401, 403):
            coordinator = self.coordinator(lambda url, **kw:
                Response(status) if url.endswith('/configurations') else Response(
                    200, [{'direction': 'production'}] if url.endswith('/powermeter') else {'USOC': 50}))
            coordinator.data = await coordinator._async_update_data()
            self.assertIn('/api/v2/status', coordinator.data)
            self.assertNotIn('/api/v2/configurations', coordinator.data)
            self.assertEqual(coordinator.token, 'test')

    async def test_partial_failure_marks_only_affected_sensors_unavailable(self):
        coordinator = self.coordinator(lambda url, **kw:
            Response(200) if url.endswith('/latestdata') else Response(404))
        coordinator.data = await coordinator._async_update_data()
        latest = self.sensor.SonnenBatterieSensor(coordinator, self.sensor.SENSORS[3], 'sonnen')
        status = self.sensor.SonnenBatterieSensor(coordinator, self.sensor.SENSORS[5], 'sonnen')
        self.assertTrue(latest.available)
        self.assertEqual(latest.native_value, 50)
        self.assertFalse(status.available)
        coordinator.last_update_success = False
        self.assertFalse(latest.available)

    async def test_identity_survives_address_and_prefix_change(self):
        coordinator = self.coordinator(lambda *a, **kw: Response())
        before = self.sensor.SonnenBatterieSensor(coordinator, self.sensor.SENSORS[0], 'sonnen')
        coordinator.ip = '192.0.2.99'
        after = self.sensor.SonnenBatterieSensor(coordinator, self.sensor.SENSORS[0], 'new')
        self.assertEqual(before._attr_unique_id, 'sonnen_House Consumption_192.0.2.1-Consumption_W')
        self.assertEqual(before._attr_unique_id, after._attr_unique_id)
        self.assertEqual(before._attr_device_info['identifiers'], after._attr_device_info['identifiers'])

    async def test_endpoint_and_direction_are_explicit(self):
        coordinator = self.coordinator(lambda *a, **kw: Response())
        coordinator.data = {'/api/v2/latestdata': {'Consumption_W': 120},
                            '/api/v2/status': {'Consumption_W': 999},
                            '/api/v2/powermeter': [{'direction': 'production', 'w_l1': 100},
                                                  {'direction': 'consumption', 'w_l1': 200}]}
        entity = self.sensor.SonnenBatterieSensor(coordinator, self.sensor.SENSORS[0], 'sonnen')
        self.assertEqual(entity.native_value, 120)
        definition = next(s for s in self.sensor.SENSORS if s['name'] == 'Consumption Power L1')
        entity = self.sensor.SonnenBatterieSensor(coordinator, definition, 'sonnen')
        self.assertEqual(entity.native_value, 200)

    async def test_targets_are_resolved_without_last_battery_fallback(self):
        a, b = self.entry('a'), self.entry('b')
        hass = types.SimpleNamespace(data={'sonnenbatterie': {'a': a, 'b': b}}, registry=Mock())
        with self.assertRaises(HAError):
            self.service.resolve_entry(hass, None)
        hass.registry.async_get.return_value = types.SimpleNamespace(platform='sonnenbatterie', config_entry_id='a')
        self.assertIs(self.service.resolve_entry(hass, ['sensor.renamed']), a)
        hass.registry.async_get.return_value = None
        with self.assertRaises(HAError):
            self.service.resolve_entry(hass, ['sensor.missing'])
        hass.data['sonnenbatterie'].pop('b')
        self.assertIs(self.service.resolve_entry(hass, None), a)

    async def test_zero_watts_and_failure_reporting(self):
        session = Mock(request=Mock(return_value=Response(204)))
        await self.control.set_battery_power(session, '192.0.2.1', 'test', 'charge', 0)
        self.assertEqual(session.request.call_args.args[:2], ('POST', 'http://192.0.2.1/api/v2/setpoint/charge/0'))
        session.request.return_value = Response(500)
        with self.assertRaises(HAError):
            await self.control.set_battery_power(session, '192.0.2.1', 'test', 'charge', 1)
        with self.assertRaises(HAError):
            await self.control.set_em_operating_mode(session, '192.0.2.1', 'test', 11)

    async def test_options_saved_without_overwriting_identity(self):
        flow = self.options.SonnenOptionsFlow()
        flow.config_entry = self.entry()
        result = await flow.async_step_init({'ip_address': '192.0.2.2', 'token': 'new', 'scan_interval': 10})
        self.assertEqual(result['data']['ip_address'], '192.0.2.2')
        self.assertEqual(flow.config_entry.data['identity_ip'], '192.0.2.1')

    async def test_setup_reload_and_unload_lifecycle(self):
        entry = self.entry()
        hass = types.SimpleNamespace(data={}, config_entries=types.SimpleNamespace(
            async_forward_entry_setups=AsyncMock(), async_reload=AsyncMock(),
            async_unload_platforms=AsyncMock(return_value=True)))
        with patch.object(self.integration, 'async_register_services', AsyncMock()), \
             patch.object(self.integration, 'copy_card_to_www', AsyncMock()), \
             patch.object(self.integration, 'async_remove_services') as remove:
            self.assertTrue(await self.integration.async_setup_entry(hass, entry))
            entry.add_update_listener.assert_called_once_with(self.integration.async_update_entry)
            await self.integration.async_update_entry(hass, entry)
            hass.config_entries.async_reload.assert_awaited_once_with('a')
            hass.config_entries.async_unload_platforms.return_value = False
            self.assertFalse(await self.integration.async_unload_entry(hass, entry))
            self.assertIn('a', hass.data['sonnenbatterie'])
            remove.assert_not_called()
            hass.config_entries.async_unload_platforms.return_value = True
            self.assertTrue(await self.integration.async_unload_entry(hass, entry))
            remove.assert_called_once_with(hass)


    async def test_services_use_selected_battery_current_options(self):
        entry = self.entry('a')
        entry.options = {'ip_address': '192.0.2.44', 'token': 'updated'}
        handlers = {}
        services = Mock()
        services.has_service.return_value = False
        services.async_register.side_effect = lambda domain, name, handler, **kw: handlers.update({name: handler})
        hass = types.SimpleNamespace(data={'sonnenbatterie': {'a': entry}},
                                     services=services, session=object())
        await self.service.async_register_services(hass)
        with patch.object(self.service, 'set_battery_power', AsyncMock()) as command:
            await handlers['set_battery_power'](types.SimpleNamespace(
                service='set_battery_power', data={'direction': 'charge', 'watts': 0}))
            command.assert_awaited_once_with(hass.session, '192.0.2.44', 'updated', 'charge', 0)
            command.side_effect = HAError('rejected')
            with self.assertRaises(HAError):
                await handlers['set_battery_power'](types.SimpleNamespace(
                    service='set_battery_power', data={'direction': 'charge', 'watts': 0}))

    async def test_timestamps_need_timezone_and_energy_is_not_rounded(self):
        coordinator = self.coordinator(lambda *a, **kw: Response())
        definition = next(s for s in self.sensor.SENSORS if s['key'] == 'Timestamp')
        entity = self.sensor.SonnenBatterieSensor(coordinator, definition, 'sonnen')
        for value in ('invalid', '2026-09-20T12:00:00'):
            coordinator.data = {'/api/v2/status': {'Timestamp': value}}
            self.assertIsNone(entity.native_value)
        coordinator.data = {'/api/v2/status': {'Timestamp': '2026-09-20T12:00:00+02:00'}}
        self.assertIsNotNone(entity.native_value.tzinfo)
        definition = next(s for s in self.sensor.SENSORS if s['key'] == 'kwh_imported')
        coordinator.data = {'/api/v2/powermeter': [{'direction': 'production', 'kwh_imported': 1.23456}]}
        entity = self.sensor.SonnenBatterieSensor(coordinator, definition, 'sonnen')
        self.assertEqual(entity.native_value, 1.23456)

    async def test_first_setup_freezes_identity_before_registering_listener(self):
        entry = self.entry()
        entry.data.pop('identity_ip')
        entry.data.pop('identity_prefix')
        hass = types.SimpleNamespace(data={}, config_entries=types.SimpleNamespace(
            async_forward_entry_setups=AsyncMock(), async_update_entry=Mock()))
        def update(target, data):
            target.add_update_listener.assert_not_called()
            target.data = data
        hass.config_entries.async_update_entry.side_effect = update
        with patch.object(self.integration, 'async_register_services', AsyncMock()), \
             patch.object(self.integration, 'copy_card_to_www', AsyncMock()):
            await self.integration.async_setup_entry(hass, entry)
        self.assertEqual(entry.data['identity_ip'], '192.0.2.1')
        self.assertEqual(entry.data['identity_prefix'], 'sonnen')


if __name__ == '__main__':
    unittest.main()
