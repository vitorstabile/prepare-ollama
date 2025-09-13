import docker
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Prepare Ollama image with DeepSeek-R1 for offline use")
    parser.add_argument(
        "--model",
        default="deepseek-r1:1.5b",
        help="DeepSeek-R1 model to use (e.g., deepseek-r1:1.5b, deepseek-r1:8b, deepseek-r1:14b)"
    )
    parser.add_argument(
        "--output",
        default="/app/output/ollama-deepseek-1.5b.tar",
        help="Name of the .tar file to export the image"
    )
    parser.add_argument(
        "--image-name",
        default=None,
        help="Name of the resulting Docker image (default: ollama-with-<model>)"
    )
    args = parser.parse_args()

    MODEL = args.model
    OUTPUT_TAR = args.output
    IMAGE_NAME = args.image_name or f"ollama-with-{MODEL.replace(':','-')}"

    client = docker.from_env()
    low_level_client = docker.APIClient(base_url='unix://var/run/docker.sock', timeout=600)

    print("==> 1. Pulling base Ollama image...")
    base_image = "ollama/ollama:latest"
    client.images.pull(base_image)

    print("==> 2. Creating temporary container...")
    container = client.containers.run(
        base_image,
        detach=True,
        tty=True
    )

    try:
        print(f"==> 3. Pulling model {MODEL} inside the container...")
        exec_log = container.exec_run(f"ollama pull {MODEL}", stdout=True, stderr=True, stream=True)
        for chunk in exec_log[1]:
            sys.stdout.write(chunk.decode(errors="ignore"))
            sys.stdout.flush()

        print("==> 4. Stopping temporary container...")
        container.stop()

        print(f"==> 5. Creating new image '{IMAGE_NAME}' with the embedded model...")
        image = low_level_client.commit(
            container=container.id,
            repository=IMAGE_NAME.split(":")[0],
            tag=IMAGE_NAME.split(":")[1] if ":" in IMAGE_NAME else "latest"
        )

        print(f"==> 6. Saving image to '{OUTPUT_TAR}'...")
        image_id = image['Id']
        with open(OUTPUT_TAR, "wb") as f:
            for chunk in low_level_client.get_image(image_id):
                f.write(chunk)

        print("Finished!")
        print(f"Image saved to: {OUTPUT_TAR}")
        print("On the offline server, run:")
        print(f"  docker load -i {OUTPUT_TAR}")
        print(f"Your image will be available as '{IMAGE_NAME}'.")

    finally:
        print("==> Cleaning up temporary container...")
        try:
            container.remove(force=True)
        except Exception:
            pass

if __name__ == "__main__":
    main()
