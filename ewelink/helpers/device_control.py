STATE_ON = "on"
STATE_OFF = "off"
STATE_TOGGLE = "toggle"

VALID_POWER_STATES = [STATE_ON, STATE_OFF, STATE_TOGGLE]


def get_new_power_state(current_state, new_state):
    if new_state != STATE_TOGGLE:
        return new_state
    return STATE_OFF if current_state == STATE_ON else STATE_ON


def get_power_state_params(params, new_state, channel):
    if params.get("switches"):
        switches = [dict(item) for item in params["switches"]]
        switches[channel - 1]["switch"] = new_state
        return {"switches": switches}

    return {"switch": new_state}


def get_all_channels_state(params):
    return [
        {
            "channel": ch["outlet"] + 1,
            "state": ch["switch"],
        }
        for ch in params["switches"]
    ]


def get_specific_channel_state(params, channel):
    return params["switches"][channel - 1]["switch"]
