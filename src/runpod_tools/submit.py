"""Submit dockerized code to RunPod."""

import runpod
import os
import logging

_LOGGER = logging.getLogger(__name__)


def launch_training_job(
    image_name: str,
    command: str,
    gpu_type_id: str = "NVIDIA GeForce RTX 4090",
    gpu_count: int = 1,
    volume_in_gb: int = 50,
) -> str | None:
    """Spins up a RunPod instance, pulls a GHCR image, and runs a command."""
    # Ensure your API key is set in your local environment variables
    runpod.api_key = os.getenv("RUNPOD_API_KEY")
    if not runpod.api_key:
        raise ValueError("RUNPOD_API_KEY environment variable is missing.")

    _LOGGER.info(f"🚀 Provisioning {gpu_count}x {gpu_type_id}...")

    # Log into GHCR if credentials are provided
    username = os.getenv("GHCR_USERNAME")
    password = os.getenv("GHCR_PAT")
    if username and password:
        runpod.create_container_registry_auth(
            name="ghcr",
            username=username,
            password=password,
        )
        _LOGGER.info("🔐 Authenticated with GHCR successfully.")

    try:
        pod = runpod.create_pod(
            name=f"auto-job-{image_name.rsplit('/', maxsplit=1)[-1].split(':', maxsplit=1)[0]}",
            image_name=image_name,
            gpu_type_id=gpu_type_id,
            gpu_count=gpu_count,
            volume_in_gb=volume_in_gb,
            container_disk_in_gb=20,
            docker_args=command,  # The command to run on startup
        )

        pod_id = pod["id"]
        _LOGGER.info(f"✅ Pod {pod_id} created successfully!")
        _LOGGER.info(f"📦 Pulling {image_name} and executing: '{command}'")

        return pod_id

    except Exception as e:
        _LOGGER.error(f"❌ Failed to create pod: {e}")
        return None


def terminate_job(pod_id: str) -> None:
    """Destroys the pod."""
    runpod.api_key: str | None = os.getenv("RUNPOD_API_KEY")
    _LOGGER.info(f"🗑️ Terminating pod {pod_id}...")
    runpod.terminate_pod(pod_id)
    _LOGGER.info("✅ Pod terminated.")
