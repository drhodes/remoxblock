"""
This xblock is for fetching remote student answers grading them
locally at edx.
"""

import pkg_resources
import requests
import logging
import hashlib
import json
from collections import namedtuple

from xblock.core import XBlock
from xblock.fields import Integer, Boolean, String, Scope
from web_fragments.fragment import Fragment
from mako.template import Template
from django.http import HttpResponse
from xblockutils.studio_editable import StudioEditableXBlockMixin
from xblock.scorable import ScorableXBlockMixin, Score

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
    
    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the RemoXBlock, shown to students
        when viewing courses.
        """
        html = self.resource_string("static/html/remoxblock.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/remoxblock.css"))
        frag.add_javascript(self.resource_string("static/js/src/remoxblock.js"))
        frag.initialize_js('RemoXBlock')
        return frag    
    
    def max_score(self): return 1        

    def do_grade(self, answers):
        # stub code, just getting something working.
        max_grade = 1
        got_grade = .5
        #self.set_score(got_grade)
        self.runtime.publish(self, "grade", {
            "value": got_grade,
            "max_value": max_grade,
        })

    def check_answer(self, lab_variable_name, lab_variable_value):
        """
        Arguments 

        - lab_variable_name (string): identifies which value is being
          graded. The field: staff_answers (json map) should
          have a matching key.
        
        - lab_variable_value (any): is the value which is being
          graded. The field: self.staff_answers contains this value
          keyed by lab_variable_name.
        
        
        Returns 

        - bool: True if lab_variable_value matches what staff has
        specified as the correct answer in staff_answers.
        """
        
        # TODO: work tolerance into this
        # TODO, this may throw an exception, need to handle it.
        
        student_answer = lab_variable_value

        # TODO consider building magic for staff to emit properly json
        normalized_json = self.staff_answers.replace("'", '"')
        
        staff_answers = json.loads(normalized_json)
        staff_answer = staff_answers[lab_variable_name]
        
        # TODO, this needs to be more robust, probably using parts of
        # an already establish grader
        return student_answer == staff_answer

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
            # self.do_grade("todo: json.loads that rsp.text")
            # self._publish_grade(Score(.7, 1))

            answer_pairs = json.loads(rsp.text).items()
            # log.error(answer_pairs)

            html = self.render_answers(answer_pairs)
            score = self.text_score(answer_pairs)

            return {
                "ok": True,
                "result": rsp.text,
                "user_id": anon_id,
                "score": score,
                "html":html,
            }
        except Exception as err:
            # maybe it makes sense to drill down further into the
            # exception, but .. users will be reporting this error, if
            # it happens, maybe .. a remote log server would be
            # useful?
            msg = "Having trouble grading: " + str(err)
            log.error(msg)            
            return { "ok": False, "error": msg}
            
    # ------------------------------------------------------------------
    # implementing ScoreableXBlockMixin, no idea what state is needed
    # nor where.

    # interface ScorableXBlockMixin
    #     get_score(self)
    #     set_score(self, score)
    #     calculate_score(self, score)
    #     get_score(self)
    
    def has_submitted_answer(self):
        # ? how to determine this?
        return True
    
    def get_score(self):
        # just a stub for now.
        return Score(raw_earned=.5, raw_possible=1)
    
    def set_score(self, score):
        # no idea how this is supposed to be implemented
        pass
    
    def calculate_score(self, score):
        # no idea how this is supposed to be implemented
        return Score(raw_earned=.5, raw_possible=1)

    ## end of ScorableXBlockMixin
