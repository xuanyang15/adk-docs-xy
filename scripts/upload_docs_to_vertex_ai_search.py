import os

from dotenv import load_dotenv

from google.cloud import storage
from google.cloud import discoveryengine_v1beta as discoveryengine
from google.api_core.exceptions import GoogleAPICallError

load_dotenv(override=True)

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
DATA_STORE_ID = os.getenv("DATA_STORE_ID")
DATA_STORE_LOCATION = os.getenv("DATA_STORE_LOCATION")
GCS_DESTINATION_PREFIX = os.getenv("GCS_DESTINATION_PREFIX")


LOCAL_DIRECTORY_PATH = ".."


def cleanup_gcs_prefix(bucket_name: str, prefix: str) -> bool:
    """Delete all the objects with the given prefix in the bucket."""
    print(f"Start cleaning up GCS: gs://{bucket_name}/{prefix}...")
    try:
        storage_client = storage.Client(project=GOOGLE_CLOUD_PROJECT)
        bucket = storage_client.bucket(bucket_name)
        blobs = list(bucket.list_blobs(prefix=prefix))

        if not blobs:
            print("GCS target location is already empty, no need to clean up.")
            return True

        bucket.delete_blobs(blobs)
        print(f"Successfully deleted {len(blobs)} objects.")
        return True
    except GoogleAPICallError as e:
        print(f"Failed to clean up GCS: {e}")
        return False


def main():
    """Main function to upload the docs."""
    if not cleanup_gcs_prefix(GCS_BUCKET_NAME, GCS_DESTINATION_PREFIX):
        print("Failed to clean up GCS. Exiting...")
        return

    print("Uploaded all the docs to GCS.")


if __name__ == "__main__":
    main()
