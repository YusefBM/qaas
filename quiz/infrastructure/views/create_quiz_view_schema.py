from voluptuous import Required, Schema, Coerce, Invalid, All, Length


def not_empty(value: str | None) -> str:
    if value is None or value.strip() == "":
        raise Invalid("Value must not be empty")

    return value


answer_schema = Schema(
    {
        Required("text"): All(str, not_empty),
        Required("is_correct"): bool,
        Required("order"): Coerce(int),
    }
)

question_schema = Schema(
    {
        Required("text"): All(str, not_empty),
        Required("order"): Coerce(int),
        Required("points"): Coerce(int),
        Required("answers"): All([answer_schema], Length(min=1)),
    }
)


create_quiz_view_schema = Schema(
    {
        Required("title"): All(str, not_empty),
        Required("description"): All(str, not_empty),
        Required("questions"): All([question_schema], Length(min=1)),
    }
)
