from typing import Callable, Dict


AwsHandler = Callable[[Dict, Dict], Dict]
