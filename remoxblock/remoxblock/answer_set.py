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
        
        # for key, val in staff_answers.items():
        #     ans = self.val(key) == val
        #     rows.append(Row(key, val, ans))
        # rows = []
        for key, val in staff_set.keyvals():
            ans = self.shares_val(staff_set, key)
            rows.append(Row(key, val, ans))
            
            
        return Template(template_html).render(rows=rows)

    def size(self):
        return len(self.answers)

    def keyvals(self):
        return self.answers.items()
    
    def num_shared_values(self, other_set):
        total = 0
        for key in self.answers:
            if self.shares_val(other_set, key): #math.isclose(self.val(key), other_set.val(key)):
                total += 1
        return total

    def shares_val(self, other_set: 'AnswerSet', key: str):
        ''' Arguments

        key: a string that keys into answer dictionary
        '''        
        return math.isclose(self.val(key), other_set.val(key))

    def val(self, key: str):
        return self.answers[key]
