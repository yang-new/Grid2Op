# Copyright (c) 2019-2020, RTE (https://www.rte-france.com)
# See AUTHORS.txt
# This Source Code Form is subject to the terms of the Mozilla Public License, version 2.0.
# If a copy of the Mozilla Public License, version 2.0 was not distributed with this file,
# you can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
# This file is part of Grid2Op, Grid2Op a testbed platform to model sequential decision making in power systems.

import numpy as np


class RandomObject(object):
    """
    Utility class to deal with randomness in some aspect of the game (chronics, action_space, observation_space for
    examples.

    Attributes
    ----------
    space_prng: ``numpy.random.RandomState``
        The random state of the observation (in case of non deterministic observations or BaseAction.
        This should not be used at the
        moment)

    seed_used: ``int``
        The seed used throughout the episode in case of non deterministic observations or action.

    Notes
    -----
        In order to be reproducible, and to make proper use of the
        :func:`BaseAgent.seed` capabilities, you must absolutely NOT use the `random` python module (which will not
        be seeded) nor the `np.random` module and avoid any other "sources" of pseudo random numbers.

        You can adapt your code the following way. Instead of using `np.random` use `self.space_prng`.

        For example, if you wanted to write
        `np.random.randint(1,5)` replace it by `self.space_prng.randint(1,5)`. It is the same for `np.random.normal()`
        that is
        replaced by `self.space_prng.normal()`.

        You have an example of such usage in :func:`RandomAgent.my_act`.

        If you really need other sources of randomness (for example if you use tensorflow or torch) we strongly
        recommend you to overload the :func:`BaseAgent.seed` accordingly. In that
    """
    def __init__(self):
        self.space_prng = np.random.RandomState()
        self.seed_used = None

    def seed(self, seed):
        """
        Set the seed of the source of pseudo random number used for this RandomObject.

        Parameters
        ----------
        seed: ``int``
            The seed to be set.

        Returns
        -------
        res: ``tuple``
            The associated tuple of seeds used. Tuples are returned because in some cases, multiple objects are seeded
            with the same call to :func:`RandomObject.seed`

        """
        self.seed_used = seed
        if self.seed_used is not None:
            # in this case i have specific seed set. So i force the seed to be deterministic.
            self.space_prng.seed(seed=self.seed_used)
        return self.seed_used,
