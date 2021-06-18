import subprocess
import json
import argparse

parser = argparse.ArgumentParser(description="Prune unused docker containers")
parser.add_argument("project", type=str, help="Name of the project")
parser.add_argument("service", type=str, help="Name of the service")
parser.add_argument("region", type=str, help="Name of the region")
parser.add_argument("container", type=str, help="Name of the container")


def describe_service(project, service, region):
    result = subprocess.run(
        [f"gcloud run services describe {service} --project={project} --region={region} --format=json"],
        capture_output=True, shell=True)
    stdout = result.stdout.decode("utf-8")
    return json.loads(stdout)


def list_revisions(project, service, region):
    result = subprocess.run(
        [f"gcloud run revisions list --project={project} --service={service} --region={region} --format=json"],
        capture_output=True, shell=True)
    stdout = result.stdout.decode("utf-8")
    return json.loads(stdout)


def list_container_images(container_name):
    result = subprocess.run(
        [f"gcloud container images list-tags {container_name} --format=json"],
        capture_output=True, shell=True)
    stdout = result.stdout.decode("utf-8")
    return json.loads(stdout)


def delete_container(container_name, digest):
    result = subprocess.run(
        [f"gcloud container images delete {container_name}@{digest} --quiet --format=json"],
        capture_output=True, shell=True)
    stdout = result.stdout.decode("utf-8")
    print(stdout)
    return json.loads(stdout)


def prune_containers(project, container_name, service, region):
    container_name = container_name.split(":")[0]
    service_info = describe_service(project, service, region)

    active_revisions = [service["revisionName"]
                        for service in service_info["status"]["traffic"]]

    revisions = list_revisions(project, service, region)

    revision_containers = [revision["status"]["imageDigest"]
                           for revision in revisions
                           if revision["metadata"]["name"] in active_revisions]

    invalid_containers = [container
                          for container in revision_containers
                          if not container.startswith(container_name)]
    if len(invalid_containers) > 0:
        raise Exception(
            f"Invalid revision container name. Base container name {container_name} not found in {','.join(invalid_containers)}")

    container_digests = [container[len(container_name) + 1:]
                         for container in revision_containers]

    container_images = list_container_images(container_name)

    unused_container_digests = [
        image["digest"]
        for image in container_images
        if image["digest"] not in container_digests]

    if not unused_container_digests:
        print("No containers found to remove. Exiting.")
        return

    for digest in unused_container_digests:
        print(f"Deleting container {container_name}@{digest}")
        print(delete_container(container_name, digest))

    print("All containers removed")


def main():
    args = parser.parse_args()

    prune_containers(args.project, args.container, args.service, args.region)


if __name__ == "__main__":
    main()
