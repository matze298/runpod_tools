"""Test script that submits a simple "Hello, World!" task to the cheapest CPU instance type available on RunPod."""

from runpod_tools.submit import launch_training_job
import runpod
import time

if __name__ == "__main__":
    pod_id = launch_training_job(
        image_name="runpod/base:1.0.2-ubuntu2204",
        command="echo 'Hello, World!' && sleep 10",  # Sleep added to keep the pod alive for a short time to verify it runs
        volume_in_gb=1,
        cpu_type_id="cpu3c-2-4",
    )

    if pod_id:
        print(f"Pod ID: {pod_id}")
    else:
        print("Pod creation failed.")
        exit(1)

    # Check status for 2 minutes, polling every 15 seconds
    start_time = time.time()
    while time.time() - start_time < 120:
        time.sleep(15)
        pod = runpod.get_pod(pod_id)
        if pod["status"] == "finished":
            print("Pod finished successfully!")
        else:
            print(f"Pod status: {pod['status']}")
