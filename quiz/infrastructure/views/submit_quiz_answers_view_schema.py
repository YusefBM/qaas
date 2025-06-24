from voluptuous import Required, Schema, Coerce, All, Length


answer_submission_schema = Schema(
    {
        Required("question_id"): Coerce(int),
        Required("answer_id"): Coerce(int),
    }
)


submit_quiz_answers_view_schema = Schema(
    {
        Required("answers"): All([answer_submission_schema], Length(min=1)),
    }
)
