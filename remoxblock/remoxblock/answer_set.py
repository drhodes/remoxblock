import pkg_resources
from collections import namedtuple
from mako.template import Template
import json

class AnswerSet():
    def __init__(self, json_blob):
        self.answers = json.loads(json_blob)
        
    # TODO move this to utils.
    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def render(self, staff_answers):
        template_html = self.resource_string("static/html/answers.html")
        # TODO rename this and move to util.py
        Row = namedtuple("Row", ['key', 'val', 'is_right_answer'])
        rows = []
        
        for key, val in staff_answers.items():
            ans = self.answers[key] = val
            rows.append(Row(key, val, ans))
            
        return Template(template_html).render(rows=rows)
        
    def check_answer(self, lab_variable_name, lab_variable_value):
        """Arguments 

        lab_variable_name (string): 

          student supplied variable name from the lab that identifies
          which value is being graded. The field: self.staff_answers
          (json map) should have a key that matches lab_variable_name.
        
        lab_variable_value (number): 

          is the value which is being graded. The field:
          self.staff_answers contains this value keyed by
          lab_variable_name.
        
        Returns 

          bool: True if lab_variable_value matches what staff has
                specified as the correct answer in staff_answers.
        """
        
        student_answer = lab_variable_value        
        # TODO, this may throw an exception, need to handle it.
        staff_answers = self.parsed_staff_answers()        
        staff_answer = staff_answers[lab_variable_name]
        
        # TODO, this needs to be more robust, probably using parts of
        # an already establish grader
        # TODO: work tolerance into this
        return math.isclose(student_answer, staff_answer)

    def num_right(self, answer_pairs):
        total = 0
        # TODO iterate over staffs_answers here instead.
        for (key, val) in answer_pairs:
            if self.check_answer(key, val):
                total += 1
        return total


    
