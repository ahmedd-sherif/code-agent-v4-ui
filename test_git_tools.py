from code_agent.tools.git_tools import clone_repository, git_status, git_add_all, git_commit
import os
import shutil

TEST_DIR = "test_git_repo"

# cleanup if exists
if os.path.exists(TEST_DIR):
    shutil.rmtree(TEST_DIR)

print("\n--- Testing Clone ---")
# Using a small public repo for testing
repo_url = "https://github.com/octocat/Hello-World.git" 
result = clone_repository(repo_url, TEST_DIR)
print(result)

if os.path.exists(TEST_DIR):
    print("\n--- Testing Status ---")
    print(git_status(TEST_DIR))
    
    print("\n--- Testing Modification ---")
    with open(f"{TEST_DIR}/test_file.txt", "w") as f:
        f.write("Test change")
    
    print(git_status(TEST_DIR))
    
    print("\n--- Testing Add ---")
    print(git_add_all(TEST_DIR))
    
    print("\n--- Testing Commit ---")
    # This might fail if user email/name not configured globally or in repo, 
    # but the tool logic is wrapper around git so it tests the python code.
    print(git_commit(TEST_DIR, "Test commit from Agent"))
    
    print("\nSUCCESS: Git tools verify script finished.")
else:
    print("\nFAILURE: Clone failed.")

# Cleanup
# if os.path.exists(TEST_DIR):
#    shutil.rmtree(TEST_DIR)
