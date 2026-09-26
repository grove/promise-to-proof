EXPERIMENTAL = True

def capture(name):
    return {name.lower(): name}

def lookup(items, key):
    return items.get(key.lower())

def summary(name):
    return "Welcome " + name

def greet(name):
    return summary(lookup(capture(name), name))
