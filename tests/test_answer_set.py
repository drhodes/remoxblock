import pytest

from remoxblock.answer_set import AnswerSet

student_json = '{"q1": 2, "q2": 4}'
staff_json = '{"q1": 2, "q2": 4}'

student_set = AnswerSet(student_json)
staff_set = AnswerSet(staff_json)

def test_size():
    assert student_set.size() == 2
    
def test_share_key_val():
    assert staff_set.shares_val(student_set, "q1")
    assert staff_set.shares_val(student_set, "q2")

def test_keyvals():
    assert (list(sorted(staff_set.keyvals()))) == [("q1", 2), ("q2", 4)]

def test_num_shared_values():
    assert staff_set.num_shared_values(student_set) == 2

def test_shares_val():
    student_set.shares_val(staff_set, "q1")

def test_val():
    assert student_set.val("q1") == 2
