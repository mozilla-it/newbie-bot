
Date.prototype.toDateInputValue = (function() {
    var local = new Date(this);
    local.setMinutes(this.getMinutes() - this.getTimezoneOffset());
    return local.toJSON().slice(0,10);
});
document.getElementById('send_date').value = new Date().toDateInputValue();

(function (global, $, undefined) {
    $(function (){
        $('#add_tag').bind('click', function () {
            $('<li class="list-group-item">' + $('input[name="tag_val"]').val() + '</li>').appendTo($("#tag_list"));
            $('input[name="tag_val"]').val('');
        });

    });
}(window, jQuery));
