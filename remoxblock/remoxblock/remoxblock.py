"""
This xblock is for fetching remote student answers and grading
them locally at edx.
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
from remoxblock.answer_set import AnswerSet

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

    # TODO is there a way to sanitize this input?
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
        '''
        if student has already submitted answers, then there should be
        answers, so render those
        '''
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
        normalized_json = self.staff_answers.replace("'", '"')
        return json.loads(normalized_json)

    def render_answers(self):
        student_set = AnswerSet(self.student_answers)
        staff_set = AnswerSet(self.staff_answers)
        return staff_set.render(student_set)

    # TODO remove this method.
    def num_right(self, answer_pairs):
        student_set = AnswerSet(self.student_answers)
        staff_set = AnswerSet(self.staff_answers)
        return student_set.num_shared_values(staff_set)
    
    def text_score(self, answer_pairs):
        total = self.num_right(answer_pairs)
        # TODO use a template for this.
        return f"score {total}/{len(answer_pairs)}"


    @XBlock.json_handler    
    def load_hub_data(self, data, suffix=''):
        # TODO DeprecationWarning: runtime.anonymous_student_id is
        # deprecated. Please use the user service instead.
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
            
            self.student_answers = rsp.text
            self.save() # this isn't strictly necessary since set_score does a state save.
            
            html = self.render_answers()
            score = self.text_score(answer_pairs)
            raw_score = self.num_right(answer_pairs)
                        
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
            
            msg = "Having trouble grading: " + str(err)
            log.error(msg)
            raise(err)
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
    
