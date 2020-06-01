# Copyright (c) 2019-2020, RTE (https://www.rte-france.com)
# See AUTHORS.txt
# This Source Code Form is subject to the terms of the Mozilla Public License, version 2.0.
# If a copy of the Mozilla Public License, version 2.0 was not distributed with this file,
# you can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
# This file is part of Grid2Op, Grid2Op a testbed platform to model sequential decision making in power systems.

import numpy as np

from grid2op.Exceptions import Grid2OpException
from grid2op.Reward.BaseReward import BaseReward
from grid2op.dtypes import dt_float

class EconomicReward(BaseReward):
    """
    This reward computes the marginal cost of the powergrid. As RL is about maximising a reward, while we want to
    minimize the cost, this class also ensures that:

    - the reward is positive if there is no game over, no error etc.
    - the reward is inversely proportional to the cost of the grid (the higher the reward, the lower the economic cost).

    """
    def __init__(self):
        BaseReward.__init__(self)
        self.reward_min = dt_float(0.0)
        self.reward_max = dt_float(1.0)
        self.worst_cost = None

    def initialize(self, env):
        if not env.redispatching_unit_commitment_availble:
            raise Grid2OpException("Impossible to use the EconomicReward reward with an environment without generators"
                                   "cost. Please make sure env.redispatching_unit_commitment_availble is available.")
        self.worst_cost = dt_float(np.sum(env.gen_cost_per_MW *env.gen_pmax))

    def __call__(self, action, env, has_error, is_done, is_illegal, is_ambiguous):
        if has_error or is_illegal or is_ambiguous:
            res = self.reward_min
        else:
            # compute the cost of the grid
            res = dt_float(np.sum(env.current_obs.prod_p * env.gen_cost_per_MW))
            # we want to minimize the cost by maximizing the reward so let's take the opposite
            res *= dt_float(-1.0)
            # to be sure it's positive, add the highest possible cost
            res += self.worst_cost

        res = np.interp(res, [dt_float(0.0), self.worst_cost], [self.reward_min, self.reward_max])
        return dt_float(res)
