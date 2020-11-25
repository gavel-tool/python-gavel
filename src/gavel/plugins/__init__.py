import pkg_resources

for entry_point in pkg_resources.iter_entry_points("gavel.plugins"):
    entry_point.load()
