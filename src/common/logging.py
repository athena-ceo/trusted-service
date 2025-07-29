def print_red(*objects, sep=' ', end='\n', file=None, flush=False):
    red = '\033[31m'
    reset = '\033[0m'
    text = sep.join(str(obj) for obj in objects)
    print(f"{red}{text}{reset}", end=end, file=file, flush=flush)
