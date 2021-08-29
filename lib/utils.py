def log_to_file(msg: str, filename: str):
    f = open(filename, 'a')
    f.write(msg+"\n")
    f.close()