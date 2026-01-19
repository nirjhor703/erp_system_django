$(function(){

    // 🔹 ADD
    $("#addForm").submit(function(e){
        e.preventDefault();
        $.post("/add_unit/", $(this).serialize(), function(res){
            if(res.status=="success"){
                toastr.success("Unit added successfully!");
                location.reload();
            } else {
                toastr.error(res.message);
            }
        });
    });

    // 🔹 EDIT LOAD
    $(".editBtn").click(function(){
        let id = $(this).data("id");
        $.get("/get_unit/"+id+"/", function(res){
            $("#edit_id").val(res.id);
            $("#edit_name").val(res.unit_name);
            $("#edit_company").val(res.company);
            $("#editModal").modal("show");
        });
    });

    // 🔹 UPDATE
    $("#editForm").submit(function(e){
        e.preventDefault();
        $.post("/update_unit/", $(this).serialize(), function(res){
            if(res.status=="updated"){
                toastr.success("Unit updated successfully!");
                location.reload();
            } else {
                toastr.error("Update failed!");
            }
        });
    });

    // 🔹 DELETE
    $(".deleteBtn").click(function(){
        if(!confirm("Delete this unit?")) return;
        let id = $(this).data("id");
        $.get("/delete_unit/"+id+"/", function(res){
            if(res.status=="deleted"){
                toastr.success("Unit deleted successfully!");
                $("#row"+id).fadeOut();
            }
        });
    });

    // 🔹 Rows per page change
    $("#rowsSelect").change(function(){
        let rows = $(this).val();
        window.location.href = "?rows=" + rows;
    });

});
