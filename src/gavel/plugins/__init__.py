try:
    from importlib.metadata import entry_points
except ImportError:
    # Python < 3.8
    from importlib_metadata import entry_points

# Load all gavel plugins
for entry_point in entry_points(group="gavel.plugins"):
    entry_point.load()
