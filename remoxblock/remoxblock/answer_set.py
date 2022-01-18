import json
import math
from collections import namedtuple

from mako.template import Template
from remoxblock import util
import pkg_resources

Row = namedtuple("Row", ['key', 'val', 'answer'])

CORRECT='CORRECT'
WRONG='WRONG'
UNSUBMITTED='UNSUBMITTED'

# TODO consider inheriting from collections.UserDict
class AnswerSet():
    def __init__(self, json_blob):
        # TODO find a better way to sanitize the json_blob.
        if json_blob == "":
            self.answers = {}
        else:
            normalized_json = json_blob.replace("'", '"')        
            self.answers = json.loads(normalized_json)
        
    def render(self, student_set: 'AnswerSet'):
        '''
        self is the reference set defined by staff_answers...  it should
        be more obvious that 'self' in this case must be the staff
        AnswerSet.
        '''        
        template_html = util.resource_string("static/html/answers.html")
        rows = []
        
        for key in self.answers:
            result = self.match_val(student_set, key)
            student_val = student_set.val(key)
            rows.append(Row(key, student_val, result))
            
        return Template(template_html).render(rows=rows)

    def size(self):
        return len(self.answers)
    
    def has_key(self, key):
        return key in self.answers
    
    def num_shared_values(self, other_set: 'AnswerSet'):
        '''tally the number of shared values for every given key'''
        total = 0
        for key in self.answers:
            if self.match_val(other_set, key) == CORRECT:
                total += 1
        return total

    def answers_match(self, other_set: 'AnswerSet', key: str):
        return math.isclose(self.val(key), other_set.val(key))
    
    def match_val(self, other_set: 'AnswerSet', key: str):
        '''
        Arguments      

        other_set: the other AnswerSet to match against.
        key: a string associated with a values
        '''
        if self.has_key(key) and other_set.has_key(key):
            if self.answers_match(other_set, key):
                return CORRECT
            else:
                return WRONG
        else:
            return UNSUBMITTED

    def val(self, key: str):
        return self.answers.get(key)
