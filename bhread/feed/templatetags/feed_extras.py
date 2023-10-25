from urllib.parse import urlparse

from django import template

register = template.Library()


def url_domain(value):
    """Format a url to only show domain name"""
    return str(urlparse(value).netloc)


register.filter("url_domain", url_domain)
