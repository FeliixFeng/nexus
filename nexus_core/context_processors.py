from nexus_core.pin_utils import is_pin_verified


def pin_context(request):
    return {'is_editor': is_pin_verified(request)}
