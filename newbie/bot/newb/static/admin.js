(function (global, $, undefined) {
    $(function (){
        $('#role_toggle').bind('click', function() {
            document.getElementById('role_view').classList.remove('collapse');
            document.getElementById('admin_view').classList.add('collapse');
            document.getElementById('pending_view').classList.add('collapse');
            document.getElementById('messages_view').classList.add('collapse');
        });
        $('#admin_toggle').bind('click', function() {
            document.getElementById('admin_view').classList.remove('collapse');
            document.getElementById('role_view').classList.add('collapse');
            document.getElementById('pending_view').classList.add('collapse');
            document.getElementById('messages_view').classList.add('collapse');
        });
        $('#pending_toggle').bind('click', function() {
            document.getElementById('pending_view').classList.remove('collapse');
            document.getElementById('admin_view').classList.add('collapse');
            document.getElementById('role_view').classList.add('collapse');
            document.getElementById('messages_view').classList.add('collapse');
        });
        $('#messages_toggle').bind('click', function() {
            document.getElementById('messages_view').classList.remove('collapse');
            document.getElementById('pending_view').classList.add('collapse');
            document.getElementById('admin_view').classList.add('collapse');
            document.getElementById('role_view').classList.add('collapse');
        })
    });
    try{
        const team = document.getElementById('team');
        team.classList.add('custom-select');
    }
    catch
    (e)
    {
        
    }




}(window, jQuery));