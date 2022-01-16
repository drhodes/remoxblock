import json
import math
from collections import namedtuple

from mako.template import Template
from remoxblock import util
import pkg_resources

Row = namedtuple("Row", ['key', 'val', 'is_right_answer'])

class AnswerSet():
    def __init__(self, json_blob):
        normalized_json = json_blob.replace("'", '"')
        self.answers = json.loads(normalized_json)
        
    def render(self, staff_set):
        template_html = util.resource_string("static/html/answers.html")
        rows = []
        
        for key, val in self.keyvals():
            ans = self.shares_val(staff_set, key)
            rows.append(Row(key, val, ans))
            
        return Template(template_html).render(rows=rows)

    def size(self):
        return len(self.answers)

    def keyvals(self):
        return self.answers.items()
    
    def num_shared_values(self, other_set):
        '''tally the number of shared values for every given key'''

        total = 0
        for key in self.answers:
            if self.shares_val(other_set, key): #math.isclose(self.val(key), other_set.val(key)):
                total += 1
        return total

    def shares_val(self, other_set: 'AnswerSet', key: str):
        '''
        Predicate: Does self.answers and other_set.answer share the same
        value associated with key?

        Arguments

        key: a string associated with a values
        '''

        # TODO: what should happen if key is not in one set or the other?
        # 
        return math.isclose(self.val(key), other_set.val(key))

    def val(self, key: str):
        return self.answers[key]
