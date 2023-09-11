"""Bin packing with reinforcement learning."""

from environments.two_d import BinPackingEnv  # noqa: F401
from gymnasium.envs.registration import register

register(
    id="2DBinPackingEnv-v0",
    entry_point="environments.two_d:BinPackingEnv",
)
