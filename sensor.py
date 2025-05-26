from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.helpers.area_registry import async_get as async_get_area_registry
from homeassistant.const import STATE_ON
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.core import callback
from .const import DOMAIN, CONF_NAME, CONF_DOMAINS, CONF_AREA

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([EntityCounterSensor(hass, entry)], True)

class EntityCounterSensor(SensorEntity):
    def __init__(self, hass, config_entry):
        self.hass = hass
        self.config_entry = config_entry
        self._name = config_entry.data.get(CONF_NAME)
        self._domains = config_entry.data.get(CONF_DOMAINS, [])
        self._area_name = config_entry.data.get(CONF_AREA)
        self._state = None
        self._attr_extra_state_attributes = {}
        self._attr_unique_id = f"{DOMAIN}_{self._name.replace(' ', '_').lower()}"
        self._attr_name = self._name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attr_extra_state_attributes

    async def async_added_to_hass(self):
        self._unsub = async_track_state_change_event(
            self.hass, self._get_monitored_entities(), self._state_changed
        )
        await self._async_update_state()

    async def async_will_remove_from_hass(self):
        self._unsub()

    def _get_monitored_entities(self):
        entity_registry = self.hass.helpers.entity_registry.async_get()
        area_registry = self.hass.helpers.area_registry.async_get()
        entities = []
        for entity_id, entity_entry in entity_registry.entities.items():
            domain = entity_id.split(".")[0]
            if domain not in self._domains:
                continue
            if self._area_name:
                if entity_entry.area_id is None:
                    continue
                area = area_registry.areas.get(entity_entry.area_id)
                if not area or area.name != self._area_name:
                    continue
            entities.append(entity_id)
        return entities

    @callback
    async def _state_changed(self, event):
        await self._async_update_state()

    async def _async_update_state(self):
        entities = self._get_monitored_entities()
        on_entities = []

        for entity_id in entities:
            state = self.hass.states.get(entity_id)
            if not state or state.state != STATE_ON:
                continue
            on_entities.append(entity_id)

        self._state = len(on_entities)

        # Attributi aggiuntivi
        attr = {}
        names = []
        for entity_id in on_entities:
            state = self.hass.states.get(entity_id)
            friendly_name = state.attributes.get("friendly_name") if state else None
            names.append(friendly_name or entity_id)
        attr["entities_on"] = ", ".join(names)
        self._attr_extra_state_attributes = attr

        self.async_write_ha_state()
