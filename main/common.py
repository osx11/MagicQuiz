from django.conf import settings

from datetime import datetime


def get_ip_address(request_meta):
    return '127.0.0.1' if settings.DEBUG or settings.TEST_IN_PROGRESS else request_meta.get('HTTP_X_FORWARDED_FOR')


def strptime(time):
    return datetime.strptime(time, '%Y-%d-%m %H:%M:%S')
