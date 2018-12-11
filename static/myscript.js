
Date.prototype.toDateInputValue = (function() {
    var local = new Date(this);
    local.setMinutes(this.getMinutes() - this.getTimezoneOffset());
    return local.toJSON().slice(0,10);
});
document.getElementById('send_date').value = new Date().toDateInputValue();

(function (global, $, undefined) {
    const message_type = document.getElementById('message_type');
    message_type.classList.add('custom-select');
    const country = document.getElementById('country');
    country.classList.add('custom-select');
    const category = document.getElementById('category');
    category.classList.add('custom-select');
    const frequency = document.getElementById('frequency');
    frequency.classList.add('custom-select');
    var tagitems = '';
    var links = [];
    var link = {};
    // Function to retrieve existing tags and links

    $( "li.litags" ).each(function( index ) {
              tagitems = tagitems +   $( this ).text() + '|';
            });
    $('#tagitems').val(tagitems);
    $("li.lilink").each(function(e){
        var datas = $(this)[0].childNodes[1].data.split(' ');
        link = {};
        link['name'] = datas[0];
        link['url'] = datas[1];
        links.push(link);
    });
    $('#linkitems').val(JSON.stringify(links));

    // Function to add tags
    $(function (){
        $('#add_tag').bind('click', function () {
            $('<li name="tag_item" class="list-group-item litags">' +
                '<a style="margin-left: 20px; margin-right: 20px; text-decoration: none;" class="clearitem" ><i class="fas fa-times tags" style="color:red"></i></a>' +
                $('input[name="tag_val"]').val() + '</li>').appendTo($("#tag_list"));
            tagitems = tagitems + $('input[name="tag_val"]').val() + '|';
            $('#tagitems').val(tagitems);
            $('input[name="tag_val"]').val('');
            document.getElementById('add_tag').classList.add('moz-disabled');
        });
    });


    // Function to add link name and url
    $(function(){
        $('#add_link').bind('click', function(){
            $('#linkitems').val('');
            link = {};
            link['name'] = $('input[name="link_name"]').val();
            link['url'] = $('input[name="link_url"]').val();
            links.push(link);
            $('<li name="link_item" class="list-group-item row lilink">' +
            '<a style="margin-right: 20px; text-decoration: none;" class="clearlink"><i class="fas fa-times links" style="color:red"></i></a>' +
            link['name'] + ' | ' + link['url'] + '</li>').appendTo($("#link_list"));
            $('#linkitems').val(JSON.stringify(links));
            $('input[name="link_name"]').val('');
            $('input[name="link_url"]').val('');
            document.getElementById('add_link').classList.add('moz-disabled');
        });
    });
    // Function to remove links and tags
    document.addEventListener('click', function(e){
        e = e || window.event;
        var target = e.target || e.srcElement;
        var classes = target.className.split(' ');
        for (var x = 0; x < classes.length; x++){
            if (classes[x] == 'links'){
                $('#linkitems').val('');
                var liVal = target.parentNode.parentNode.valueOf().innerText.split(' ');
                for (var i = 0; i < links.length; i++){
                    if(links[i]["name"] === liVal[0]){
                        links.splice(i, 1);
                    }
                }
                $('#linkitems').val(JSON.stringify(links));
                target.parentNode.parentNode.parentNode.removeChild(target.parentNode.parentNode);
            }
            if (classes[x] == 'tags'){
                tagitems = '';
                target.parentNode.parentNode.parentNode.removeChild(target.parentNode.parentNode);
                var liVal = target.parentNode.parentNode.valueOf().innerText.split(' | ');
                $( "li.litags" ).each(function( index ) {
                    tagitems = tagitems + $(this).text() + '|';
                });
                $('#tagitems').val(tagitems);
            }
        }
    }, false);

    // Check inputs and enable/disable as appropriate
    document.addEventListener('keyup', (e) => {
        checkInputs();
    }, false);
    function checkInputs() {
        var name = document.getElementById('link_name');
        var link = document.getElementById('link_url');
        var tag = document.getElementById('tag_val');
        if (name.value.length > 0 && link.value.length > 0 && (link.value.startsWith('http://') || link.value.startsWith('https://'))){
            document.getElementById('add_link').classList.remove('moz-disabled');
        } else {
            document.getElementById('add_link').classList.add('moz-disabled');
        }
        if (tag.value.length > 0){
            document.getElementById('add_tag').classList.remove('moz-disabled');
        } else {
            document.getElementById('add_tag').classList.add('moz-disabled');
        }
    };


}(window, jQuery));
// add tool tip to http link
    $(function() {
      $('[data-toggle="tooltip"]').tooltip();
    });

