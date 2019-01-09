
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
    const loc = document.getElementById('location');
    loc.classList.add('custom-select');
    const emp_type = document.getElementById('emp_type');
    emp_type.classList.add('custom-select');
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
            var tags = $('input[name="tag_val"]').val().split(',');
            for (let x = 0; x < tags.length; x++){
                $('<li name="tag_item" class="list-group-item litags">' +
                '<a style="margin-left: 20px; margin-right: 20px; text-decoration: none;" class="clearitem" ><i class="fas fa-times tags" style="color:red"></i></a>' +
                tags[x] + '</li>').appendTo($("#tag_list"));
            tagitems = tagitems + $('input[name="tag_val"]').val() + '|';
            }

            $('#tagitems').val(tagitems);
            $('input[name="tag_val"]').val('');
            document.getElementById('add_tag').classList.add('moz-disabled');
            checkInputs();
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
            $('<div class="c-message__attachments">' +
            ' <div class="c-message_attachment">' +
            '  <div class="c-message_attachment__border" style="background-color: rgb(0, 137, 82);"></div>' +
            '    <div class="c-message_attachment__body">' +
            '     <div class="c-message_attachment__row c-message_attachment__row--actions">' +
            '       <a role="link" tabindex="0" target="_blank" class="c-button c-button--outline-primary c-button--small c-message_attachment__button null--outline-primary null--small" type="button" data-qa="message_attachment_button_primary" href="'+ link["url"] + '" rel="noopener noreferrer">' +
            '        <span class="overflow_ellipsis" dir="auto"> '+ link["name"] +'</span>' +
            '       </a>\n' +
            '     </div>\n' +
            '    </div>\n' +
            '  </div>\n' +
            ' </div>').appendTo($("#preview_list"));
            $('#linkitems').val(JSON.stringify(links));
            $('input[name="link_name"]').val('');
            $('input[name="link_url"]').val('');
            document.getElementById('add_link').classList.add('moz-disabled');
            checkInputs();
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
            document.getElementById('submit-message').classList.add('moz-disabled');
        } else {
            document.getElementById('add_link').classList.add('moz-disabled');
            document.getElementById('submit-message').classList.remove('moz-disabled')
        }
        if (name.value.length > 0 || link.value.length > 0 || tag.value.length > 0){
            document.getElementById('submit-message').classList.add('moz-disabled');
        } else {
            document.getElementById('submit-message').classList.remove('moz-disabled')
        }
        if (tag.value.length > 0){
            document.getElementById('add_tag').classList.remove('moz-disabled');
        } else {
            document.getElementById('add_tag').classList.add('moz-disabled');
        }
        var textfield = document.getElementById('text');
        document.getElementById('preview-message-body').textContent=textfield.value;

    };




}(window, jQuery));
// add tool tip to http link
    $(function() {
      $('[data-toggle="tooltip"]').tooltip();
    });

var options = {
      valueNames: [ 'team', 'tags', 'owner', 'topic' ]
    };

var userList = new List('users', options);
var date=new Date();
var time=date.toLocaleString('en-US', { hour: 'numeric', minute: 'numeric', hour12: true });
document.getElementById('current_time').innerHTML = time;
var timeels = document.getElementsByClassName('current-time');
for (let x = 0; x < timeels.length; x++){
    timeels[x].innerHTML = time;
}