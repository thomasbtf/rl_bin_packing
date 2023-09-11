"""Useful helpers."""
import random
import string
from dataclasses import fields
from typing import Any, Self


class DataClassGenerator:
    def __init__(self, data_class: type, **kwargs: Any) -> None:
        self.data_class = data_class
        self.max_values = kwargs

    def generate_instances(self: Self, num_instances: int) -> list[type]:
        instances = []
        data_fields = [field.name for field in fields(self.data_class)]

        for _ in range(num_instances):
            instance_fields = {}
            for field in data_fields:
                if field in self.max_values:
                    max_value = self.max_values[field]
                    if isinstance(max_value, bool):
                        instance_fields[field] = random.choice([True, False])
                    elif isinstance(max_value, float):
                        instance_fields[field] = random.uniform(1, max_value)
                    elif isinstance(max_value, str):
                        letters = [*string.ascii_lowercase]
                        instance_fields[field] = "".join(
                            random.choice(letters) for _ in range(len(max_value))
                        )
                    else:
                        instance_fields[field] = random.randint(1, max_value)
                else:
                    instance_fields[field] = None

            instance = self.data_class(**instance_fields)
            instances.append(instance)

        return instances
