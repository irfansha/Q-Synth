from typing import Callable, Sequence, Type, ParamSpec, Generic


class PDDLType:
    def __init__(self, name: str):
        self.name = name
        self.type_name = self.__class__.__name__

    def __str__(self) -> str:
        return self.name


class object_(PDDLType):
    def type_str(self) -> str:
        return "object"


class PDDLPredicateInstance:
    def __init__(self, name: str, args: list[str]):
        self.name = name
        self.args = args

    def __str__(self) -> str:
        return f"({self.name} {' '.join(self.args)})"


P = ParamSpec("P")


class _PDDLPredicate(Generic[P]):
    def __init__(self, function: Callable[P, None], name: str | None):
        self.function = function
        self.predicate_name = function.__name__ if name is None else name
        self.args = {
            name: class_.__name__ for name, class_ in function.__annotations__.items()
        }

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> PDDLPredicateInstance:
        argstrs = [str(arg) for arg in args]
        return PDDLPredicateInstance(self.predicate_name, argstrs)

    def __str__(self) -> str:
        args_grouped_by_type: dict[str, list[str]] = {}
        for arg, type_ in self.args.items():
            if type_ not in args_grouped_by_type:
                args_grouped_by_type[type_] = []
            args_grouped_by_type[type_].append(f"?{arg}")

        arg_strings = [
            " ".join(args) + " - " + type_
            for type_, args in args_grouped_by_type.items()
        ]

        return f"({self.predicate_name} {' '.join(arg_strings)})"


def PDDLPredicate(
    name: str | None = None,
):
    def decorator(function: Callable[P, None]):
        return _PDDLPredicate(function, name)

    return decorator


@PDDLPredicate(name="not")
def not_(predicate: PDDLPredicateInstance):
    pass


class PDDLIncreaseCostFunctionPredicateInstance(PDDLPredicateInstance):
    def __init__(self, amount: int):
        self.amount = amount

    def __str__(self) -> str:
        return f"(increase (total-cost) {self.amount})"


def increase_cost(amount: int) -> PDDLIncreaseCostFunctionPredicateInstance:
    return PDDLIncreaseCostFunctionPredicateInstance(amount)


class PDDLConditionalPredicateInstance(PDDLPredicateInstance):
    def __init__(
        self,
        conditions: list[PDDLPredicateInstance],
        effects: list[PDDLPredicateInstance],
    ):
        self.conditions = conditions
        self.effects = effects

    def __str__(self) -> str:
        return f"(when (and {' '.join(map(str, self.conditions))}) (and {' '.join(map(str, self.effects))}))"


def when(
    conditions: list[PDDLPredicateInstance], effects: list[PDDLPredicateInstance]
) -> PDDLConditionalPredicateInstance:
    return PDDLConditionalPredicateInstance(conditions, effects)


class PDDLForallPredicateInstance(PDDLPredicateInstance, Generic[P]):
    def __init__(
        self,
        function: Callable[P, Sequence[PDDLPredicateInstance]],
    ):
        self.function = function
        annotations = function.__annotations__
        self.args = {name: class_.__name__ for name, class_ in annotations.items()}

        self.predicates = self.function(
            *[type_(f"?{arg}") for arg, type_ in annotations.items()]
        )  # type: ignore

    def __str__(self) -> str:
        args_grouped_by_type: dict[str, list[str]] = {}
        for arg, type_ in self.args.items():
            if type_ not in args_grouped_by_type:
                args_grouped_by_type[type_] = []
            args_grouped_by_type[type_].append(f"?{arg}")

        arg_strings = [
            " ".join(args) + " - " + type_
            for type_, args in args_grouped_by_type.items()
        ]

        return f"(forall ({' '.join(arg_strings)}) (and {' '.join(map(str, self.predicates))}))"


def forall(
    function: Callable[P, Sequence[PDDLPredicateInstance]],
) -> PDDLForallPredicateInstance:
    return PDDLForallPredicateInstance(function)


