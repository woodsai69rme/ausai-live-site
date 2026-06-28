import urllib.request
import zipfile
import os
import shutil

url = "https://github.com/lsdefine/GenericAgent/archive/refs/heads/main.zip"
zip_path = r"C:\Users\karma\ACTIVE_PROJECTS\GenericAgent.zip"
extract_dir = r"C:\Users\karma\ACTIVE_PROJECTS"
final_dir = r"C:\Users\karma\ACTIVE_PROJECTS\GenericAgent"

print(f"Downloading {url}...")
urllib.request.urlretrieve(url, zip_path)

print("Extracting...")
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

os.remove(zip_path)

extracted_folder = r"C:\Users\karma\ACTIVE_PROJECTS\GenericAgent-main"
if os.path.exists(extracted_folder):
    if os.path.exists(final_dir):
        shutil.rmtree(final_dir)
    os.rename(extracted_folder, final_dir)
    print(f"Successfully extracted to {final_dir}")
else:
    print("Extraction failed or folder structure unexpected.")
