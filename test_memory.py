from code_agent.storage import create_session, add_message, get_session_history, list_sessions
import time

print("\n--- Testing Memory ---")

# 1. Create session
session_id = f"sess_{int(time.time())}"
print(f"Creating session: {session_id}")
create_session(session_id, "Test Session")

# 2. Add messages
print("Adding messages...")
add_message(session_id, "user", "Hello, do you remember me?")
add_message(session_id, "assistant", "Yes, I have persistent memory now!")

# 3. Read history
print("\nReading history:")
history = get_session_history(session_id)
for msg in history:
    print(f"[{msg['role']}]: {msg['content']}")

# 4. List sessions
print("\nListing sessions:")
sessions = list_sessions()
print(f"Found {len(sessions)} sessions.")
found = any(s['session_id'] == session_id for s in sessions)

if history and found:
    print("\nSUCCESS: Memory DB works!")
else:
    print("\nFAILURE: Memory test failed.")
