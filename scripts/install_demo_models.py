"""Install bundled JSON inference models without replacing local training outputs."""

import json
from pathlib import Path

MODELS = {
    'profile_risk_model.json': 'profile-logreg-v2-no-avatar',
    'pair_risk_model.json': 'pair-text-logreg-v1-synthetic',
}


def install_models(project_root: Path) -> list[Path]:
    root = project_root.resolve()
    artifacts = []
    # Validate the complete release before installing any of its files.
    for name, model_id in MODELS.items():
        raw = (root / 'models' / name).read_bytes()
        model = json.loads(raw)
        if model.get('model_id') != model_id or not isinstance(model.get('coefficients'), list):
            raise ValueError(f'Unexpected bundled model: {name}')
        artifacts.append((name, raw))

    destination = root / 'outputs/ml'
    destination.mkdir(parents=True, exist_ok=True)
    installed = []
    for name, raw in artifacts:
        target = destination / name
        try:
            with target.open('xb') as output:
                output.write(raw)
        except FileExistsError:
            continue
        installed.append(target)
    return installed


if __name__ == '__main__':
    result = install_models(Path(__file__).resolve().parents[1])
    print(f'Installed {len(result)} bundled model(s); existing local models were preserved.')
