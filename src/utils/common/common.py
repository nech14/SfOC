

def print_vars(model):
    for k, v in vars(model).items():
        print(f"{k} = {v}")

def get_vars_str(model) -> str:
    result = ""
    for k, v in vars(model).items():
        result += f"{k} = {v}\n"
    return result