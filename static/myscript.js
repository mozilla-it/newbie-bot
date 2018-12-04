
Date.prototype.toDateInputValue = (function() {
    var local = new Date(this);
    local.setMinutes(this.getMinutes() - this.getTimezoneOffset());
    return local.toJSON().slice(0,10);
});
document.getElementById('send_date').value = new Date().toDateInputValue();

(function (global, $, undefined) {
    var tagitems = '';
    $(function (){
        $('#add_tag').bind('click', function () {
            $('<li name="tag_item" class="list-group-item tags">' + $('input[name="tag_val"]').val() + '</li>').appendTo($("#tag_list"));
            tagitems = tagitems + $('input[name="tag_val"]').val() + '|';
            console.log('tagitems ', tagitems);
            $('#tagitems').val(tagitems);
            $('input[name="tag_val"]').val('');
            $( "li.tags" ).each(function( index ) {
              console.log( index + ": " + $( this ).text() );
            });
            console.log('tagitems val ', $('#tagitems').val());
        });

    });
}(window, jQuery));
