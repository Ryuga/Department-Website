from django_hosts import patterns, host

host_patterns = patterns(
    '',
    host(r'www', 'core.apps.web.urls', name='www'),
    host(r'zephyrus', 'core.apps.dashboard.urls', name='zephyrus'),
    host(r'dashboard', 'core.apps.dashboard.urls', name='dashboard'),
    host(r'admin', 'core.urls', name='admin'),
    host(r'', 'core.apps.web.urls', name='default'),
)
