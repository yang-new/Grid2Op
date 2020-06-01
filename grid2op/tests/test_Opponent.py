# Copyright (c) 2019-2020, RTE (https://www.rte-france.com)
# See AUTHORS.txt
# This Source Code Form is subject to the terms of the Mozilla Public License, version 2.0.
# If a copy of the Mozilla Public License, version 2.0 was not distributed with this file,
# you can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
# This file is part of Grid2Op, Grid2Op a testbed platform to model sequential decision making in power systems.

import pdb
import warnings
from grid2op.tests.helper_path_test import *
from grid2op.Opponent import BaseOpponent
from grid2op.MakeEnv import make


class TestLoadingOpp(unittest.TestCase):
    def test_creation_BaseOpponent(self):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            with make("rte_case5_example", test=True) as env:
                my_opp = BaseOpponent(action_space=env.action_space)


if __name__ == "__main__":
    unittest.main()
