$(function(){
$('#addModal').on('shown.bs.modal', function () {
        $("#form_name").focus();
    });
    /* ADD */
$("#addForm").submit(function(e){
    e.preventDefault();

    $.post("/add_form/", $(this).serialize(), function(res){
        if(res.status=="success"){
            // Redirect to last page
            window.location.href = window.location.pathname + "?page=" + res.last_page;
        } else {
            alert(res.message || "Error adding form");
        }
    });
});


    /* EDIT LOAD */
    $(".editBtn").click(function(){
        let id = $(this).data("id");
        $.get("/get_form/"+id+"/", function(res){
            $("#edit_id").val(res.id);
            $("#edit_name").val(res.form_name);
            $("#edit_company").val(res.company);
            $("#edit_type").val(res.type);
            $("#editModal").modal("show");
        });
    });

    /* UPDATE */
    $("#editForm").submit(function(e){
        e.preventDefault();
        $.post("/update_form/", $(this).serialize(), function(res){
            if(res.status=="updated"){
                location.reload();
            } else {
                alert("Update failed");
            }
        });
    });

    /* DELETE */
    $(".deleteBtn").click(function(){
        if(!confirm("Delete this form?")) return;
        let id = $(this).data("id");
        $.get("/delete_form/"+id+"/", function(res){
            if(res.status=="deleted"){
                $("#row"+id).fadeOut();
            }
        });
    });

});