class _PDDLAction:
    def __init__(
        self,
        function: Callable[
            ..., tuple[Sequence[PDDLPredicateInstance], Sequence[PDDLPredicateInstance]]
        ],
        name: str | None,
    ):
        self.function = function
        self.name = function.__name__ if name is None else name
        self.args = {
            name: class_.__name__ for name, class_ in function.__annotations__.items()
        }
        args = self.function.__annotations__

        self.preconditions, self.effects = self.function(
            *[type_(f"?{arg}") for arg, type_ in args.items()]
        )

    def __call__(self, *args):
        return self.function(*args)

    def __str__(self) -> str:
        parameters_grouped_by_type: dict[str, list[str]] = {}
        for arg, type_ in self.args.items():
            if type_ not in parameters_grouped_by_type:
                parameters_grouped_by_type[type_] = []
            parameters_grouped_by_type[type_].append(f"?{arg}")

        parameters_with_type = [
            " ".join(parameters) + " - " + type_
            for type_, parameters in parameters_grouped_by_type.items()
        ]

        parameters = f":parameters ({' '.join(parameters_with_type)})"
        preconditions = f":precondition (and {' '.join(map(str, self.preconditions))})"

        return f"""
    (:action {self.name}
        {parameters}
        {preconditions}
        :effect (and {" ".join(map(str, self.effects))})
    )"""


def PDDLAction(
    name: str | None = None,
):
    def decorator(
        function: Callable[
            ..., tuple[Sequence[PDDLPredicateInstance], Sequence[PDDLPredicateInstance]]
        ],
    ):
        return _PDDLAction(function, name)

    return decorator


def PDDLDurativePredicate(
    type_: str | None = None,
):
    def decorator(function: Callable[[PDDLPredicateInstance], None]):
        return _PDDLDurativePredicate(function, type_)

    return decorator


class PDDLDurativePredicateInstance:
    def __init__(self, type_: str, predicate: PDDLPredicateInstance):
        self.type_ = type_
        self.predicate = predicate

    def __str__(self) -> str:
        return f"({self.type_} {self.predicate})"


class _PDDLDurativePredicate:
    def __init__(
        self, function: Callable[[PDDLPredicateInstance], None], type_: str | None
    ):
        self.function = function
        self.type_ = function.__name__ if type_ is None else type_

    def __call__(
        self, predicate: PDDLPredicateInstance
    ) -> PDDLDurativePredicateInstance:
        return PDDLDurativePredicateInstance(self.type_, predicate)


@PDDLDurativePredicate(type_="at start")
def at_start(predicate: PDDLPredicateInstance):
    pass


@PDDLDurativePredicate(type_="at end")
def at_end(predicate: PDDLPredicateInstance):
    pass


@PDDLDurativePredicate(type_="over all")
def over_all(predicate: PDDLPredicateInstance):
    pass


class _PDDLDurativeAction:
    def __init__(
        self,
        function: Callable[
            ...,
            tuple[
                int,
                Sequence[PDDLDurativePredicateInstance],
                Sequence[PDDLDurativePredicateInstance],
            ],
        ],
        name: str | None,
    ):
        self.function = function
        self.name = function.__name__ if name is None else name
        self.args = {
            name: class_.__name__ for name, class_ in function.__annotations__.items()
        }
        args = self.function.__annotations__

        self.duration, self.conditions, self.effects = self.function(
            *[type_(f"?{arg}") for arg, type_ in args.items()]
        )

    def __call__(self, *args):
        return self.function(*args)

    def __str__(self) -> str:
        parameters_grouped_by_type: dict[str, list[str]] = {}
        for arg, type_ in self.args.items():
            if type_ not in parameters_grouped_by_type:
                parameters_grouped_by_type[type_] = []
            parameters_grouped_by_type[type_].append(f"?{arg}")

        parameters_with_type = [
            " ".join(parameters) + " - " + type_
            for type_, parameters in parameters_grouped_by_type.items()
        ]

        parameters = f":parameters ({' '.join(parameters_with_type)})"
        duration = f":duration (= ?duration {self.duration})"
        conditions = f":condition (and {' '.join(map(str, self.conditions))})"
        effects = f":effect (and {' '.join(map(str, self.effects))})"

        return f"""
    (:durative-action {self.name}
        {parameters}
        {duration}
        {conditions}
        {effects}
    )"""


def PDDLDurativeAction(
    name: str | None = None,
):
    def decorator(
        function: Callable[
            ...,
            tuple[
                int,
                Sequence[PDDLDurativePredicateInstance],
                Sequence[PDDLDurativePredicateInstance],
            ],
        ],
    ):
        return _PDDLDurativeAction(function, name)

    return decorator


