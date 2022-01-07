"""
This xblock is for fetching remote student answers and grading
them and grading them locally at edx
"""

import pkg_resources

from xblock.core import XBlock
from xblock.fields import Integer, Boolean, String, Scope
from web_fragments.fragment import Fragment
from django.http import HttpResponse
import requests

#https://github.com/openedx/xblock-utils
from xblockutils.studio_editable import StudioEditableXBlockMixin

@XBlock.wants('user')
@XBlock.needs("i18n")
class RemoXBlock(StudioEditableXBlockMixin, XBlock):
    """
    Grade Remote Json
    """
    # # Fields are defined on the class.  You can access them in your code as
    # # self.<fieldname>.

    # # store the number of times users up-vote the XBlock. The value
    # # applies to the XBlock and all users collectively.
    upvotes = Integer(help="number of upvotes", default=0, scope=Scope.user_state_summary)

    # # store the number of times users down-vote the XBlock. The value
    # # applies to the XBlock and all users collectively.
    downvotes = Integer(help="number of downvotes", default=0, scope=Scope.user_state_summary)

    # # to record whether or not the user has voted. The value applies
    # # to the XBlock and each user individually.
    voted = Boolean(help="has the user voted yet?", default=False, scope=Scope.user_state)

    # The above fields need to be removed.
    #################
    
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
    
    @XBlock.json_handler
    def load_hub_data(self, data, suffix=''):       
        # "{'q1': 2, 'q2': 4}"
        
        user_service = self.runtime.service(self, 'user')
        xb_user = user_service.get_current_user()
        user_id = xb_user.opt_attrs['edx-platform.user_id']
        
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

        #!! TODO remove this like, it is overwriting user_id for testing purposes 🐬
        # user_id from edx will be different.
        user_id = "35dd7e9124c8847ec5-030ef"

        
        return {"result": rsp.text, "user_id": user_id}
    
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



