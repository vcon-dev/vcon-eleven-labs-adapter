"""
Configuration management for the vCon ElevenLabs Adapter
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator


class ElevenLabsConfig(BaseModel):
    """ElevenLabs configuration"""

    api_key: str
    agent_ids: Any = Field(default_factory=list)
    poll_interval: int = 300
    batch_size: int = 10
    timeout: int = 30

    @field_validator("agent_ids", mode="before")
    @classmethod
    def validate_agent_ids(cls, v):
        """Validate and normalize agent_ids - can be 'all' string or list of IDs"""
        if isinstance(v, str):
            # Keep "all" as a string for the adapter to handle
            return v
        if isinstance(v, list):
            return v
        # Default to empty list
        return []


class FileExporterConfig(BaseModel):
    """File exporter configuration"""

    enabled: bool = True
    directory: str = "./vcons"
    overwrite: bool = False


class S3ExporterConfig(BaseModel):
    """S3 exporter configuration"""

    enabled: bool = False
    bucket: str
    region: str = "us-east-1"
    prefix: str = "elevenlabs/"
    encryption: str = "none"


class WebhookExporterConfig(BaseModel):
    """Webhook exporter configuration"""

    enabled: bool = False
    url: str
    api_key: Optional[str] = None
    auth_type: str = "none"
    batch_size: int = 10
    retry_attempts: int = 3


class ExportersConfig(BaseModel):
    """Exporters configuration"""

    file: FileExporterConfig = Field(default_factory=FileExporterConfig)
    s3: S3ExporterConfig = Field(default_factory=S3ExporterConfig)
    webhook: WebhookExporterConfig = Field(default_factory=WebhookExporterConfig)


class LoggingConfig(BaseModel):
    """Logging configuration"""

    level: str = "INFO"
    file: Optional[str] = None
    console: bool = True
    format: str = "text"


class VconConfig(BaseModel):
    """vCon configuration"""

    include_analysis: bool = True
    include_attachments: bool = True
    sign: bool = False
    encryption: str = "none"


class AdapterConfig(BaseModel):
    """Main adapter configuration"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    elevenlabs: ElevenLabsConfig
    exporters: ExportersConfig = Field(default_factory=ExportersConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    vcon: VconConfig = Field(default_factory=VconConfig)


def load_yaml_config(config_file: str) -> Dict[str, Any]:
    """
    Load YAML configuration file with environment variable substitution

    Args:
        config_file: Path to YAML configuration file

    Returns:
        Configuration dictionary
    """
    config_path = Path(config_file)

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")

    with open(config_path, "r") as f:
        content = f.read()

    content = _substitute_env_vars(content)

    return yaml.safe_load(content)


def _substitute_env_vars(content: str) -> str:
    """
    Substitute environment variables in format ${VAR_NAME}

    Args:
        content: String content to substitute

    Returns:
        Content with environment variables substituted
    """
    import re

    pattern = r"\$\{([^}]+)\}"

    def replacer(match):
        var_name = match.group(1)
        return os.environ.get(var_name, match.group(0))

    return re.sub(pattern, replacer, content)


def load_config(config_file: str) -> AdapterConfig:
    """
    Load and validate adapter configuration

    Args:
        config_file: Path to YAML configuration file

    Returns:
        Validated AdapterConfig instance
    """
    config_dict = load_yaml_config(config_file)

    return AdapterConfig(**config_dict)


def get_config_value(config: Dict[str, Any], path: str, default: Any = None) -> Any:
    """
    Get a nested config value using dot notation

    Args:
        config: Configuration dictionary
        path: Dot-separated path (e.g., "elevenlabs.api_key")
        default: Default value if not found

    Returns:
        Configuration value
    """
    keys = path.split(".")
    value = config

    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
            if value is None:
                return default
        else:
            return default

    return value
