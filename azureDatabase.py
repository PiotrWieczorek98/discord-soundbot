import os
from azure.storage.blob import BlobServiceClient


# Upload to cloud
def upload_to_azure(file_loc: str, file_name: str, container_name: str):
    try:
        # Create the BlobServiceClient object which will be used to create a container client
        connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)

        # Create a blob client using the local file name as the name for the blob
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)

        # Upload the created file
        print("\nUploading to Azure Storage as blob: " + file_loc)
        with open(file_loc, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
    except:
        print("failed uploading txt to azure")


# Download from cloud
def download_from_azure(file_loc: str, container_name: str, overwrite: bool):
    try:
        # Create the BlobServiceClient object which will be used to create a container client
        connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)

        # Get container
        container_client = blob_service_client.get_container_client(container_name)

        # Download files
        loc_base = file_loc
        for blob in container_client.list_blobs():
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob.name)
            file_loc = loc_base + blob.name
            if not os.path.isfile(file_loc) or overwrite:
                print("Downloading blob to " + file_loc)
                with open(file_loc, "wb") as download_file:
                    download_file.write(blob_client.download_blob().readall())
    except:
        print("failed downloading mp3 from azure")