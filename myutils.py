def myrd(path):
    with open(path, "r") as f:
        for line in f.readlines():
            yield line.rstrip("\r\n")

