"""
OS functions

Copyright 2017 Pavel Folov
"""

import shutil
import logging

logger = logging.getLogger(__name__)

class filebackup:
    """Backups a file while needs to rewrite the file.

    Returns file back if something wrong happened.
    Backup file will be replaced if exists.

    >>> with filebackup('1.txt') as sb:
    >>>     print(sb.filepath, sb.bak_filepath)
    >>>     # write new file
    """
    # todo: integrate backup scheme
    def __init__(self, filepath, ext='.bak'):
        self.filepath = filepath
        self.bak_ext = ext
        self.bak_filepath = None

    def __enter__(self):
        self.bak_filepath = self.filepath + self.bak_ext
        shutil.move(self.filepath, self.bak_filepath)
        logger.info('created backup from: %s, to: %s', self.filepath, self.bak_filepath)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is None:
            logger.info('successful done')
            return
        logger.exception(exc_val)
        # todo: os.remove(self.filepath)
        shutil.move(self.bak_filepath, self.filepath)
