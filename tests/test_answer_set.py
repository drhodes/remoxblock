import pytest

from remoxblock.answer_set import AnswerSet, CORRECT, WRONG, UNSUBMITTED


student_json = '{"q1": 2, "q2": 4}'
staff_json = '{"q1": 2, "q2": 4}'

student_set = AnswerSet(student_json)
staff_set = AnswerSet(staff_json)

def test_size():
    assert student_set.size() == 2

def test_empty_json():
    aset = AnswerSet("")
    assert aset.size() == 0

    
def test_match_val():
    assert staff_set.match_val(student_set, "q1") == CORRECT
    assert staff_set.match_val(student_set, "q2") == CORRECT

def test_keyvals():
    assert (list(sorted(staff_set.keyvals()))) == [("q1", 2), ("q2", 4)]

def test_num_shared_values():
    assert staff_set.num_shared_values(student_set) == 2

def test_val():
    assert student_set.val("q1") == 2
