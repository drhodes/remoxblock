from remoxblock.answer_set import AnswerSet

student_json = '{"q1": 2, "q2": 4}'
staff_json = '{"q1": 2, "q2": 4}'


def test_init():
    student_set = AnswerSet(student_json)
    staff_set = AnswerSet(staff_json)

    
    
