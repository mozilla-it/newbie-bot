
Date.prototype.toDateInputValue = (function() {
    var local = new Date(this);
    local.setMinutes(this.getMinutes() - this.getTimezoneOffset());
    return local.toJSON().slice(0,10);
});
document.getElementById('send_date').value = new Date().toDateInputValue();

(function (global, $, undefined) {
    const message = document.getElementById('message_type');
    message.classList.add('custom-select');
    const country = document.getElementById('country');
    country.classList.add('custom-select');
    const category = document.getElementById('category');
    category.classList.add('custom-select');
    const frequency = document.getElementById('frequency');
    frequency.classList.add('custom-select');
    var tagitems = '';
    $( "li.tags" ).each(function( index ) {
              tagitems = tagitems +   $( this ).text() + '|';
            });
    console.log('tagitems ', tagitems);
    $(function (){
        $('#add_tag').bind('click', function () {
            $('<li name="tag_item" class="list-group-item tags">' +
                '<a style="margin-left: 20px; margin-right: 20px; text-decoration: none;" class="clearitem"><i class="fas fa-times" style="color:red"></i></a>' +
                $('input[name="tag_val"]').val() + '</li>').appendTo($("#tag_list"));
            tagitems = tagitems + $('input[name="tag_val"]').val() + '|';
            $('#tagitems').val(tagitems);
            $('input[name="tag_val"]').val('');
        });
    });
    $(function(){
        $('#tag_list a.clearitem').click(function () {
            tagitems = '';
          $(this).parent().remove();
          $( "li.tags" ).each(function( index ) {
              tagitems = tagitems + $(this).text() + '|';
            });
          $('#tagitems').val(tagitems);
        });
    });
}(window, jQuery));
