(function (global, $, undefined) {
    $(function (){
        $('#role_toggle').bind('click', function() {
            document.getElementById('role_view').classList.remove('collapse');
            document.getElementById('admin_view').classList.add('collapse');
            document.getElementById('pending_view').classList.add('collapse');
        });
        $('#admin_toggle').bind('click', function() {
            document.getElementById('admin_view').classList.remove('collapse');
            document.getElementById('role_view').classList.add('collapse');
            document.getElementById('pending_view').classList.add('collapse');
        });
        $('#pending_toggle').bind('click', function() {
            document.getElementById('pending_view').classList.remove('collapse');
            document.getElementById('admin_view').classList.add('collapse');
            document.getElementById('role_view').classList.add('collapse');
        });
    });



}(window, jQuery));