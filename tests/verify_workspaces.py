import requests
import shutil
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_workspace_crud():
    print("Testing Workspace CRUD...")
    
    ws_name = "test_workspace_123"
    new_name = "test_workspace_renamed"
    
    # 1. Create
    print(f"Creating workspace '{ws_name}'...")
    res = requests.post(f"{BASE_URL}/workspaces", json={"name": ws_name})
    if res.status_code != 200:
        print(f"FAILED to create: {res.text}")
        return
    print("Created successfully.")
    
    # 2. List
    print("Listing workspaces...")
    res = requests.get(f"{BASE_URL}/workspaces")
    workspaces = res.json()
    found = any(ws['name'] == ws_name for ws in workspaces)
    if not found:
        print("FAILED: Workspace not found in list")
        return
    print("Listed successfully.")

    # 3. Rename
    print(f"Renaming to '{new_name}'...")
    res = requests.patch(f"{BASE_URL}/workspaces/{ws_name}", json={"new_name": new_name})
    if res.status_code != 200:
        print(f"FAILED to rename: {res.text}")
        return
    print("Renamed successfully.")
    
    # 4. Verify Rename
    res = requests.get(f"{BASE_URL}/workspaces")
    workspaces = res.json()
    found_old = any(ws['name'] == ws_name for ws in workspaces)
    found_new = any(ws['name'] == new_name for ws in workspaces)
    if found_old or not found_new:
        print("FAILED: Rename verification failed")
        return
    print("Rename verified.")

    # 5. Delete
    print(f"Deleting '{new_name}'...")
    res = requests.delete(f"{BASE_URL}/workspaces/{new_name}")
    if res.status_code != 200:
        print(f"FAILED to delete: {res.text}")
        return
    print("Deleted successfully.")
    
    # 6. Verify Delete
    res = requests.get(f"{BASE_URL}/workspaces")
    workspaces = res.json()
    found = any(ws['name'] == new_name for ws in workspaces)
    if found:
        print("FAILED: Workspace still exists after delete")
        return
    print("Delete verified.")
    print("ALL TESTS PASSED.")

if __name__ == "__main__":
    test_workspace_crud()
