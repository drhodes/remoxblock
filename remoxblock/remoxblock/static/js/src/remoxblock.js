/* Javascript for RemoXBlock. */
function RemoXBlock(runtime, element) {
    // const progress = new Progress();

    var handlerUrl = runtime.handlerUrl(element, 'increment_count');

    function renderAnswers(html) {
        $('#user-lab-data', element).html(html);
    }

    function renderError(result) {
        $('#remoxblock-error', element).text(result);
    }
    
    function renderScore(score) {
        $('#remoxblock-score', element).text(score);
    }
    
    function updateData(result) {
        console.log(["updating data", result]);
        // $('#user-id', element).text(result.user_id);        
        if (result.ok) {
            renderAnswers(result.html);
            renderScore(result.score);
        } else {
            renderError(result);
        }
        unwaitCursor();
    }

    function waitCursor() { document.body.style.cursor = 'wait'; }
    function unwaitCursor() { document.body.style.cursor = 'default'; }
    
    var handlerLoadHubData = runtime.handlerUrl(element, 'load_hub_data');
    $('#load-hub-data', element).click(function(eventObject) {
        console.log("running LTI request");
        waitCursor();
        
        $.ajax({
            type: "POST",
            url: handlerLoadHubData,
            data: JSON.stringify({"hello": "world"}),
            success: updateData,
            error: function(XMLHttpRequest, textStatus, errorThrown) { 
                unwaitCursor();
                alert("Status: " + textStatus);
                alert("Error: " + errorThrown);
            }});
    });
    
    
    $(function ($) {
        /* Here's where you'd do things on page load. */
    });
}
