"""
This file contains the settings (path to the case file, chronics converter etc.) that allows to make a simple
environment with a powergrid of only 5 buses, 3 laods, 2 generators and 8 powerlines.
"""
import os
import pkg_resources
import numpy as np
from pathlib import Path

file_dir = Path(__file__).parent.absolute()
grid2op_root = file_dir.parent.absolute()
dat_dir = os.path.abspath(os.path.join(grid2op_root, "data"))
case_dir = "case14_test"
grid_file = "case14_test.json"

case14_test_CASEFILE = os.path.join(dat_dir, case_dir, grid_file)
case14_test_CHRONICSPATH = os.path.join(dat_dir, case_dir, "chronics")

case14_test_TH_LIM = np.array([   352.8251645 ,    352.8251645 , 183197.68156979, 183197.68156979,
                                   183197.68156979,  12213.17877132, 183197.68156979,    352.8251645,
                                      352.8251645 ,    352.8251645 ,    352.8251645 ,    352.8251645,
                                   183197.68156979, 183197.68156979, 183197.68156979,    352.8251645,
                                      352.8251645 ,    352.8251645 ,   2721.79412618,   2721.79412618])
