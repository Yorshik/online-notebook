def format_settings_string(settings_dct: dict) -> str:
    string = ''
    for key, value in settings_dct.items():
        string += f'{key}: {value};'
    return string
