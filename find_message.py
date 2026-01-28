import google.adk
import pkgutil
import inspect

def find_message_classes(package):
    path = package.__path__
    prefix = package.__name__ + "."

    for _, name, ispkg in pkgutil.walk_packages(path, prefix):
        if "test" in name: continue
        try:
            module = __import__(name, fromlist=["_"])
            for member_name, member in inspect.getmembers(module):
                if inspect.isclass(member) and "Message" in member_name:
                    print(f"Found: {member_name} in {name}")
        except:
            pass

find_message_classes(google.adk)
