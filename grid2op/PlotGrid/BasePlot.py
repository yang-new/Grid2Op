# Copyright (c) 2019-2020, RTE (https://www.rte-france.com)
# See AUTHORS.txt
# This Source Code Form is subject to the terms of the Mozilla Public License, version 2.0.
# If a copy of the Mozilla Public License, version 2.0 was not distributed with this file,
# you can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
# This file is part of Grid2Op, Grid2Op a testbed platform to model sequential decision making in power systems.

import numpy as np
import copy
from abc import ABC, abstractmethod

from grid2op.Observation import BaseObservation
from grid2op.Exceptions import PlotError
from grid2op.PlotGrid.LayoutUtil import layout_obs_sub_load_and_gen
from grid2op.PlotGrid.PlotUtil import PlotUtil as pltu
from grid2op.dtypes import dt_float, dt_int

class BasePlot(ABC):
    """
    Abstract interface to plot the state of the powergrid

    Implement the interface with a plotting library to generate drawings 

    Attributes
    -----------

    observation_space: ``grid2op.Observation.ObservationSpace``
        The observation space used.

    width: ``int`` Width of the drawing

    height: ``int`` Height of the drawing

    grid_layout: ``dict`` A grid layout dict to use

    """
    def __init__(self,
                 observation_space,
                 width=800,
                 height=600,
                 scale=2000.0,
                 grid_layout=None,
                 parallel_spacing=3.0):

        self.observation_space = observation_space
        self.width = width
        self.height = height
        self.scale = scale
        self._parallel_spacing = parallel_spacing

        self._info_to_units = {
            "rho": "%",
            "a": "A",
            "p": "MW",
            "v":"kV"
        }
        self._lines_info = ["rho", "a", "p", "v", None]
        self._loads_info = ["p", "v", None]
        self._gens_info = ["p", "v", None]

        self._grid_layout = self.compute_grid_layout(observation_space, grid_layout)

        # Augment observation_space with dummy observation data
        # so we can use it as an observation for plotting just the layout or custom infos
        self.observation_space.topo_vect = np.ones(self.observation_space.dim_topo, dtype=np.int)
        self.observation_space.line_status = np.full(self.observation_space.n_line, True)
        self.observation_space.rho = np.full(self.observation_space.n_line, 0.0)
        self.observation_space.p_or = np.ones(self.observation_space.n_line)

    @abstractmethod
    def create_figure(self):
        """
        Creates a new figure to draw into.
        Depending on the library can also be called Plot, canvas, screen .. 
        """
        pass

    @abstractmethod
    def clear_figure(self, figure):
        """
        Clears a figure
        Depending on the library can also be called Plot, canvas, screen .. 
        """
        pass

    @abstractmethod
    def convert_figure_to_numpy_HWC(self, figure):
        """
        Given a figure as returned by `BasePlot.create_figure`
        Convert it to a numpy array of dtype uint8 
        and data layed out in the HWC format
        """
        pass

    def compute_grid_layout(self, observation_space, grid_layout = None):
        """
        Compute the grid layout from the observation space

        This should return a native python ``dict`` 
        in the same format as observation_space.grid_layout :

        .. code-block:: python

            {
              "substation1_name": [x_coord, y_coord],
              "substation2_name": [x_coord, y_coord],
              [...],
              "load1_name": [x_coord, y_coord],
              [...], 
              "gen1_name": [x_coord, y_coord],
              [...]
            }
        
        Note that is must contain at least the positions for the substations.
        The loads and generators will be skipped if missing. 

        By default, if `grid_layout` is provided this is returned, 
        otherwise returns observation_space.grid_layout

        Parameters
        ----------

        observation_space: ``grid2op.Observation.ObservationSpace``
             The observation space of the environment

        grid_layout: ``dict`` or ``None``
             A dictionary containing the coordinates for each substation.
        """
        # We need an intial layout to work with
        use_grid_layout = None
        if grid_layout != None:
            use_grid_layout = grid_layout
        elif observation_space.grid_layout is not None:
            use_grid_layout = observation_space.grid_layout
        else:
            raise PlotError("No grid layout provided for plotting")

        # Compute loads and gens positions using a default implementation
        observation_space.grid_layout = use_grid_layout
        return layout_obs_sub_load_and_gen(observation_space, scale=self.scale, use_initial=True)

    @abstractmethod
    def draw_substation(self, figure, observation,
                        sub_id, sub_name,
                        pos_x, pos_y):
        """
        Draws a substation into the figure

        Parameters
        ----------

        figure: :object: Figure to draw to. 
        This is the object returned by create_figure

        observation: :grid2op.Observation.BaseObservation: 
        Current state of the grid being drawn

        sub_id: :int: Id of the substation, Index in the observation

        sub_name: :str: Name of the substation

        pos_x: :int: x position from the layout

        pos_y: :int: y position from the layout
        """
        pass

    def update_substation(self, figure, observation,
                        sub_id, sub_name,
                        pos_x, pos_y):
        """
        Update a substation into the figure
        """
        pass

    @abstractmethod
    def draw_load(self, figure, observation,
                  load_name, load_id, load_bus,
                  load_value, load_unit,
                  pos_x, pos_y,
                  sub_x, sub_y):
        """
        Draws a load into the figure

        Parameters
        ----------

        figure: :object: Figure to draw to. 
        This is the object returned by create_figure

        observation: :grid2op.Observation.BaseObservation:
        Current state of the grid being drawn

        load_name: ``str`` Name of the load

        load_id: ``int`` Id of the load, Index in the observation

        load_bus: ``int`` Id of bus the load is connected to.

        load_value: ``float`` An informative value of the load current state

        load_unit: ``str`` The unit of the `load_value` argument as a string

        pos_x: ``int`` x position from the layout

        pos_y: ``int`` y position from the layout

        sub_x: ``int`` x position of the connected substation from the layout

        sub_y: ``int`` y position of the connected substation from the layout
        """
        pass

    def update_load(self, figure, observation,
                    load_name, load_id, load_bus,
                    load_value, load_unit,
                    pos_x, pos_y,
                    sub_x, sub_y):
        """
        Update a load into the figure
        """
        pass

    @abstractmethod
    def draw_gen(self, figure, observation,
                 gen_name, gen_id, gen_bus,
                 gen_value, gen_unit,
                 pos_x, pos_y,
                 sub_x, sub_y):
        """
        Draws a generator into the figure

        Parameters
        ----------

        figure: :object: Figure to draw to.
        This is the object returned by create_figure

        observation: `grid2op.Observation.BaseObservation` 
        Current state of the grid being drawn

        gen_name: ``str`` Name of the load

        gen_id: ``int`` Id of the generator, Index in the observation

        gen_bus: ``int`` Bus id the generator is connected to

        gen_value: ``float``
        An informative value of the generator current state

        gen_unit: ``str`` The unit of the `gen_value` argument as a string

        pos_x: ``int`` x position from the layout

        pos_y: ``int`` y position from the layout

        sub_x: ``int`` x position of the connected substation from the layout

        sub_y: ``int`` y position of the connected substation from the layout
        """
        pass

    def update_gen(self, figure, observation,
                   gen_name, gen_id, gen_bus,
                   gen_value, gen_unit,
                   pos_x, pos_y,
                   sub_x, sub_y):
        """
        Updates a generator into the figure
        """
        pass

    @abstractmethod
    def draw_powerline(self, figure, observation,
                       line_id, line_name, connected,
                       line_value, line_unit,
                       or_bus, pos_or_x, pos_or_y,
                       ex_bus, pos_ex_x, pos_ex_y):
        """
        Draws a powerline into the figure

        Parameters
        ----------

        figure: ``object`` Figure to draw to. 
        This is the object returned by `create_figure`

        observation: ``grid2op.Observation.BaseObservation``
        Current state of the grid being drawn

        line_id: ``int`` Id of the powerline, index in the observation

        line_name: ``str`` Name of the powerline

        connected: ``bool`` Is the line connected ?

        line_value: ``float`` An informative value of the line current state

        line_unit: ``str`` The unit of the `line_value` argument as a string

        or_bus: ``int`` Bus the powerline origin is connected to

        pos_or_x: ``int`` Powerline origin x position from the layout

        pos_or_y: ``int`` Powerline origin y position from the layout

        ex_bus: ``int`` Bus the powerline extremity is connected to

        pos_ex_x: ``int`` Powerline extremity x position from the layout

        pos_ex_y: ``int`` Powerline extremity y position from the layout
        """
        pass

    def update_powerline(self, figure, observation,
                         line_id, line_name, connected,
                         line_value, line_unit,
                         or_bus, pos_or_x, pos_or_y,
                         ex_bus, pos_ex_x, pos_ex_y):
        """
        Draws a powerline into the figure
        """
        pass

    @abstractmethod
    def draw_legend(self, figure, observation):
        """
        Setup the legend for the given figure.

        Parameters
        ----------
        figure: ``object`` Figure to draw to. 
        This is the object returned by `create_figure`

        observation: ``grid2op.Observation.BaseObservation``
        Current state of the grid being drawn
        """
        pass
    
    def update_legend(self, figure, observation):
        """
        Updates the legend for the given figure.
        """
        pass

    def plot_postprocess(self, figure, observation, is_update):
        """
        Some implementations may need post-processing.
        This is called at the end of plot.
        """
        pass

    def _plot_subs(self, figure, observation, redraw):
        draw_fn = self.draw_substation
        if not redraw:
            draw_fn = self.update_substation

        for sub_idx in range(observation.n_sub):
            sub_name = observation.name_sub[sub_idx]
            sub_x = self._grid_layout[sub_name][0]
            sub_y = self._grid_layout[sub_name][1]
            draw_fn(figure, observation,
                    sub_idx, sub_name,
                    sub_x, sub_y)

    def _plot_loads(self, figure, observation, load_values, load_unit, redraw):
        draw_fn = self.draw_load
        if not redraw:
            draw_fn = self.update_load

        topo = observation.topo_vect
        topo_pos = observation.load_pos_topo_vect
        for load_idx, load_name in enumerate(observation.name_load):
            if load_name not in self._grid_layout:
                continue
            load_value = None
            if load_values is not None:
                load_value = np.round(float(load_values[load_idx]), 2)
            load_x = self._grid_layout[load_name][0]
            load_y = self._grid_layout[load_name][1]
            load_subid = observation.load_to_subid[load_idx]
            load_subname = observation.name_sub[load_subid]
            load_bus = topo[topo_pos[load_idx]]
            load_bus = load_bus if load_bus > 0 else 0
            sub_x = self._grid_layout[load_subname][0]
            sub_y = self._grid_layout[load_subname][1]
            draw_fn(figure, observation,
                    load_idx, load_name, load_bus,
                    load_value, load_unit,
                    load_x, load_y, sub_x, sub_y)

    def _plot_gens(self, figure, observation, gen_values, gen_unit, redraw):
        draw_fn = self.draw_gen
        if not redraw:
            draw_fn = self.update_gen

        topo = observation.topo_vect
        topo_pos = observation.gen_pos_topo_vect
        for gen_idx, gen_name in enumerate(observation.name_gen):
            if gen_name not in self._grid_layout:
                continue
            gen_value = None
            if gen_values is not None:
                gen_value = np.round(float(gen_values[gen_idx]), 2)
            gen_x = self._grid_layout[gen_name][0]
            gen_y = self._grid_layout[gen_name][1]
            gen_subid = observation.gen_to_subid[gen_idx]
            gen_subname = observation.name_sub[gen_subid]
            gen_bus = topo[topo_pos[gen_idx]]
            gen_bus = gen_bus if gen_bus > 0 else 0
            sub_x = self._grid_layout[gen_subname][0]
            sub_y = self._grid_layout[gen_subname][1]
            draw_fn(figure, observation,
                    gen_idx, gen_name, gen_bus,
                    gen_value, gen_unit,
                    gen_x, gen_y, sub_x, sub_y)

    def _plot_lines(self, figure, observation, line_values, line_unit, redraw):
        draw_fn = self.draw_powerline
        if not redraw:
            draw_fn = self.update_powerline
            
        topo = observation.topo_vect
        line_or_pos = observation.line_or_pos_topo_vect
        line_ex_pos = observation.line_ex_pos_topo_vect

        for line_idx in range(observation.n_line):
            line_or_sub = observation.line_or_to_subid[line_idx]
            line_or_sub_name = observation.name_sub[line_or_sub]
            line_ex_sub = observation.line_ex_to_subid[line_idx]
            line_ex_sub_name = observation.name_sub[line_ex_sub]
            line_name = observation.name_line[line_idx]
            line_status = True
            line_status = observation.line_status[line_idx]
            line_value = None
            if line_values is not None:
                lv = line_values[line_idx]
                if isinstance(lv, (float, dt_float)):
                    line_value = np.round(float(lv), 2)
                elif isinstance(lv, (int, dt_int)):
                    line_value = int(lv)
                else:
                    line_value = lv

            line_or_bus = topo[line_or_pos[line_idx]]
            line_or_bus = line_or_bus if line_or_bus > 0 else 0
            line_or_x = self._grid_layout[line_or_sub_name][0]
            line_or_y = self._grid_layout[line_or_sub_name][1]
            line_ex_bus = topo[line_ex_pos[line_idx]]
            line_ex_bus = line_ex_bus if line_ex_bus > 0 else 0
            line_ex_x = self._grid_layout[line_ex_sub_name][0]
            line_ex_y = self._grid_layout[line_ex_sub_name][1]

            # Special case for parralel lines
            tmp = self.observation_space.get_lines_id(from_=line_or_sub,
                                                      to_=line_ex_sub)
            if len(tmp) > 1:
                ox, oy = pltu.orth_norm_from_points(line_or_x, line_or_y,
                                                    line_ex_x, line_ex_y)
                if line_idx == tmp[0]:
                    line_or_x += ox * self._parallel_spacing
                    line_or_y += oy * self._parallel_spacing
                    line_ex_x += ox * self._parallel_spacing
                    line_ex_y += oy * self._parallel_spacing
                else:
                    line_or_x -= ox * self._parallel_spacing
                    line_or_y -= oy * self._parallel_spacing
                    line_ex_x -= ox * self._parallel_spacing
                    line_ex_y -= oy * self._parallel_spacing

            draw_fn(figure, observation,
                    line_idx, line_name, line_status,
                    line_value, line_unit,
                    line_or_bus, line_or_x, line_or_y,
                    line_ex_bus, line_ex_x, line_ex_y)

    def _plot_legend(self, fig, observation, redraw):
        draw_fn = self.draw_legend
        if not redraw:
            draw_fn = self.update_legend

        draw_fn(fig, observation)

    def plot_layout(self):
        """
        This function plot the layout of the grid, as well as the object. You will see the name of each elements and
        their id.
        """
        return self.plot_info(observation=self.observation_space,
                              figure=None, redraw=True)
        
    def plot_obs(self, observation,
                 figure=None,
                 redraw=True,
                 line_info="rho",
                 load_info="p",
                 gen_info="p"):
        """
        Plot an observation.
        
        Parameters
        ----------
        observation: :class:`grid2op.Observation.BaseObservation`
            The observation to plot

        figure: ``object``
            The figure on which to plot the observation. 
            If figure is ``None``, a new figure is created.

        line_info: ``str``
            One of "rho", "a", or "p" or "v" 
            The information that will be plotted on the powerline.
            By default "rho".
            All flow are taken "origin" side.

        load_info: ``str``
            One of "p" or "v" the information displayed on the load.
            (default to "p").

        gen_info: ``str``
            One of "p" or "v" the information displayed on the generators
            (default to "p").

        Returns
        -------
        res: ``object``
            The figure updated with the data from the new observation.
        """

        # Start by checking arguments are valid
        if not isinstance(observation, BaseObservation):            
            err_msg = "Observation is not a derived type of " \
                      "grid2op.Observation.BaseObservation"
            raise PlotError(err_msg)
        if line_info not in self._lines_info:
            err_msg = "Impossible to plot line info \"{}\" for line." \
                      " Possible values are {}"
            raise PlotError(err_msg.format(line_info, str(self._lines_info)))
        if load_info not in self._loads_info:
            err_msg = "Impossible to plot load info \"{}\" for line." \
                      " Possible values are {}"
            raise PlotError(err_msg.format(load_info, str(self._loads_info)))
        if gen_info not in self._gens_info:
            err_msg = "Impossible to plot gen info \"{}\" for line." \
                      " Possible values are {}"
            raise PlotError(err_msg.format(gen_info, str(self._gens_info)))

        line_values = None
        line_unit = ""
        if line_info is not None:
            line_unit = self._info_to_units[line_info]
        if line_info == "rho":
            line_values = observation.rho * 100.0
        if line_info == "p":
            line_values = observation.p_or
        if line_info == "a":
            line_values = observation.a_or
        if line_info == "v":
            line_values = observation.v_or

        load_values = None
        load_unit = ""
        if load_info is not None:
            load_unit = self._info_to_units[load_info]
        if load_info == "p":
            load_values = copy.copy(observation.load_p) * -1.0
        if load_info == "v":
            load_values = observation.load_v

        gen_values = None
        gen_unit = ""
        if gen_info is not None:
            gen_unit = self._info_to_units[gen_info]
        if gen_info == "p":
            gen_values = observation.prod_p
        if gen_info == "v":
            gen_values = observation.prod_v

        return self.plot_info(observation=observation, figure=figure, redraw=redraw,
                              line_values=line_values, line_unit=line_unit,
                              load_values=load_values, load_unit=load_unit,
                              gen_values=gen_values, gen_unit=gen_unit)

    def plot_info(self,
                  figure=None,
                  redraw=True,
                  line_values=None,
                  line_unit="",
                  load_values=None,
                  load_unit="",
                  gen_values=None,
                  gen_unit="",
                  observation=None):
        """
        Plot an observation with custom values
        
        Parameters
        ----------
        figure: ``object``
            The figure on which to plot the observation. 
            If figure is ``None`` a new figure is created.

        line_values: ``list``
            information to be displayed for the powerlines
            [must have the same size as observation.n_line  and convertible to float]

        line_unit: ``str``
            Unit string for the :line_values: argument, displayed after the line value

        load_info: ``list``
            information to display for the loads
            [must have the same size as observation.n_load and convertible to float]

        load_unit: ``str``
            Unit string for the :load_values: argument, displayed after the load value

        gen_info: ``list``
            information to display in the generators
            [must have the same size as observation.n_gen and convertible to float]

        gen_unit: ``str``
            Unit string for the :gen_values: argument, displayed after the generator value

        observation: :class:`grid2op.Observation.BaseObservation`
            An observation to plot, can be None if no values are drawn from the observation

        Returns
        -------
        res: ``object``
            The figure updated with the data from the new observation.
        """
        # Check values are in the correct format
        if line_values is not None and len(line_values) != self.observation_space.n_line:
            raise PlotError("Impossible to display these values on the powerlines: there are {} values"
                            "provided for {} powerlines in the grid".format(len(line_values), self.observation_space.n_line))
        if load_values is not None and len(load_values) != self.observation_space.n_load:
            raise PlotError("Impossible to display these values on the loads: there are {} values"
                            "provided for {} loads in the grid".format(len(load_values), self.observation_space.n_load))
        if gen_values is not None and len(gen_values) != self.observation_space.n_gen:
            raise PlotError("Impossible to display these values on the generators: there are {} values"
                            "provided for {} generators in the grid".format(len(gen_info), self.observation_space.n_gen))

        # Get a valid figure to draw into
        if figure is None:
            fig = self.create_figure()
            redraw = True
        elif redraw:
            self.clear_figure(figure)
            fig = figure
        else:
            fig = figure

        # Get a valid Observation
        if observation is None:
            # See dummy data added in the constructor
            observation = self.observation_space
            
        # Trigger draw calls
        self._plot_lines(fig, observation, line_values, line_unit, redraw)
        self._plot_loads(fig, observation, load_values, load_unit, redraw)
        self._plot_gens(fig, observation, gen_values, gen_unit, redraw)
        self._plot_subs(fig, observation, redraw)
        self._plot_legend(fig, observation, redraw)

        # Some implementations may need postprocessing
        self.plot_postprocess(fig, observation, not redraw)
        
        # Return updated figure
        return fig
