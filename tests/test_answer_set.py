import pytest

from remoxblock.answer_set import AnswerSet

student_json = '{"q1": 2, "q2": 4}'
staff_json = '{"q1": 2, "q2": 4}'

student_set = AnswerSet(student_json)
staff_set = AnswerSet(staff_json)

def test_init():
    student_set = AnswerSet(student_json)
    staff_set = AnswerSet(staff_json)
    
def test_size():
    student_set = AnswerSet(student_json)
    assert student_set.size() == 2

    
def test_share_key_val():
    student_set = AnswerSet(student_json)
    staff_set = AnswerSet(staff_json)
    
    assert staff_set.shares_val(student_set, "q1")
    assert staff_set.shares_val(student_set, "q2")
