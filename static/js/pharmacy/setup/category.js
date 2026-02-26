// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

$(function(){
    console.log("Category JS loaded!");
    function loadGroups(type_id){
        let group_select = $("#add_group");
        group_select.html('<option value="">Loading...</option>');

        if(type_id){
            $.get("/ajax/get-groups/", {type_id: type_id}, function(res){
                group_select.html('<option value="">Select Group</option>');

                if(res.groups.length > 0){
                    res.groups.forEach(function(g){
                        group_select.append('<option value="'+g.id+'">'+g.name+'</option>');
                    });
                } else {
                    group_select.html('<option value="">No groups found</option>');
                }
            });
        } else {
            group_select.html('<option value="">Select Group</option>');
        }
    }
    // ---------------- ADD MODAL ----------------
$('#addModal').on('shown.bs.modal', function () {
    $("#category_name").focus();

    let type_id = $("#add_type").val();  // hidden type
    let group_select = $("#add_group");

    // Clear previous options
    group_select.html('<option value="">Select Group</option>');

    // Fetch groups for the module type
    if(type_id){
        $.get("/ajax/get-groups/", {type_id: type_id}, function(res){
            if(res.groups.length > 0){
                res.groups.forEach(function(g){
                    group_select.append('<option value="'+g.id+'">'+g.name+'</option>');
                });
            } else {
                group_select.html('<option value="">No groups found</option>');
            }
        });
    }
});


    // ---------------- CHANGE TYPE IN ADD ----------------
    $("#add_type").change(function(){
        let type_id = $(this).val();
        let group_select = $("#add_group");
        group_select.html('<option value="">Select Group</option>');

        if(type_id){
            $.get("/ajax/get-groups/", {type_id: type_id}, function(res){
                res.groups.forEach(function(g){
                    group_select.append('<option value="'+g.id+'">'+g.name+'</option>');
                });
            });
        }
    });

    // ---------------- ADD CATEGORY SUBMIT ----------------
    $("#addForm").submit(function(e){
        e.preventDefault();
        $.ajax({
        type: "POST",
        url: "/add_category/",
        data: $(this).serialize(),  // includes hidden input type
        headers: { "X-CSRFToken": csrftoken },
        success: function(res){
            if(res.status=="success"){
                toastr.success("Item Category added successfully!");
                $("#addModal").modal('hide');
                setTimeout(()=>{ window.location.href = "?page=" + res.last_page; }, 800);
            } else {
                toastr.error(res.message || "Error adding category!");
            }
        }
    });

    });

    // ---------------- EDIT CATEGORY ----------------
    $(".editBtn").click(function(){
        let id = $(this).data("id");
        $.get("/get_category/"+id+"/", function(res){
            $("#edit_id").val(res.id);
            $("#edit_name").val(res.category_name);
            $("#edit_company").val(res.company);
            $("#edit_type").val(res.type);

            let group_select = $("#edit_group");
            group_select.html('<option value="">Select Group</option>');

            if(res.type){
                $.get("/ajax/get-groups/", {type_id: res.type}, function(res2){
                    res2.groups.forEach(function(g){
                        group_select.append('<option value="'+g.id+'">'+g.name+'</option>');
                    });
                    group_select.val(res.group);
                });
            }
            $("#editModal").modal("show");
        });
    });

    $("#edit_type").change(function(){
        let type_id = $(this).val();
        let group_select = $("#edit_group");
        group_select.html('<option value="">Select Group</option>');

        if(type_id){
            $.get("/ajax/get-groups/", {type_id: type_id}, function(res){
                res.groups.forEach(function(g){
                    group_select.append('<option value="'+g.id+'">'+g.name+'</option>');
                });
            });
        }
    });

    // ---------------- EDIT CATEGORY SUBMIT ----------------
    $("#editForm").submit(function(e){
        e.preventDefault();
        $.ajax({
            type: "POST",
            url: "/update_category/",
            data: $(this).serialize(),
            headers: { "X-CSRFToken": csrftoken },
            success: function(res){
                if(res.status == "updated"){
                    toastr.success("Item Category updated successfully!");
                    $("#editModal").modal('hide');
                    setTimeout(()=>{ location.reload(); }, 800);
                } else {
                    toastr.error("Error updating category!");
                }
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
