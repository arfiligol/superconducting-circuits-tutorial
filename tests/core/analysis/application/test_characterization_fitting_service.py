"""Tests for Characterization fitting application service."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

import numpy as np
from sqlmodel import Session, SQLModel, create_engine

from core.analysis.application.analysis.physics.admittance import (
    calculate_y11_imaginary,
)
from core.analysis.application.services.characterization_fitting_service import (
    CharacterizationFittingService,
    SquidFittingConfig,
    Y11FittingConfig,
)
from core.shared.persistence.models import DataRecord, DatasetRecord
from core.shared.persistence.unit_of_work import SqliteUnitOfWork


def _build_uow_factory(tmp_path: Path):
    db_path = tmp_path / "characterization_fit.sqlite"
    engine = create_engine(f"sqlite:///{db_path}")
    SQLModel.metadata.create_all(engine)

    @contextmanager
    def _factory():
        with Session(engine) as session:
            yield SqliteUnitOfWork(session=session)

    return _factory


def _seed_y11_dataset(uow_factory) -> tuple[int, int]:
    freq_ghz = np.linspace(4.0, 8.0, 201)
    l_jun_nh = np.linspace(0.8, 2.8, 9)
    values_matrix = [
        [
            float(
                calculate_y11_imaginary(
                    float(l_value),
                    float(freq_value),
                    Ls1_nH=0.02,
                    Ls2_nH=0.03,
                    C_pF=1.0,
                )
            )
            for l_value in l_jun_nh
        ]
        for freq_value in freq_ghz
    ]

    with uow_factory() as uow:
        dataset = DatasetRecord(name="characterization-fit", source_meta={}, parameters={})
        uow.datasets.add(dataset)
        uow.flush()
        assert dataset.id is not None

        base_record = DataRecord(
            dataset_id=dataset.id,
            data_type="y_parameters",
            parameter="Y11",
            representation="imaginary",
            axes=[
                {"name": "Freq", "unit": "GHz", "values": [float(x) for x in freq_ghz]},
                {"name": "L_jun", "unit": "nH", "values": [float(x) for x in l_jun_nh]},
            ],
            values=values_matrix,
        )
        uow.data_records.add(base_record)
        uow.commit()
        assert base_record.id is not None
        return int(dataset.id), int(base_record.id)


def test_squid_fitting_run_persists_contract(tmp_path: Path, monkeypatch) -> None:
    uow_factory = _build_uow_factory(tmp_path)
    monkeypatch.setattr(
        "core.analysis.application.services.characterization_fitting_service.get_unit_of_work",
        uow_factory,
    )
    monkeypatch.setattr(
        "core.analysis.application.services.fit_result_persistence.get_unit_of_work",
        uow_factory,
    )
    dataset_id, record_id = _seed_y11_dataset(uow_factory)

    summary = CharacterizationFittingService().run_squid_fitting(
        dataset_id=dataset_id,
        config=SquidFittingConfig(
            fit_model="WITH_LS",
            ls_min_nh=0.0,
            ls_max_nh=None,
            c_min_pf=0.0,
            c_max_pf=None,
            fixed_c_pf=None,
            fit_min_nh=None,
            fit_max_nh=None,
        ),
        record_ids=[record_id],
        trace_mode_group="base",
    )

    assert summary["method"] == "lc_squid_fit"
    assert summary["created_data_records"] > 0
    assert summary["created_derived_parameters"] > 0

    with uow_factory() as uow:
        params = [
            param
            for param in uow.derived_params.list_by_dataset(dataset_id)
            if param.method == "lc_squid_fit"
        ]
        assert params
        assert {param.extra.get("trace_mode_group") for param in params} == {"base"}


def test_y11_fitting_run_persists_contract(tmp_path: Path, monkeypatch) -> None:
    uow_factory = _build_uow_factory(tmp_path)
    monkeypatch.setattr(
        "core.analysis.application.services.characterization_fitting_service.get_unit_of_work",
        uow_factory,
    )
    monkeypatch.setattr(
        "core.analysis.application.services.fit_result_persistence.get_unit_of_work",
        uow_factory,
    )
    dataset_id, record_id = _seed_y11_dataset(uow_factory)

    summary = CharacterizationFittingService().run_y11_fitting(
        dataset_id=dataset_id,
        config=Y11FittingConfig(
            ls1_init_nh=0.02,
            ls2_init_nh=0.03,
            c_init_pf=1.0,
            c_max_pf=3.0,
        ),
        record_ids=[record_id],
        trace_mode_group="sideband",
    )

    assert summary["method"] == "y11_fit"
    assert summary["created_data_records"] == 2
    assert summary["created_derived_parameters"] == 4

    with uow_factory() as uow:
        params = [
            param
            for param in uow.derived_params.list_by_dataset(dataset_id)
            if param.method == "y11_fit"
        ]
        names = {param.name for param in params}
        assert names == {"Ls1_nH", "Ls2_nH", "C_pF", "RMSE"}
        assert {param.extra.get("trace_mode_group") for param in params} == {"sideband"}
