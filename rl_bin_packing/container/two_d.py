"""Contains 2D containers."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Any, Self

import numpy as np
import plotly.graph_objects as go


@dataclass(frozen=True)
class Shipment:
    """Represents a shipment with dimensions and properties."""

    length: int
    height: int
    weight: int
    stackable: bool = True
    rotatable: bool = False
    identifier: str | None = None

    @property
    def volume(self: Self) -> int:
        """Calculate the volume of the shipment."""
        return self.length * self.height


@dataclass
class Position:
    """Represents a 2D position with x and y coordinates."""

    x: int | float
    y: int | float

    def __add__(self: Position, other: Position) -> Position:
        """Add two Position objects together."""
        return Position(self.x + other.x, self.y + other.y)

    def __mul__(self: Self, i: int) -> Position:
        """Multiply the Position by a scalar."""
        return Position(self.x * i, self.y * i)

    def __truediv__(self: Self, i: int) -> Position:
        """Divide the Position by a scalar."""
        return Position(self.x / i, self.y / i)


@dataclass
class PackedShipment:
    """Represents a shipment that has been packed into a container."""

    shipment: Shipment
    position: Position

    @property
    def center_of_gravity(self: Self) -> Position:
        """Calculate the center of gravity of the packed shipment."""
        x = (self.position.x * 2 + self.shipment.length) / 2
        y = (self.position.y * 2 + self.shipment.height) / 2
        return Position(x, y)

    def plot_center_of_gravity(self: Self, fig: go.Figure) -> go.Figure:
        """Plot the center of gravity on a Plotly figure.

        Args:
            fig (go.Figure): The Plotly figure to add the center of gravity marker to.

        Returns:
            go.Figure: The updated Plotly figure.
        """
        return fig.add_trace(
            go.Scatter(
                x=[self.center_of_gravity.x],
                y=[self.center_of_gravity.y],
                mode="markers",
                marker={"color": "grey"},
                name=f"G {self.shipment.identifier or ''}",
            ),
        )

    def plot(self: Self, fig: go.Figure, cog: bool = True) -> go.Figure:
        """Plot the packed shipment on a Plotly figure.

        Args:
            fig (go.Figure): The Plotly figure to add the shipment to.
            cog (bool): Whether to plot the center of gravity. Defaults to True.

        Returns:
            go.Figure: The updated Plotly figure.
        """
        x0 = self.position.x
        y0 = self.position.y
        x1 = self.position.x + self.shipment.length
        y1 = self.position.y + self.shipment.height
        fig.add_trace(
            go.Scatter(
                x=[x0, x1, x1, x0, x0],
                y=[y0, y0, y1, y1, y0],
                mode="lines",
                fill="toself",
                line={"width": 0.5},
                name=f"Shipment {self.shipment.identifier or ''}",
            ),
        )

        if cog:
            fig = self.plot_center_of_gravity(fig)
        return fig


class Container:
    """Represents a container for packing shipments."""

    shipments: list[PackedShipment]
    length: int
    height: int

    def __init__(self: Self, length: int, height: int) -> None:
        """Initialize a Container with specified dimensions.

        Args:
            length (int): The length of the container.
            height (int): The height of the container.
        """
        self.length = length
        self.height = height
        self.shipments = []
        self.map = self._init_map()

    @property
    def total_volume(self: Self) -> int:
        """Calculate the total volume of the container."""
        return self.length * self.height

    @property
    def remaining_volume(self: Self) -> int:
        """Calculate the remaining volume in the container."""
        return self.total_volume - sum(s.shipment.volume for s in self.shipments)

    @property
    def degree_of_filling(self: Self) -> float:
        """Calculate the degree of filling of the container."""
        return self.remaining_volume / self.total_volume

    @property
    def weight(self: Self) -> int:
        """Calculate the total weight of the packed shipments."""
        return sum(ps.shipment.weight for ps in self.shipments)

    @property
    def center_of_gravity(self: Self) -> Position:
        """Calculate the center of gravity of the packed shipments."""
        cog = Position(0, 0)
        for ps in self.shipments:
            cog += ps.center_of_gravity * ps.shipment.weight
        cog /= self.weight
        return cog

    @property
    def optimal_center_of_gravity(self: Self) -> Position:
        """Get the optimal center of gravity for the container."""
        return Position(self.length / 2, 0)

    @property
    def distance_optimal_cog(self: Self) -> float:
        """Calculate the distance from the optimal center of gravity."""
        return sqrt(
            (
                self.optimal_center_of_gravity.x
                - self.center_of_gravity.x
                + self.optimal_center_of_gravity.y
                - self.center_of_gravity.y
            )
            ** 2,
        )

    @property
    def valid(self: Self) -> bool:
        """Check if the container is valid."""
        valid = True
        valid &= self._check_ouf_bound_shipments()
        valid &= self._check__non_overlapping_shipments()
        return valid

    def _init_map(self: Self) -> np.ndarray[Any, np.dtype[np.int8]]:
        return np.zeros(shape=[self.length, self.height], dtype=np.int8)

    def _update_map(self: Self, ps: PackedShipment) -> None:
        x_start = ps.position.x
        y_start = ps.position.y
        x_end = x_start + ps.shipment.length
        y_end = y_start + ps.shipment.height

        self.map[x_start:x_end, y_start:y_end] += 1

    def _check_ouf_bound_shipments(self: Self) -> bool:
        """Check if all shipments are within the bounds of the container."""
        for packed_shipment in self.shipments:
            if (
                packed_shipment.position.x < 0
                or packed_shipment.position.y < 0
                or packed_shipment.position.x + packed_shipment.shipment.length
                > self.length
                or packed_shipment.position.y + packed_shipment.shipment.height
                > self.height
            ):
                return False
        return True

    def _check__non_overlapping_shipments(self: Self) -> bool:
        """Check if there are no overlapping shipments in the container."""
        for shipment1 in self.shipments:
            for shipment2 in self.shipments:
                if shipment1 != shipment2:
                    x1_1 = shipment1.position.x
                    y1_1 = shipment1.position.y
                    x1_2 = x1_1 + shipment1.shipment.length
                    y1_2 = y1_1 + shipment1.shipment.height

                    x2_1 = shipment2.position.x
                    y2_1 = shipment2.position.y
                    x2_2 = x2_1 + shipment2.shipment.length
                    y2_2 = y2_1 + shipment2.shipment.height

                    if not (
                        x1_2 <= x2_1 or x2_2 <= x1_1 or y1_2 <= y2_1 or y2_2 <= y1_1
                    ):
                        return False
        return True

    def pack(self: Self, shipment: Shipment, x: int, y: int) -> None:
        """Pack a shipment into the container at the specified position.

        Args:
            shipment (Shipment): The shipment to be packed.
            x (int): The x-coordinate of the position to pack the shipment.
            y (int): The y-coordinate of the position to pack the shipment.
        """
        ps = PackedShipment(shipment, Position(x, y))
        self.shipments.append(ps)
        self._update_map(ps)

    def plot_center_of_gravity(self: Self, fig: go.Figure) -> go.Figure:
        """Plot the center of gravity of the container on a Plotly figure.

        Args:
            fig (go.Figure): The Plotly figure to add the center of gravity marker to.

        Returns:
            go.Figure: The updated Plotly figure.
        """
        return fig.add_trace(
            go.Scatter(
                x=[self.center_of_gravity.x],
                y=[self.center_of_gravity.y],
                mode="markers",
                marker_symbol="cross-thin",
                marker_line_width=1,
                marker_line_color="red",
                name="G Container",
            ),
        )

    def plot(self: Self, cog: bool = True) -> go.Figure:
        """Plot the container and its packed shipments on a Plotly figure.

        Args:
            cog (bool): Whether to plot the center of gravity. Defaults to True.

        Returns:
            go.Figure: The Plotly figure representing the container and its contents.
        """
        fig = go.Figure()
        fig.add_shape(
            type="rect",
            x0=0,
            y0=0,
            x1=self.length,
            y1=self.height,
            line={"color": "black" if self.valid else "red", "width": 1},
            fillcolor=None,
        )

        for shipment in self.shipments:
            fig = shipment.plot(fig=fig, cog=cog)

        if cog:
            fig = self.plot_center_of_gravity(fig=fig)

        fig.update_yaxes(
            scaleanchor="x",
            scaleratio=1,
        )

        fig.update_layout(
            title=(
                f"2D Container Packing, "
                f"Valid: {self.valid}, "
                f"Distance optimal COG: {round(self.distance_optimal_cog, 2)}"
            ),
            xaxis={"range": [0 - 1, self.length + 1]},
            yaxis={"range": [0 - 1, self.height + 1]},
            showlegend=True,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        return fig

    def plot_map(self: Self) -> None:
        """Print the container's map using ASCII characters with an outline."""
        print(self.map)
        print("+" + "-" * self.length + "+")  # Container top outline
        for row in self.map.T[::-1]:
            row_str = "|"  # Left container outline
            row_str += "".join(["1" if val == 1 else "0" for val in row])
            row_str += "|"  # Right container outline
            print(row_str)
        print("+" + "-" * self.length + "+")  # Container bottom outline


# container = Container(5, 3)
# s1 = Shipment(1, 1, 40, identifier="aa")
# s2 = Shipment(1, 2, 20, identifier="bb")
# container.pack(shipment=s1, x=0, y=0)
# container.pack(shipment=s2, x=1, y=0)
# container.plot_map()
# container.plot().show(renderer="browser")
