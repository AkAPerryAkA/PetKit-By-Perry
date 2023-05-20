class ConfigFlow(config_entries.ConfigFlow, domain = DOMAIN):
    async def async_step_user(self, info):
        if info is not None:
            pass  # TODO: process info
        return self.async_show_form(step_id = "sync_user", data_schema = vol.Schema({vol.Required("E-Mail Address"): str, vol.Required("Password"): str}))