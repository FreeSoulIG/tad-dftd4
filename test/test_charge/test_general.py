# This file is part of tad-dftd4.
#
# SPDX-Identifier: LGPL-3.0
# Copyright (C) 2022 Marvin Friede
#
# tad-dftd4 is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# tad-dftd4 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with tad-dftd4. If not, see <https://www.gnu.org/licenses/>.
"""
Testing the charges module
==========================

This module tests the EEQ charge model including:
 - single molecule
 - batched
 - ghost atoms
 - autograd via `gradcheck`

Note that `torch.linalg.solve` gives slightly different results (around 1e-5
to 1e-6) across different PyTorch versions (1.11.0 vs 1.13.0) for single
precision. For double precision, however the results are identical.
"""
from __future__ import annotations

import pytest
import torch

from tad_dftd4 import charges

from ..utils import get_device_from_str


@pytest.mark.parametrize("dtype", [torch.float16, torch.float32, torch.float64])
def test_change_type(dtype: torch.dtype) -> None:
    model = charges.ChargeModel.param2019().type(dtype)
    assert model.dtype == dtype


def test_change_type_fail() -> None:
    model = charges.ChargeModel.param2019()

    # trying to use setter
    with pytest.raises(AttributeError):
        model.dtype = torch.float64

    # passing disallowed dtype
    with pytest.raises(ValueError):
        model.type(torch.bool)


@pytest.mark.cuda
@pytest.mark.parametrize("device_str", ["cpu", "cuda"])
def test_change_device(device_str: str) -> None:
    device = get_device_from_str(device_str)
    model = charges.ChargeModel.param2019().to(device)
    assert model.device == device


def test_change_device_fail() -> None:
    model = charges.ChargeModel.param2019()

    # trying to use setter
    with pytest.raises(AttributeError):
        model.device = "cpu"


def test_init_dtype_fail() -> None:
    t = torch.rand(5)

    # all tensor must have the same type
    with pytest.raises(RuntimeError):
        charges.ChargeModel(t.type(torch.double), t, t, t)


@pytest.mark.cuda
def test_init_device_fail() -> None:
    t = torch.rand(5)

    # all tensor must be on the same device
    with pytest.raises(RuntimeError):
        charges.ChargeModel(t.to("cuda"), t, t, t)


@pytest.mark.cuda
def test_solve_dtype_fail() -> None:
    t = torch.rand(5)
    model = charges.ChargeModel.param2019()

    # all tensor must have the same type
    with pytest.raises(RuntimeError):
        charges.solve(t, t.type(torch.double), t, model, t)


@pytest.mark.cuda
def test_solve_device_fail() -> None:
    t = torch.rand(5)
    model = charges.ChargeModel.param2019()

    # all tensor must be on the same device
    with pytest.raises(RuntimeError):
        charges.solve(t, t.to("cuda"), t, model, t)
