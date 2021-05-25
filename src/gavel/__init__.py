__version__ = "0.0.0"

import gavel.plugins
from multiprocessing import set_start_method, get_start_method
if get_start_method(allow_none=True) is None:
    set_start_method("spawn")
