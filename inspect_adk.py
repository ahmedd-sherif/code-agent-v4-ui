import google.adk
print("google.adk dir:", dir(google.adk))

try:
    import google.adk.types
    print("google.adk.types dir:", dir(google.adk.types))
except ImportError:
    print("No google.adk.types")

try:
    from google.adk.types import UserMessage
    print("UserMessage found!")
except ImportError:
    print("UserMessage not found in types")
