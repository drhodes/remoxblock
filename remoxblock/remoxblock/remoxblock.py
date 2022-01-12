"""
This xblock is for fetching remote student answers grading them
locally at edx.
"""

from collections import namedtuple
import hashlib
import json
import logging
import math
import pkg_resources
import requests

from django.http import HttpResponse
from mako.template import Template
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Float, Boolean, String, Scope
from xblock.scorable import ScorableXBlockMixin, Score
from xblockutils.studio_editable import StudioEditableXBlockMixin

import remoxblock.util as util

log = logging.getLogger(__name__)

# https://openedx.atlassian.net/wiki/spaces/AC/pages/161400730/Open+edX+Runtime+XBlock+API
# https://github.com/openedx/xblock-utils

@XBlock.needs('settings')
@XBlock.wants('user')
@XBlock.needs("i18n")
class RemoXBlock(XBlock, StudioEditableXBlockMixin, ScorableXBlockMixin):
    """
    Grade Remote Json
    """
    learner_score = Float(scope=Scope.user_state)

    # configuration fields -------------------------------------------------------
    
    consumer = String(display_name="Consumer Id", help="consumer id",
                      default="", scope=Scope.settings)
    
    secret = String(display_name="Secret Key",
                    help="secret key",
                    default="", scope=Scope.settings)
    
    host = String(display_name="FileServer Host",
                  help="The hostname of the json file server",
                  default="", scope=Scope.settings)

    answer_path = String(display_name="Answer Path",
                         help="name-of-git-repo/path/to/notebook-name.json",
                         default="",
                         scope=Scope.settings)

    staff_answers = String(display_name="Staff Answers",
                           help="paste json blob here, todo: better documentation needed",
                           default="", scope=Scope.settings)
    
    editable_fields = ('display_name',
                       'host',
                       'answer_path',
                       'consumer',
                       'secret',
                       'staff_answers')
    

    def student_view(self, context=None):
        """
        The primary view of the RemoXBlock, shown to students
        when viewing courses.
        """
        # TODO, if a learner_score is when this method is called then
        # render those.

        # TODO, if this is a rescore then also include the previous
        # answers

        # also store the previous set of answer from the lab.
        
        html = self.resource_string("static/html/remoxblock.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/remoxblock.css"))
        frag.add_javascript(self.resource_string("static/js/src/remoxblock.js"))
        frag.initialize_js('RemoXBlock')
        return frag    

    def parsed_staff_answers(self):
        # TODO consider building magic for staff to emit properly json        
        normalized_json = self.staff_answers.replace("'", '"')
        return json.loads(normalized_json)
        
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

    def render_answers(self, answers):
        template_html = self.resource_string("static/html/answers.html")
        Row = namedtuple("Row", ['key', 'val', 'is_right_answer'])

        rows = []
        for key, val in answers:
            ans = "right" if self.check_answer(key, val) else "wrong"
            rows.append(Row(key, val, ans))
            
        return Template(template_html).render(rows=rows)
    
    def text_score(self, answer_pairs):
        num_right = 0        
        for (key, val) in answer_pairs:
            if self.check_answer(key, val):
                num_right += 1

        # TODO use a template for this.
        return f"score {num_right}/{len(answer_pairs)}"

    def check_staff_answers_not_empty(self):
        pass
    
    @XBlock.json_handler
    def load_hub_data(self, data, suffix=''):
        anon_id = util.generate_jupyterhub_userid(self.runtime.anonymous_student_id)
        url = self.host
        
        sess = requests.Session()
        req = requests.Request(
            url=url,
            method="POST",
            data={
                "userid": anon_id,
                "answerpath": self.answer_path,
            },
            auth=(self.consumer, self.secret)
        )
        
        try:
            # rsp should contain the answers from .json file.
            # by comparing the key/vals between self.answers and rsp.results
            rsp = sess.send(req.prepare())

            # TODO more error handling with better messages.
            answer_pairs = json.loads(rsp.text).items()

            html = self.render_answers(answer_pairs)
            score = self.text_score(answer_pairs)

            #TODO replace the hard coded 1 here with something real.
            self.set_score(Score(1, self.max_raw_score()))
            self.rescore(False)
            
            return {
                "ok": True,
                "result": rsp.text,
                "user_id": anon_id,
                "score": score,
                "html":html,
            }
        except Exception as err:
            # maybe it makes sense to drill down further into the
            # exception, but .. users will be reporting this error
            
            msg = "Having trouble grading: " + str(err)
            log.error(msg)            
            return { "ok": False, "error": msg}

        
    def max_raw_score(self):
        # this could return zero, which could lead to div by zero.
        return len(self.parsed_staff_answers())

    # ------------------------------------------------------------------
    # implementing ScorableXBlockMixin
    
    def has_submitted_answer(self):
        return self.learner_score != None
    
    def get_score(self):
        if self.learner_score:
            return Score(self.learner_score, self.max_raw_score())
        else:
            return Score(0, self.max_raw_score())
    
    def set_score(self, score):
        #Score = namedtuple('Score', ['raw_earned', 'raw_possible'])
        self.learner_score = score.raw_earned
        self.save()
        
    def calculate_score(self):
        return Score(self.learner_score, self.max_raw_score())

    ## end of ScorableXBlockMixin

    
    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")
