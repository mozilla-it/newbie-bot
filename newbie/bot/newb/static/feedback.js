(function (global, $, undefined) {
    var downloadButton = document.getElementById('downloadbutton');
    downloadButton.addEventListener('click', () => {
        downloadFeedback();
    });

    function downloadFile(fileName, urlData){
        var aLink = document.createElement('a');
        var evt = document.createEvent("HTMLEvents");
        evt.initEvent("click");
        aLink.download = fileName;
        aLink.href = urlData ;
        aLink.dispatchEvent(evt);
    }

    function downloadFeedback(){
        $.ajax({
            url: "/downloadfeedback",
            type: "get",
            success: function(response){
                let csvContent = "data:text/csv;charset=utf-8," + response;
                var encodedUri = encodeURI(csvContent);
                var link = document.createElement("a");
                link.setAttribute("href", encodedUri);
                link.setAttribute("download", "user_feedback.csv");
                document.body.appendChild(link); // Required for FF
                link.click(); // This will download the data file named "user_feedback.csv".
            }
        })
    }
}(window, jQuery));