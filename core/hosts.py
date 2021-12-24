from django_hosts import patterns, host

host_patterns = patterns(
    '',
    host(r'www', 'web.urls', name='www'),
    host(r'dashboard', 'dashboard.urls', name='dashboard'),
    # host(r'admin', 'web.redirection_urls', name='admin'),
)
