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
from grid2op.Environment import MultiEnvironment
from grid2op.MakeEnv import make
from grid2op.Observation import CompleteObservation
import pdb


class TestLoadingMultiEnv(unittest.TestCase):
    def test_creation_multienv(self):
        nb_env = 2
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            with make("rte_case5_example", test=True) as env:
                multi_envs = MultiEnvironment(env=env, nb_env=nb_env)

        obss, rewards, dones, infos = multi_envs.step([env.action_space() for _ in range(nb_env)])
        for ob in obss:
            assert isinstance(ob, CompleteObservation)

        obss = multi_envs.reset()
        for ob in obss:
            assert isinstance(ob, CompleteObservation)

        # test some actions will not throw errors
        multi_envs.set_ff(7*288)
        multi_envs.set_chunk_size(128)
        obss = multi_envs.reset()
        seeds = multi_envs.get_seeds()
        multi_envs.close()

    def test_seeding(self):
        nb_env = 2
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            with make("rte_case5_example", test=True) as env:
                env.seed(2)
                multi_envs1 = MultiEnvironment(env=env, nb_env=nb_env)
                seeds_1 = multi_envs1.get_seeds()
                multi_envs1.close()
                multi_envs2 = MultiEnvironment(env=env, nb_env=nb_env)
                seeds_2 = multi_envs2.get_seeds()
                multi_envs2.close()
                env.seed(2)
                multi_envs3 = MultiEnvironment(env=env, nb_env=nb_env)
                seeds_3 = multi_envs3.get_seeds()
                multi_envs3.close()
                assert np.all(seeds_1 == seeds_3)
                assert np.any(seeds_1 != seeds_2)


if __name__ == "__main__":
    unittest.main()
