# Runtime/model modernization (2026-11-18)

The web application still estimates diamond prices from seven named characteristics.
The historical notebook and `le_model_03012021.pkl` are unchanged and retained as evidence.

## Versions and model compatibility

- Python: previously unspecified → 3.15.2 (Docker and .python-version).
- Flask 1.1.1 → 3.1.3; gunicorn 19.9.0 → 27.0.1.
- PyCaret 2.3.3 is replaced for serving. Its current 3.3.2 release still requires
  NumPy <1.27 and pandas <2.2, so it does not offer the current numerical stack used here.
- Training uses scikit-learn 1.9.1, NumPy 2.5.5, pandas 3.1.1.
- Old direct Jinja2 2.11.3 / itsdangerous 1.1.0 / certifi 2019.11.28 pins were removed;
  Flask resolves maintained compatible transitive packages.
- The old pickle references PyCaret internal preprocessing, sklearn and LightGBM.
  A separate network-isolated load attempt in the modern training container fails with
  `ModuleNotFoundError: pycaret`. It is **not** a migrated pickle.
  Old-environment inference was not reproduced, so prediction parity is not claimed.
- The replacement is a regularized linear model of log price, using log carat,
  its square and one-hot categories. It exports coefficients and a versioned schema to JSON.
  Serving uses standard-library math, without sklearn or pickle loading.

## Reproduce training

Download [the historical PyCaret diamond CSV](https://raw.githubusercontent.com/pycaret/datasets/main/data/common/diamond.csv)
to a local file. The training script rejects any bytes whose SHA-256 differs from
`aa8e835297ff307efadf789e6fb33d288645ece2bb4335113ec3c071375f4dc9`.
The dataset is not republished here; its historical acknowledgement remains in README.

```sh
pip install -r requirements-train.txt
python train.py diamond.csv --output diamond_model.json
```

This uses 5400 of the 6000 original records for training and 600 for holdout,
seed 786, with no refit on the holdout. Observed MAE: 997.891845 USD; R²: 0.963080537.
Median-price baseline MAE on the same holdout: 6630.66 USD.
The exported scorer is checked against sklearn predictions for every holdout record
within the 0.0051 USD rounding tolerance. The split differs from the original notebook:
these numbers are not evidence of an improvement over the old model or of current market accuracy.

## Run and validate

```sh
pip install -r requirements-dev.txt
python -m pytest -q
python -m pip check
ruff check .
docker build --target test -t diamond-test .
docker run --rm --network none --read-only --tmpfs /tmp diamond-test
docker build --target runtime -t diamond .
docker run --rm -p 127.0.0.1:8000:8000 diamond
```

Open localhost:8000. POST /predict accepts form fields; POST /predict_api accepts the same
fields in a JSON object and still returns a JSON number. /health checks that the model loaded.
Invalid/missing/extra fields, nonfinite weights and unknown categories return HTTP 400.
Form order no longer affects predictions. Historical `Clarity=F` maps to dataset `FL`;
the UI now uses FL and allows the actual source maximum of 2.91 carats.
Flask debug mode is off; external font requests were removed.

## Deployment gate and rollback

GitHub has an active `kolkrabbi.heroku.com` webhook and historical deployments to
`how-big-is-love`. The old public URL returned HTTP 404 on 2026-11-18, which does not
prove the account/app integration is disabled. No Heroku settings were changed.
Do not merge this branch until the owner dashboard establishes the deployment state,
supported Python runtime and last known-good Heroku release. No live deployment was performed.

Source rollback baseline: `4a374a33b9bfdf998e341ed0cdb48ab4f7326db7`.
A source revert alone may not recover the old dependency environment. Retain the deployed
slug/image and use Heroku's previous known-good release for operational rollback.
The new JSON artifact can be rolled back together with its matching app/model.py revision.
