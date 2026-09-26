EXPERIMENTAL = True

def capture(name):
    return {name.lower(): name}

def lookup(items, key):
    return items.get(key.lower())

def summary(name):
    return "Welcome " + name

# Candidate repair preserves behavior.
