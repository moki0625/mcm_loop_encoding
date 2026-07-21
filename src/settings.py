"""
This file
"""

import logging
import os
import random
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import tensorflow as tf
import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

@dataclass
class DataFolderSetting:
    """
    setting.data_folder
    """
    cycle_date_folder: Path = "D:\\SynologyDrive\\Data\MCM_Loop\\cycle_summary.csv"
    output_folder: Path = "D:\\SynologyDrive\\Data\\MCM_Loop\\Processed_data\\"

@dataclass
class EncodingSetting:
    """
    setting.encoding
    """
    step_minutes: int = 5 # unit: minute
    save_to_single_file: bool = True


@dataclass
class Settings:
    """
    Main setting
    """
    data_folder: DataFolderSetting = field(default_factory=DataFolderSetting)
    encoding: EncodingSetting = field(default_factory=EncodingSetting)