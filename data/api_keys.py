from flask import abort


def get_api_key(access_level):
    if access_level == 'free':
        return '1219711-0100101-1203211-1110108'
    elif access_level == 'pro':
        return '1051101-0132110-1111161-0198111'
    elif access_level == 'admin':
        return '1111073-2112114-1111061-0199116'
    else:
        raise abort(403)
