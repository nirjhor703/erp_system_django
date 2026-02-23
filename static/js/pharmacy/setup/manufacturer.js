$(function(){
// When the add modal is shown
$('#addModal').on('shown.bs.modal', function () {
        $("#manufacturer_name").focus();
    });


    /* ADD */
$("#addForm").submit(function(e){
    e.preventDefault();

    let data = $(this).serializeArray();
    data.push({name: 'rows', value: $("#rowsPerPageSelect").val() || 15});

    $.post("/add_manufacturer/", $.param(data), function(res){
        if(res.status=="success"){
            toastr.success("Manufacturer added successfully!");
            $("#addModal").modal('hide');

            // Redirect to the last page
            setTimeout(() => {
                let rows = $("#rowsPerPageSelect").val() || 15;
                window.location.href = window.location.pathname + "?page=" + res.last_page + "&rows=" + rows;
            }, 500);
        } else {
            toastr.error(res.message || "Error adding manufacturer!");
        }
    });
});


    


    /* EDIT LOAD */
    $(".editBtn").click(function(){
        let id = $(this).data("id");

        $.get("/get_manufacturer/"+id+"/", function(res){
            $("#edit_id").val(res.id);
            $("#edit_name").val(res.manufacturer_name);
            $("#edit_company").val(res.company);
            $("#editModal").modal("show");
        });
    });


    /* UPDATE */
    $("#editForm").submit(function(e){
        e.preventDefault();

        $.post("/update_manufacturer/", $(this).serialize(), function(res){
            if(res.status=="updated"){
                toastr.success("Manufacturer updated successfully!");
                $("#editModal").modal('hide');
                setTimeout(()=>{ location.reload(); }, 1000);
            } else {
                toastr.error("Error updating manufacturer!");
            }
        });
    });


    /* DELETE */
    $(".deleteBtn").click(function(){
        if(!confirm("Delete this manufacturer?")) return;

        let id = $(this).data("id");

        $.get("/delete_manufacturer/"+id+"/", function(res){
            if(res.status=="deleted"){
                $("#row"+id).fadeOut();
                toastr.success("Manufacturer deleted successfully!");
            } else {
                toastr.error("Error deleting manufacturer!");
            }
        });
    });
$('#rowsPerPage').change(function(){
    let rows = $(this).val();
    window.location.href = '?rows=' + rows; // reload page with new rows per page
});

});
