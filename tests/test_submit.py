"""Tests for runpod_tools.submit."""

from unittest.mock import MagicMock, patch

import pytest

from runpod_tools.submit import launch_training_job, terminate_job


@pytest.fixture(name="image_name")
def fixture_image_name() -> str:
    """Provide a valid GHCR image name for testing."""
    return "ghcr.io/username/repo:tag"  # Replace with a real image for an actual test


def test_launch_training_job(image_name: str) -> None:
    """Tests whether we can launch a training job on RunPod."""
    # GIVEN a valid GHCR image and command
    command = "echo Hello, RunPod!"

    # GIVEN mocked environment variables for API key and GHCR credentials
    mocked_env_vars = {
        "RUNPOD_API_KEY": "mocked_api_key",
        "GHCR_USERNAME": "mocked_username",
        "GHCR_PAT": "mocked_pat",
    }
    # GIVEN a mocked run_pod.create_pod to avoid real API calls
    # GIVEN a mocked  runpod.create_container_registry_auth to avoid real API calls for registry authentication
    with (
        patch.dict("os.environ", mocked_env_vars),
        patch("runpod_tools.submit.runpod.create_pod") as mock_create_pod,
        patch("runpod_tools.submit.runpod.create_container_registry_auth") as mock_create_container_registry_auth,
    ):
        mock_create_pod.return_value = {"id": "mocked_pod_id"}
        mock_create_container_registry_auth.return_value = {
            "username": mocked_env_vars["GHCR_USERNAME"],
            "password": mocked_env_vars["GHCR_PAT"],
        }

        # WHEN we launch the training job
        pod_id = launch_training_job(image_name, command)

    # THEN we should get the mocked pod ID back
    assert pod_id == "mocked_pod_id"

    # THEN the create_pod function should be called with the correct parameters, including registry credentials
    mock_create_pod.assert_called_once_with(
        name="auto-job-repo",
        image_name=image_name,
        gpu_type_id="NVIDIA GeForce RTX 4090",
        gpu_count=1,
        volume_in_gb=50,
        container_disk_in_gb=20,
        docker_args=command,
    )


def test_terminate_job() -> None:
    """Tests whether we can terminate a RunPod job."""
    # GIVEN a launched job
    dummy_job = MagicMock()
    dummy_job.id = "dummy_job_id"

    # WHEN we terminate the job
    with patch("runpod_tools.submit.runpod.terminate_pod") as mock_terminate_pod:
        terminate_job(dummy_job.id)

    # THEN we should see logs confirming termination (manual verification needed)
    # AND the terminate_pod function should be called with the correct pod ID
    mock_terminate_pod.assert_called_once_with("dummy_job_id")
