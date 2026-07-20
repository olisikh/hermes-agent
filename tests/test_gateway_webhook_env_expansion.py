"""Gateway config must expand ${VAR} references before constructing webhook routes."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import yaml


def test_gateway_expands_webhook_route_secret_env_reference() -> None:
    from gateway.config import Platform, load_gateway_config

    yaml_config = {
        "platforms": {
            "webhook": {
                "enabled": True,
                "extra": {
                    "routes": {
                        "plane-work-item": {
                            "secret": "${PLANE_HERMES_WEBHOOK_SECRET}",
                            "prompt": "test",
                            "deliver": "log",
                        }
                    }
                },
            }
        }
    }

    with TemporaryDirectory() as temp_dir:
        home = Path(temp_dir)
        (home / "config.yaml").write_text(yaml.safe_dump(yaml_config), encoding="utf-8")
        with (
            patch("gateway.config.get_hermes_home", return_value=home),
            patch.dict(os.environ, {"PLANE_HERMES_WEBHOOK_SECRET": "resolved-secret"}, clear=False),
        ):
            cfg = load_gateway_config()

    route = cfg.platforms[Platform.WEBHOOK].extra["routes"]["plane-work-item"]
    assert route["secret"] == "resolved-secret"
