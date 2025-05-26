from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, CONF_NAME, CONF_DOMAINS, CONF_AREA, DEFAULT_DOMAINS
from homeassistant.helpers.area_registry import async_get as async_get_area_registry
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry

class EntityCounterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._name = None
        self._domains = None
        self._area = None

    async def async_step_user(self, user_input=None):
        errors = {}

        area_registry = await async_get_area_registry(self.hass)
        areas = sorted(area_registry.areas.values(), key=lambda x: x.name)

        entity_registry = await async_get_entity_registry(self.hass)
        all_domains = sorted({entity_id.split(".")[0] for entity_id in entity_registry.entities})

        if user_input is not None:
            self._name = user_input.get(CONF_NAME)
            self._domains = user_input.get(CONF_DOMAINS)
            self._area = user_input.get(CONF_AREA)
            return self.async_create_entry(
                title=self._name or "Entity Counter",
                data={
                    CONF_NAME: self._name,
                    CONF_DOMAINS: self._domains,
                    CONF_AREA: self._area,
                },
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default="Entity Counter"): str,
                vol.Required(CONF_DOMAINS, default=DEFAULT_DOMAINS[0]): vol.In(all_domains),
                vol.Optional(CONF_AREA, default=None): vol.In([area.name for area in areas]),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)