class PDDLInstance:
    def __init__(
        self,
        objects: list[PDDLType] = [],
        types: list[Type[PDDLType]] = [],
        constants: list[PDDLType] = [],
        predicates: list[_PDDLPredicate] = [],
        initial_state: list[PDDLPredicateInstance] = [],
        goal_state: list[PDDLPredicateInstance] = [],
        actions: list[_PDDLAction] = [],
        durative_actions: list[_PDDLDurativeAction] = [],
        cost_function: bool = False,
        negative_preconditions: bool = True,
        durative_actions_req: bool = False,
    ):
        self.domain = "Quantum"
        self.problem = "circuit"
        self.objects = objects
        self.types = types
        self.constants = constants
        self.predicates = predicates
        self.initial_state = initial_state
        self.goal_state = goal_state
        self.actions = actions
        self.durative_actions = durative_actions
        self.cost_function = cost_function
        self.negative_preconditions = negative_preconditions
        self.durative_actions_req = durative_actions_req

    def compile(self) -> tuple[str, str]:
        object_grouped_by_type: dict[str, list[PDDLType]] = {}
        for obj in self.objects:
            if obj.type_name not in object_grouped_by_type:
                object_grouped_by_type[obj.type_name] = []
            object_grouped_by_type[obj.type_name].append(obj)

        object_strings = [
            " ".join(map(lambda o: o.name, objects)) + " - " + type_
            for type_, objects in object_grouped_by_type.items()
        ]

        init_strings = [
            str(predicate_instance) for predicate_instance in self.initial_state
        ]

        goal_strings = [
            str(predicate_instance) for predicate_instance in self.goal_state
        ]

        metric_string = f"(:metric minimize (total-cost))" if self.cost_function else ""
        metric_string = (
            f"(:metric minimize (total-time))" if self.durative_actions_req else ""
        )

        nl = "\n"
        problem = f"""
(define (problem {self.problem})
    (:domain {self.domain})
    (:objects
        {f'{nl}        '.join(object_strings)}
    )
    (:init
        {f'{nl}        '.join(init_strings)}
        {f'{nl}        (= (total-cost) 0)' if self.cost_function else ''}
    )
    (:goal
        (and
            {f'{nl}            '.join(goal_strings)}
        )
    )
    {metric_string}
)
"""
        types_grouped_by_super_type: dict[str, list[Type[PDDLType]]] = {}
        for type_ in self.types:
            if type_.__base__ is None:
                raise ValueError("Type must have a base class.")
            super_class = (
                type_.__base__.__name__
                if type_.__base__.__name__ != "object_"
                else "object"
            )
            if super_class not in types_grouped_by_super_type:
                types_grouped_by_super_type[super_class] = []
            types_grouped_by_super_type[super_class].append(type_)

        type_strings = [
            " ".join(map(lambda t: t.__name__, types)) + " - " + super_type
            for super_type, types in types_grouped_by_super_type.items()
        ]

        constants_grouped_by_type: dict[str, list[PDDLType]] = {}
        for constant in self.constants:
            if constant.type_name not in constants_grouped_by_type:
                constants_grouped_by_type[constant.type_name] = []
            constants_grouped_by_type[constant.type_name].append(constant)

        constant_strings = [
            " ".join(map(lambda c: c.name, constants)) + " - " + type_
            for type_, constants in constants_grouped_by_type.items()
        ]

        functions_string = f"(:functions (total-cost))" if self.cost_function else ""

        nl = "\n"
        domain = f"""
(define (domain {self.domain})
    (:requirements :strips :typing {":negative-preconditions" if self.negative_preconditions else ""} {":action-costs" if self.cost_function else ""} {":durative-actions" if self.durative_actions_req else ""})
    (:types
        {f'{nl}        '.join(type_strings)}
    )
    (:constants
        {f'{nl}        '.join(constant_strings)}
    )
    (:predicates
        {f'{nl}        '.join(map(str, self.predicates))}
    )
    {functions_string}
    {f'{nl}    '.join(map(str, self.actions))}
    {f'{nl}    '.join(map(str, self.durative_actions))}
)
"""
        return domain, problem
