from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import (
    DEVICE_CLASS_GAS,
    VOLUME_CUBIC_METERS,
    ELECTRIC_POTENTIAL_VOLT,
    STATE_UNKNOWN
)
from .const import DOMAIN

GAS_SENSORS = {
    "balance": {
        "name": "燃气费余额",
        "icon": "hass:cash-100",
        "unit_of_measurement": "元",
        "attributes": ["last_update"]
    },
    "current_level": {
        "name": "当前燃气阶梯",
        "icon": "hass:stairs"
    },
    "current_price": {
        "name": "当前气价",
        "icon": "hass:cash-100",
        "unit_of_measurement": "元/m³"
    },
    "current_level_remain": {
        "name": "当前阶梯剩余额度",
        "device_class": DEVICE_CLASS_GAS,
        "unit_of_measurement": VOLUME_CUBIC_METERS
    },
    "year_consume": {
        "name": "本年度用气量",
        "device_class": DEVICE_CLASS_GAS,
        "unit_of_measurement": VOLUME_CUBIC_METERS
    },
    "month_reg_qty": {
        "name": "当月用气量",
        "device_class": DEVICE_CLASS_GAS,
        "unit_of_measurement": VOLUME_CUBIC_METERS
    },
    "battery_voltage": {
        "name": "气表电量",
        "device_class": DEVICE_CLASS_GAS,
        "unit_of_measurement": ELECTRIC_POTENTIAL_VOLT
    },
    "mtr_status": {
        "name": "阀门状态",
        "device_class": DEVICE_CLASS_GAS,
        "unit_of_measurement": ""
    }
}


async def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    sensors = []
    coordinator = hass.data[DOMAIN]
    for user_code, data in coordinator.data.items():
        for key in GAS_SENSORS.keys():
            if key in data.keys():
                sensors.append(GASSensor(coordinator, user_code, key))
        for month in range(len(data["monthly_bills"])):
            sensors.append(GASHistorySensor(coordinator, user_code, month))
        for day in range(len(data["daily_bills"])):
            sensors.append(GASDailyBillSensor(coordinator, user_code, day))
    async_add_devices(sensors, True)


class GASBaseSensor(CoordinatorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._unique_id = None

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def should_poll(self):
        return False


class GASSensor(GASBaseSensor):
    def __init__(self, coordinator, user_code, sensor_key):
        super().__init__(coordinator)
        self._user_code = user_code
        self._sensor_key = sensor_key
        self._config = GAS_SENSORS[self._sensor_key]
        self._attributes = self._config.get("attributes")
        self._coordinator = coordinator
        self._unique_id = f"{DOMAIN}.{user_code}_{sensor_key}"
        self.entity_id = self._unique_id

    def get_value(self, attribute=None):
        try:
            if attribute is None:
                return self._coordinator.data.get(self._user_code).get(self._sensor_key)
            return self._coordinator.data.get(self._user_code).get(attribute)
        except KeyError:
            return STATE_UNKNOWN

    @property
    def name(self):
        return self._config.get("name")

    @property
    def state(self):
        return self.get_value()

    @property
    def icon(self):
        return self._config.get("icon")

    @property
    def device_class(self):
        return self._config.get("device_class")

    @property
    def unit_of_measurement(self):
        return self._config.get("unit_of_measurement")

    @property
    def extra_state_attributes(self):
        attributes = {}
        if self._attributes is not None:
            try:
                for attribute in self._attributes:
                    attributes[attribute] = self.get_value(attribute)
            except KeyError:
                pass
        return attributes


class GASHistorySensor(GASBaseSensor):
    def __init__(self, coordinator, user_code, index):
        super().__init__(coordinator)
        self._user_code = user_code
        self._coordinator = coordinator
        self._index = index
        self._unique_id = f"{DOMAIN}.{user_code}_monthly_{index + 1}"
        self.entity_id = self._unique_id

    @property
    def name(self):
        try:
            return self._coordinator.data.get(self._user_code).get("monthly_bills")[self._index].get("mon")
        except KeyError:
            return STATE_UNKNOWN

    @property
    def state(self):
        try:
            return self._coordinator.data.get(self._user_code).get("monthly_bills")[self._index].get("regQty")
        except KeyError:
            return STATE_UNKNOWN

    @property
    def extra_state_attributes(self):
        try:
            return {
                "consume_bill": self._coordinator.data.get(self._user_code).get("monthly_bills")[self._index].get(
                    "amt")
            }
        except KeyError:
            return {"consume_bill": 0.0}

    @property
    def device_class(self):
        return DEVICE_CLASS_GAS

    @property
    def unit_of_measurement(self):
        return VOLUME_CUBIC_METERS


class GASDailyBillSensor(GASBaseSensor):
    def __init__(self, coordinator, user_code, index):
        super().__init__(coordinator)
        self._user_code = user_code
        self._coordinator = coordinator
        self._index = index
        self._unique_id = f"{DOMAIN}.{user_code}_daily_{index + 1}"
        self.entity_id = self._unique_id

    @property
    def name(self):
        try:
            return self._coordinator.data.get(self._user_code).get("daily_bills")[self._index].get("day")[:10]
        except KeyError:
            return STATE_UNKNOWN

    @property
    def state(self):
        try:
            return self._coordinator.data.get(self._user_code).get("daily_bills")[self._index].get("regQty")
        except KeyError:
            return STATE_UNKNOWN

    @property
    def device_class(self):
        return DEVICE_CLASS_GAS

    @property
    def unit_of_measurement(self):
        return VOLUME_CUBIC_METERS
