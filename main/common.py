from django.conf import settings


def get_ip_address(request_meta):
    return '127.0.0.1' if settings.DEBUG or settings.TEST_IN_PROGRESS else request_meta.get('HTTP_X_FORWARDED_FOR')
