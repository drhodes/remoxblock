"""
This xblock is for fetching remote student answers and grading
them locally at edx.
"""

import hashlib
import json
import logging
import math
import pkg_resources
import requests
import traceback

from django.http import HttpResponse
from mako.template import Template
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Float, Boolean, String, Scope
from xblock.scorable import ScorableXBlockMixin, Score
from xblockutils.studio_editable import StudioEditableXBlockMixin

from . import util
from . import answer_set.AnswerSet

log = logging.getLogger(__name__)
_ = lambda t: t

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
    # persist student answers so they can be reloaded on page view.
    student_answers = String(display_name="Student Answers", default="", scope=Scope.user_state)
    
    weight = Float(
        display_name="Problem Weight",
        help=_(
            "Enter the number of points possible for this component.  "
            "The default value is 1.0.  "
        ),
        default=1.0,
        scope=Scope.settings,
        values={"min": 0},
    )

    # the following should not be necessary since it is a field of
    # ScorableXBlockMixin
    has_score = True
    
    # configuration fields -------------------------------------------------------
   
    notebook_name = String(display_name="Notebook Name",
                           help="The name of the jupyter notebook: filename.ipynb, please include the file extension .ipynb",
                           default="",
                           scope=Scope.settings)
    
    answer_server = String(display_name="Answer Server",
                  help="The hostname (www.example.com) of the json file server",
                  default="", scope=Scope.settings)
    
    ans_username = String(display_name="Answer Server username", help="the username for the answer server",
                          default="", scope=Scope.settings)
    
    ans_password = String(display_name="Answer Server password", help="the password for the answer server",
                          default="", scope=Scope.settings)
    
    # TODO is there a way to sanitize this input?
    # need to get this working.
    staff_answers = String(display_name="Answers",
                           help="paste json blob here, todo: better documentation needed",
                           default="{}", scope=Scope.settings)
    
    editable_fields = ('display_name',
                       'notebook_name',
                       'answer_server',
                       'ans_username',
                       'ans_password',
                       'staff_answers')

    def student_view(self, context=None):
        html_answers = self.render_answers()
        template_html = self.resource_string("static/html/revisit-remoxblock.html")
        
        frag = Fragment(Template(template_html).render(answers=html_answers, ctx=self))
        frag.add_css(self.resource_string("static/css/remoxblock.css"))
        frag.add_javascript(self.resource_string("static/js/src/remoxblock.js"))
        frag.initialize_js('RemoXBlock')
        return frag

    def parsed_staff_answers(self):
        # TODO If the json doesn't parse here then it most probably means
        # that @staff entered bunk json in the studio xblock config
        # modal, or that it's empty.  staff_answers should not be
        # empty!
        
        # maybe the author_edit_view method could be used to show the
        # validating studio config values
        try:
            return json.loads(self.staff_answers)
        except: pass
        
        trace = traceback.format_exc()
        log.error(trace)
        return {}

    def render_answers(self):
        '''construct HTML that displays answers in that conform to edx's style
        '''
        student_set = AnswerSet(self.student_answers)
        staff_set = AnswerSet(self.staff_answers)
        return staff_set.render(student_set)

    # TODO remove this method.
    def num_right(self):
        student_set = AnswerSet(self.student_answers)
        staff_set = AnswerSet(self.staff_answers)
        return student_set.num_shared_values(staff_set)
    
    def text_score(self):
        numer = self.num_right()
        denom = self.max_raw_score()
        return f"{numer}/{denom}"

    @XBlock.json_handler    
    def load_hub_data(self, data, suffix=''):
        # TODO DeprecationWarning: runtime.anonymous_student_id is
        # deprecated. Please use the user service instead.

        # XBlock.json handler
        anon_id = util.generate_jupyterhub_userid(self.runtime.anonymous_student_id)
        url = self.answer_server
        
        sess = requests.Session()
        req = requests.Request(
            url=url,
            method="POST",
            data={
                "edx-anon-id": anon_id,
                "labname": self.notebook_name,
            },
            auth=(self.ans_username, self.ans_password)
        )
        
        try:
            rsp = sess.send(req.prepare())

            # check for a wrong answer password
            if rsp.status_code == 401:
                return {"ok":False, "error":"Staff username/password for answer server is incorrect"}
            
            log.error(str(rsp))
            
            # payload contain the answers from jupyter notebook
            # answer.json file generated by the student
            # key/vals between self.answers and
            payload = json.loads(rsp.text)
                

            if "error" in payload:
                return { "ok": False, "error": payload["error"] }
            answer_pairs = payload.items()

            # persist the student answers so if the student revisits
            # this xblock view then they will see what answers were
            # previously submitted.
            self.student_answers = rsp.text
            self.save() 

            html = self.render_answers()
            score = self.text_score()
            raw_score = self.num_right() #answer_pairs)
                        
            self.set_score(Score(raw_score, self.max_raw_score()))
            if self.has_submitted_answer():
                self.rescore(False) # is this necessary?
            
            return {
                "ok": True,
                "result": rsp.text,
                "user_id": anon_id,
                "score": score,
                "learner_score": self.learner_score,
                "html":html,
            }
        
        except Exception as err:
            # maybe it makes sense to drill down further into the
            # exception, but .. users will be reporting this error
            
            msg = f"Having trouble grading: {str(err)}"
            # log.error(msg)
            # raise(err)
            return { "ok": False, "error": msg}
        
    def max_grade(self):
        return len(self.parsed_staff_answers())

    def max_score(self):
        return self.weight
    
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
        self.learner_score = score.raw_earned
        self.save()
        
    def calculate_score(self):
        return Score(self.learner_score, self.max_raw_score())

    def publish_grade(self):
        self._publish_grade(self.calculate_score())
    
    ## end of ScorableXBlockMixin

    # this doesn't need to be a method!
    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # ----------------------------------------------------------------------------------------
    # https://openedx.atlassian.net/wiki/spaces/AC/pages/161400730/Open+edX+Runtime+XBlock+API

    # def author_edit_view(self): pass
    # def author_preview_view(self): pass

    # Used in GradesTransformer among other places.
    # def has_submitted_answer(self):
    #     '''Returns True if the problem has been answered by the runtime user.'''
    #     pass
    
