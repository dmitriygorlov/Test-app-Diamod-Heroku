import json

import pytest

from app import app, model
from model import CATEGORIES, load_model, predict

ROW = {"Carat Weight": 1.5, "Cut": "Ideal", "Color": "D", "Clarity": "VS1",
       "Polish": "EX", "Symmetry": "EX", "Report": "GIA"}


def test_prediction_form_and_api():
    client = app.test_client()
    assert client.get("/").status_code == 200
    assert client.get("/health").json["status"] == "ok"
    response = client.post("/predict_api", json=ROW)
    assert response.status_code == 200
    assert 0 < response.json < 100000
    # Form ordering must not alter feature order.
    form = client.post("/predict", data=dict(reversed(list(ROW.items()))))
    assert form.status_code == 200
    assert f"{response.json:.2f}$".encode() in form.data


@pytest.mark.parametrize("bad", [None, [], {}, {**ROW, "Carat Weight": "NaN"},
    {**ROW, "Carat Weight": True}, {**ROW, "Carat Weight": 0},
    {**ROW, "Cut": "unknown"}, {**ROW, "extra": 1}])
def test_invalid_input(bad):
    client = app.test_client()
    assert client.post("/predict_api", data=json.dumps(bad), content_type="application/json").status_code == 400


def test_malformed_json():
    assert app.test_client().post("/predict_api", data="{", content_type="application/json").status_code == 400


def test_all_categories_and_endpoints():
    for name, values in CATEGORIES.items():
        for value in values:
            assert predict({**ROW, name: value}, model) > 0
    for weight in (0.75, 2.9):
        assert predict({**ROW, "Carat Weight": weight}, model) > 0


def test_schema_rejection(tmp_path):
    path = tmp_path / "model.json"
    path.write_text(json.dumps({**model, "schema_version": 99}))
    with pytest.raises(ValueError, match="schema"):
        load_model(path)


def test_legacy_flawless_alias():
    assert predict({**ROW, "Clarity": "F"}, model) == predict({**ROW, "Clarity": "FL"}, model)
