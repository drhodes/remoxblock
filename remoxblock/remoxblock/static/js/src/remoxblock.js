/* Javascript for RemoXBlock. */
function RemoXBlock(runtime, element) {
    function log(msg) { console.log("remox: " + msg); }
    
    function waitCursor() { document.body.style.cursor = 'wait'; }
    function unwaitCursor() { document.body.style.cursor = 'default'; }
    
    function renderAnswers(html) { $('#user-lab-data', element).html(html); }
    function renderScore(score) {
        var txt = `${score} points (graded)`;
        $('#remoxblock-score', element).text(txt);
    }
    function renderError(msg) {
        var errmsg = `Please forward this error to the community TA on the forum: ${msg}`;
        $('#remoxblock-error', element).text(errmsg);
    }
    function clearError() { $('#remoxblock-error', element).text(""); }
    
    function updateData(result) {
        log(["updating data", result]);
        if (result.ok) {
            renderAnswers(result.html);
            renderScore(result.score);
            clearError();
        } else {
            renderError(result.error);
            log(result.error);
        }
        unwaitCursor();
    }
    
    var handlerLoadHubData = runtime.handlerUrl(element, 'load_hub_data');
    $('#load-hub-data', element).click(function(eventObject) {
        log("loading student answers");
        waitCursor();
        
        $.ajax({
            type: "POST",
            url: handlerLoadHubData,
            data: JSON.stringify({}),
            success: updateData,
            error: function(XMLHttpRequest, textStatus, errorThrown) { 
                unwaitCursor();
                renderError(`Status: ${textStatus}, Error: ${errorThrown}`);
                log(`Status: ${textStatus}, Error: ${errorThrown}`);
            }});
    });
    
    $(function ($) {
        /* Here's where you'd do things on page load. */
    });
}
