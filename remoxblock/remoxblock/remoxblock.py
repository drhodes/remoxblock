"""
This xblock is for fetching remote student answers grading them
locally at edx.
"""

import pkg_resources

from xblock.core import XBlock
from xblock.fields import Integer, Boolean, String, Scope
from web_fragments.fragment import Fragment
from django.http import HttpResponse
import requests
import logging

# https://github.com/openedx/xblock-utils
from xblockutils.studio_editable import StudioEditableXBlockMixin
from xblock.scorable import ScorableXBlockMixin

log = logging.getLogger(__name__)

# https://openedx.atlassian.net/wiki/spaces/AC/pages/161400730/Open+edX+Runtime+XBlock+API

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

    answers = String(display_name="Answers",
                     help="paste json blob here, todo: better documentation needed",
                     default="", scope=Scope.settings)
    
    editable_fields = ('display_name', 'host', 'consumer', 'secret', 'answers')
    
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
    
    # TO-DO: change this handler to perform your own actions.  You may need more
    # than one handler, or you may not need any handlers at all.
    @XBlock.json_handler
    def increment_count(self, data, suffix=''):
        """
        An example handler, which increments the data.
        """
        # Just to show data coming in...
        assert data['hello'] == 'world'

        self.count += 1
        return {"count": self.count}

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

    
    @XBlock.json_handler
    def load_hub_data(self, data, suffix=''):        
        log.error("testing error logs!")
        # "{'q1': 2, 'q2': 4}"

        anon_id = self.runtime.anonymous_student_id
        
        url = self.host
        req = requests.Request(url=url,
                               method="POST",
                               data={
                                   "userid":"35dd7e9124c8847ec5-030ef",
                                   "labname":"jupyter-answer-magic/test/test_autograde1.json",
                               },                           
                               auth=(self.consumer, self.secret))
        sess = requests.Session()

        # rsp should contain the answers from the jupyter notebook.
        # grading happens here? by comparing the key/vals between
        # self.answers and rsp.results
        
        # TODO more error handling with better messages.
        
        rsp = sess.send(req.prepare())
        #self.do_grade("todo: json.loads that rsp.result")
        
        #!! TODO remove this, it is overwriting user_id for testing purposes 🐬
        # user_id from edx will be different.
        fake_user_id = "35dd7e9124c8847ec5-030ef"

        return {"result": rsp.text, "user_id": fake_user_id, "location":anon_id}
    
    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("RemoXBlock",
             """<remoxblock/>
             """),
            ("Multiple RemoXBlock",
             """<vertical_demo>
                <remoxblock/>
                <remoxblock/>
                </vertical_demo>
             """),
        ]



