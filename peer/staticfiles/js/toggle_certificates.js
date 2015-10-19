$(document).ready(function(var_on_click, var_show){
    $(".certificate").click(function(){
        $(this).parent().find("pre").toggle();
    });
});
