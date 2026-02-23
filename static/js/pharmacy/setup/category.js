$(function(){
$('#addModal').on('shown.bs.modal', function () {
        $("#category_name").focus();
    });
    // ---------------- ADD CATEGORY ----------------
    $("#addForm").submit(function(e){
        e.preventDefault();
        $.post("/add_category/", $(this).serialize(), function(res){
            if(res.status=="success"){
                toastr.success("Item Category added successfully!");
                $("#addModal").modal('hide');
                setTimeout(()=>{ 
                    window.location.href = "?page=" + res.last_page; 
                }, 800);
            } else {
                toastr.error(res.message || "Error adding category!");
            }
        });
    });

    // ---------------- EDIT LOAD ----------------
    $(".editBtn").click(function(){
        let id = $(this).data("id");
        $.get("/get_category/"+id+"/", function(res){
            $("#edit_id").val(res.id);
            $("#edit_name").val(res.category_name);
            $("#edit_company").val(res.company);
            $("#edit_type").val(res.type);
            $("#edit_group").val(res.group);

            $("#editModal").modal("show");
        });
    });

    // ---------------- UPDATE CATEGORY ----------------
    $("#editForm").submit(function(e){
        e.preventDefault();
        $.post("/update_category/", $(this).serialize(), function(res){
            if(res.status=="updated"){
                toastr.success("Item Category updated successfully!");
                $("#editModal").modal('hide');
                setTimeout(()=>{ location.reload(); }, 800);
            } else {
                toastr.error("Error updating category!");
            }
        });
    });

    // ---------------- DELETE CATEGORY ----------------
    $(".deleteBtn").click(function(){
        if(!confirm("Delete this category?")) return;

        let id = $(this).data("id");
        $.get("/delete_category/"+id+"/", function(res){
            if(res.status=="deleted"){
                toastr.success("Item Category deleted successfully!");
                $("#row"+id).fadeOut();
            } else {
                toastr.error("Error deleting category!");
            }
        });
    });

    // ---------------- ROWS PER PAGE ----------------
    $('#rowsPerPage').change(function(){
        let rows = $(this).val();
        window.location.href = '?rows=' + rows;
    });

});
