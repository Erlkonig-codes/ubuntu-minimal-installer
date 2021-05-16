def bool_confirmation(confirmation_question):
    answer = input(confirmation_question)
    bool_data = answer.lower() == 'y'
    return bool_data
