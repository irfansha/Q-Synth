class Variable:
    """
    Common class for defining variables. Allows easy extraction of name and time step.
    """

    def __init__(self, name: str, params: list, time_step: int):
        self.name = name
        self.params = params
        self.time_step = time_step

    def __eq__(self, other):
        if not isinstance(other, Variable):
            return False
        elif self.name != other.name:
            return False
        elif self.params != other.params:
            return False
        elif self.time_step != other.time_step:
            return False
        else:
            return True

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        param_str = " ".join(map(str, self.params))
        return f"{self.name} {param_str} {self.time_step}"


