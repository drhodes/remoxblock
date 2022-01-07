/* Javascript for RemoXBlock. */
function RemoXBlock(runtime, element) {

    function updateCount(result) {
        $('.count', element).text(result.count);
    }

    var handlerUrl = runtime.handlerUrl(element, 'increment_count');
    
    function updateData(result) {
        console.log(["updating data", result]);
        $('#user-lab-data', element).text(result.result);
        $('#user-id', element).text(result.user_id);
    }
    
    var handlerLoadHubData = runtime.handlerUrl(element, 'load_hub_data');
    $('#load-hub-data', element).click(function(eventObject) {
        console.log("running LTI request");
        
        $.ajax({
            type: "POST",
            url: handlerLoadHubData,
            data: JSON.stringify({"hello": "world"}),
            success: updateData,
            error: function(XMLHttpRequest, textStatus, errorThrown) { 
                alert("Status: " + textStatus);
                alert("Error: " + errorThrown);
            }});
    });
    
    
    $(function ($) {
        /* Here's where you'd do things on page load. */
    });
}
