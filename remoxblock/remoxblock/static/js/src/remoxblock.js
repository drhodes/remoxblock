/* Javascript for RemoXBlock. */
function RemoXBlock(runtime, element) {
    // const progress = new Progress();
    
    function updateCount(result) {
        $('.count', element).text(result.count);
    }

    var handlerUrl = runtime.handlerUrl(element, 'increment_count');
    
    function updateData(result) {
        console.log(["updating data", result]);
        $('#user-lab-data', element).text(result.result);
        $('#user-id', element).text(result.user_id);
        $('#location', element).text(">" + result.location);
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


    // ------------------------------------------------------------------
    // ux
    // make a progress evident, 
    // class Progress {
    //     constructor() {
    //         this.clocks = ["🕐", "🕑", "🕒", "🕓", "🕔", "🕕",
    //                        "🕖", "🕗", "🕘", "🕙", "🕚", "🕛"];
    //         this.clk_idx = 0;
    //         this.waiting = true;            
    //     }

    //     start_timer() {
    //         let update = _ => {
    //             if (this.waiting) {
    //                 this.update_display();
    //                 this.next_clock();
    //                 setTimeout(update, 100);
    //             }
    //         };
    
    //     }

    //     next_clock() {
    //         this.clk_idx = (this.clk_idx + 1) % this.clocks.length;
    //     }
    
    //     update_display() {
    //         if (this.is_waiting()) {
    //             let c = this.clocks[this.clk_idx];            
    //             $('#user-lab-data', element).text(c);
    //             $('#user-id', element).text(c);
    //             $('#location', element).text(c);
    //         }
    //     }

    //     set_waiting() { this.waiting = true; }
    //     set_not_waiting() { this.waiting = false; }
    //     is_waiting() { return this.waiting; }


    // }
}
