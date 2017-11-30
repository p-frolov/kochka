import coloredlogs


def _logger_settings(level):
    return {'handlers': ['console', 'file', 'errors'], 'level': level, 'propagate': False}


_date_format = '%Y-%m-%d %H:%M:%S'
_default_format = '%(asctime)s %(name)-15s - %(levelname)-10s - %(message)s'

config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'class': 'logging.Formatter',
            'datefmt': _date_format,
            'format': _default_format,
        },
        'colored': {
            '()': coloredlogs.ColoredFormatter,
            'datefmt': _date_format,
            'format': _default_format,
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'colored',
        },
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'encoding': 'utf-8',
            'level': 'DEBUG',
            'filename': 'logs/kochka.log',
            'when': 'D',
            'backupCount': 7,
            'utc': True,
            'formatter': 'default',
        },
        'audit': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'encoding': 'utf-8',
            'level': 'INFO',
            'filename': 'logs/audit.log',
            'when': 'D',
            'backupCount': 365,
            'utc': True,
            'formatter': 'default',
        },
        'errors': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'encoding': 'utf-8',
            'level': 'ERROR',
            'filename': 'logs/kochka-errors.log',
            'when': 'D',
            'backupCount': 7,
            'utc': True,
            'formatter': 'default',
        },
    },
    # particular modules
    'loggers': {
        # decrease log level to avoid a noise
        # 'engineio': _logger_settings('WARNING'),
        'oslib': _logger_settings('INFO'),
        'kochka.audit': {'handlers': ['audit'], 'level': 'INFO', 'propagate': False},
    },
    # root and other modules
    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'file', 'errors'],
    },
}
