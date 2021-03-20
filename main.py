import signal
from configparser import ConfigParser
from gpiozero import Button, MCP3208, LED


class Scaled:
    def __init__(self, channel, label, unit, min_value, max_value, min_threshold, max_threshold):
        self.adc = MCP3208(channel)
        self.channel = channel
        self.min_value = min_value
        self.max_value = max_value
        self.label = label
        self.unit = unit
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold

    @property
    def value(self):
        diff = self.max_value - self.min_value
        # print(self.min_value)
        value = self.adc.value * diff + min_value
        if self.min_threshold <= value <= self.max_threshold:
            value = 0.0
        return value, self.adc.value * 3.3

    @property
    def text(self):
        return f"{self.value} {self.unit}"

    def __repr__(self):
        return f"AE{self.adc.channel}: {self.label}"


class MyButton(Button):
    def __init__(self, pin, label, pull_up, *args, **kwargs):
        super().__init__(pin, pull_up=pull_up, *args, **kwargs)
        self.label = label
    def __repr__(self):
        return f"DE [{self.pin}] {self.label}"


class MyLED(LED):
    def __init__(self, pin, label, active_high, initial_value, *args, **kwargs):
        super().__init__(pin, active_high=active_high, initial_value=initial_value, *args, **kwargs)
        self.label = label
    def __repr__(self):
        return f"DA [{self.pin}] {self.label}"


AE = []
DE = []
DA = []

cfg = ConfigParser()
cfg.read("configuration.ini")
for section_name, section in cfg.items():
    if section_name == "DEFAULT":
        continue
    label = section.get("label")
    channel = section.getint("channel")
    pull_up = section.getboolean("pull_up", None)

    active_high = section.getboolean("active_high", None)
    initial_value = section.getboolean("initial_value", None)

    if section_name.startswith("AE"):
        min_value = section.getfloat("min")
        max_value = section.getfloat("max")
        unit = section.get("unit")
        min_threshold = section.getfloat("min_threshold", fallback=0.0)
        max_threshold = section.getfloat("max_threshold", fallback=0.0)
        AE.append(Scaled(channel, label, unit, min_value, max_value, min_threshold, max_threshold))
    elif section_name.startswith("DE"):
        DE.append(MyButton(channel, label, pull_up))
    elif section_name.startswith("DA"):
        DA.append(MyLED(channel, label, active_high=active_high, initial_value=initial_value))


AE.sort(key=lambda x: x.channel, reverse=True)

for adc in AE:
    print(adc, adc.value)


signal.pause()
#AE.clear()
#DE.clear()
#DA.clear()

