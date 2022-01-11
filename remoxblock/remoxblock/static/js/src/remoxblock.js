/* Javascript for RemoXBlock. */
function RemoXBlock(runtime, element) {
    // const progress = new Progress();

    var handlerUrl = runtime.handlerUrl(element, 'increment_count');

    function waitCursor() { document.body.style.cursor = 'wait'; }
    function unwaitCursor() { document.body.style.cursor = 'default'; }
    
    function renderAnswers(html) { $('#user-lab-data', element).html(html); }
    function renderScore(score) { $('#remoxblock-score', element).text(score); }
    function renderError(result) { $('#remoxblock-error', element).text(result); }
    function clearError() { $('#remoxblock-error', element).text(""); }
    
    function updateData(result) {
        console.log(["updating data", result]);
        if (result.ok) {
            renderAnswers(result.html);
            renderScore(result.score);
            clearError();
        } else {
            renderError(result.error);
        }
        unwaitCursor();
    }
    
    var handlerLoadHubData = runtime.handlerUrl(element, 'load_hub_data');
    $('#load-hub-data', element).click(function(eventObject) {
        console.log("running LTI request");
        waitCursor();
        
        $.ajax({
            type: "POST",
            url: handlerLoadHubData,
            data: JSON.stringify({}),
            success: updateData,
            error: function(XMLHttpRequest, textStatus, errorThrown) { 
                unwaitCursor();
                renderError(`Status: ${textStatus}, Error: ${errorThrown}`);
            }});
    });
    
    $(function ($) {
        /* Here's where you'd do things on page load. */
    });
}
