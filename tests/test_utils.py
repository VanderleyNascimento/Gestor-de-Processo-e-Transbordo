import pandas as pd
import utils


def test_validate_dataframe_schema_required_and_recommended():
    df = pd.DataFrame({"agência_destino_anotacao": ["A1"], "seal": ["S1"]})
    report = utils.validate_dataframe_schema(df)

    assert report["is_valid"] is True
    assert report["missing_required"] == []
    assert "package_id" in report["missing_recommended"]


def test_deduplicate_packages_prioritizes_package_id_then_barcode():
    df = pd.DataFrame(
        {
            "package_id": ["P1", "P1", None, None, "P2"],
            "barcode": ["B1", "B1", "B3", "B3", "B2"],
            "agência_destino_anotacao": ["A", "A", "A", "A", "B"],
        }
    )

    deduped, info = utils.deduplicate_packages(df)

    assert len(deduped) == 3
    assert info["removed"] == 2
    assert info["strategy"] == "package_id+barcode"


def test_process_data_sets_status_prazo_vectorized():
    today = pd.Timestamp.now().normalize()
    df = pd.DataFrame(
        {
            "agência_destino_anotacao": ["A", "A", "A", "A"],
            "promised_date": [
                (today - pd.Timedelta(days=1)).strftime("%d/%m/%Y"),
                today.strftime("%d/%m/%Y"),
                (today + pd.Timedelta(days=1)).strftime("%d/%m/%Y"),
                (today + pd.Timedelta(days=2)).strftime("%d/%m/%Y"),
            ],
        }
    )

    out = utils.process_data(df, trasbordo_list=["A"])

    assert out["Categoria"].eq("Transbordo").all()
    assert list(out["Status_Prazo"]) == ["Atrasado", "Vence Hoje", "Atenção", "No Prazo"]


def test_group_data_by_seal_handles_missing_optional_columns():
    df = pd.DataFrame(
        {
            "seal": ["S1", "S1", "S2"],
            "agência_destino_anotacao": ["A", "A", "B"],
        }
    )

    grouped = utils.group_data_by_seal(df)

    assert set(grouped["seal"]) == {"S1", "S2"}
    assert grouped.loc[grouped["seal"] == "S1", "Qtd_Pacotes"].iloc[0] == 2
    assert "Tipo_Veiculo" in grouped.columns
    assert "Identificador" in grouped.columns


def test_calculate_slo_uses_config_and_generates_status():
    today = pd.Timestamp.now().normalize()
    promised = today + pd.Timedelta(days=3)
    df = pd.DataFrame(
        {
            "agência_destino_anotacao": ["AG1"],
            "promised_date": [promised.strftime("%d/%m/%Y")],
            "seal": ["S1"],
        }
    )
    cfg = {"AG1": {"transit_time": 1, "agency_time": 1}}

    out = utils.calculate_slo(df, cfg)

    expected_limit = promised - pd.Timedelta(days=3)
    assert out["Data_Limite_Expedicao"].iloc[0].normalize() == expected_limit
    assert out["Status_Expedicao"].iloc[0] == "Expedir Hoje"
