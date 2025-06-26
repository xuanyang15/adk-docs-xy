import os
from pathlib import Path

from dotenv import load_dotenv

from google.cloud import storage
from google.cloud import discoveryengine_v1beta as discoveryengine
from google.api_core.exceptions import GoogleAPICallError

load_dotenv(override=True)

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
GCS_DESTINATION_PREFIX = os.getenv("GCS_DESTINATION_PREFIX")
COLLECTION_ID = os.getenv("COLLECTION_ID")
DATA_STORE_ID = os.getenv("DATA_STORE_ID")
DATA_STORE_LOCATION = os.getenv("DATA_STORE_LOCATION")

LOCAL_DIRECTORY_PATH = Path(__file__).parent / ".."


def cleanup_gcs_prefix(project_id: str, bucket_name: str, prefix: str) -> bool:
    """Delete all the objects with the given prefix in the bucket."""
    print(f"Start cleaning up GCS: gs://{bucket_name}/{prefix}...")
    try:
        storage_client = storage.Client(project=project_id)
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


def upload_directory_to_gcs(
    source_directory: str, project_id: str, bucket_name: str, prefix: str
) -> bool:
    """Upload the whole directory into GCS."""
    print(
        f"Start uploading directory {source_directory} to GCS: gs://{bucket_name}/{prefix}..."
    )

    if not os.path.isdir(source_directory):
        print(f"[Error] {source_directory} is not a directory or does not exist.")
        return False

    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    for root, dirs, files in os.walk(source_directory):
        # Exclude hidden dirs and files

        # 1. Modify the 'dirs' list in-place to prevent os.walk from descending
        # into hidden directories.
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        # 2. Filter out hidden files from the current directory's file list.
        files = [f for f in files if not f.startswith(".")]

        for filename in files:
            if not filename.lower().endswith(".md") and not filename.lower().endswith(
                ".py"
            ):
                continue

            local_path = os.path.join(root, filename)
            relative_path = os.path.relpath(local_path, source_directory)
            gcs_path = os.path.join(prefix, relative_path)

            try:
                blob = bucket.blob(gcs_path)
                content_type = None
                if filename.lower().endswith(".md"):
                    # Vertex AI search doesn't recognize text/markdown, use text/html instead
                    content_type = "text/html"
                if filename.lower().endswith(".py"):
                    # Use plain text for Python code
                    content_type = "text/plain"

                blob.upload_from_filename(local_path, content_type=content_type)
                type_msg = (
                    f"(type {content_type})" if content_type else "(type auto-detect)"
                )
                print(
                    f"  - Uploaded {type_msg}: {local_path} -> gs://{bucket_name}/{gcs_path}"
                )
            except GoogleAPICallError as e:
                print(f"Error uploading file {local_path}: {e}")
                return False

    print("Sucessfully uploaded all the docs to GCS.")
    return True


def import_from_gcs_to_vertex_ai(
    project_id: str,
    location: str,
    collection_id: str,
    data_store_id: str,
    gcs_bucket: str,
    gcs_prefix: str,
) -> bool:
    """
    Triggers a bulk import task from a GCS folder to Vertex AI Search
    using FULL reconciliation mode to ensure the datastore matches the source.
    """
    print(f"Triggering FULL SYNC import from gs://{gcs_bucket}/{gcs_prefix}...")

    try:
        client = discoveryengine.DocumentServiceClient()
        parent = (
            f"projects/{project_id}/locations/{location}/collections/{collection_id}"
            f"/dataStores/{data_store_id}/branches/default_branch"
        )

        gcs_uri = f"gs://{gcs_bucket}/{gcs_prefix}/*"

        request = discoveryengine.ImportDocumentsRequest(
            parent=parent,
            # Specify the GCS source and use "content" for unstructed data.
            gcs_source=discoveryengine.GcsSource(input_uris=[gcs_uri], data_schema="content"),
            reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.FULL,
        )

        operation = client.import_documents(request=request)
        print(
            "Successfully started full sync import operation."
            f"Operation Name: {operation.operation.name}"
        )
        return True

    except GoogleAPICallError as e:
        print(f"Error triggering import: {e}")
        return False


def main():
    """Main function to upload the docs."""
    if not cleanup_gcs_prefix(
        GOOGLE_CLOUD_PROJECT, GCS_BUCKET_NAME, GCS_DESTINATION_PREFIX
    ):
        print("Failed to clean up GCS. Exiting...")
        return

    if not upload_directory_to_gcs(
        LOCAL_DIRECTORY_PATH,
        GOOGLE_CLOUD_PROJECT,
        GCS_BUCKET_NAME,
        GCS_DESTINATION_PREFIX,
    ):
        print("Failed to upload docs to GCS. Exiting...")
        return

    # 3. Trigger a full import from GCS to Vertex AI Search.
    if not import_from_gcs_to_vertex_ai(
        GOOGLE_CLOUD_PROJECT,
        DATA_STORE_LOCATION,
        COLLECTION_ID,
        DATA_STORE_ID,
        GCS_BUCKET_NAME,
        GCS_DESTINATION_PREFIX,
    ):
        print("Failed to trigger import. Exiting...")
        return

    print("--- Sync task has been successfully initiated ---")


if __name__ == "__main__":
    main()
