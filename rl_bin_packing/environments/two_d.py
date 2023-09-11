from typing import Any, Self, Tuple

import gymnasium as gym
import numpy as np
import plotly.graph_objects as go
from gymnasium import spaces

from rl_bin_packing.container.two_d import Container, Shipment


class BinPackingEnv(gym.Env):
    def __init__(self: Self, container: Container, shipments: list[Shipment]) -> None:
        self.shipments = shipments
        self.container = Container(container.length, container.height)

        num_shipments = len(shipments)

        self.reset()

        # Define action spaces
        self.action_space = spaces.MultiDiscrete(
            [
                num_shipments,  # Select shipment (index)
                container.length,  # X-coordinate
                container.height,  # Y-coordinate
            ]
        )

        # Define observation space
        self.observation_space = spaces.Dict(
            {
                "container_state": spaces.Box(
                    low=0,
                    high=1,
                    shape=(container.length, container.height),
                    dtype=np.int8,
                ),
                "shipment_info": spaces.Box(
                    low=np.zeros((num_shipments, 3), dtype=np.int32),
                    high=np.ones((num_shipments, 3), dtype=np.int32)
                    * np.iinfo(np.int32).max,
                    dtype=np.int32,
                ),
            },
        )

    def reset(self: Self, seed=None, options=None):
        super().reset(seed=seed)
        self.container = Container(self.container.length, self.container.height)

        num_shipments = len(self.shipments)
        self.available_shipments = np.ones(num_shipments, dtype=np.int8)
        self.shipment_sizes = np.zeros(shape=[num_shipments, 2], dtype=np.int32)
        self.shipment_weights = np.zeros(shape=num_shipments, dtype=np.int32)

        for i, shipment in enumerate(self.shipments):
            self.shipment_sizes[i] = shipment.length, shipment.height
            self.shipment_weights[i] = shipment.weight
        return self._get_observation(), {}

    def step(self: Self, action: tuple[int, int, int]):
        # Parse the action
        shipment_idx, x, y = action

        # Get the selected shipment
        shipment = self.shipments[shipment_idx]

        # Place the shipment in the container
        self.container.pack(shipment, x, y)

        # Remove the shipment from available shipments
        self.available_shipments[shipment_idx] = 0

        # Calculate reward
        reward = self._calculate_reward()

        # Check if the episode is done
        terminated = self._is_done()

        # Return the next observation, reward, done flag, and additional info
        return self._get_observation(), reward, terminated, False, {}

    def render(self: Self) -> go.Figure:
        # Render the current state of the environment
        return self.container.plot()

    def _get_observation(self: Self) -> dict:
        shipment_info = []

        for i, shipment in enumerate(self.shipments):
            if self.available_shipments[i]:
                # Include information for available shipments
                shipment_info.append(
                    [
                        shipment.length,
                        shipment.height,
                        shipment.weight,
                    ],
                )
            else:
                # For unavailable shipments, use zeros
                shipment_info.append([0, 0, 0])

        return {
            "container_state": self.container.map,
            "shipment_info": np.array(shipment_info, dtype=np.int32),
        }

    def _calculate_reward(self: Self) -> float | int:
        if not self.container.valid:
            return -1

        # Reward for degree of filling (higher is better)
        degree_of_filling_reward = self.container.degree_of_filling

        # Reward for smaller distance to the optimal center of gravity
        distance_to_optimal_cog_reward = 1.0 / (
            1.0 + self.container.distance_optimal_cog
        )

        # Combine the rewards with weights to balance them
        return 0.5 * degree_of_filling_reward + 0.5 * distance_to_optimal_cog_reward

    def _is_done(self: Self) -> bool:
        # Define your termination conditions
        if len(self.available_shipments) == 0 or not self.container.valid:
            return True
        return False
