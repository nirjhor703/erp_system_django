$(function(){
$('#addModal').on('shown.bs.modal', function () {
        $("#tran_group_name").focus();
    });

// ================= ADD =================
$("#addForm").submit(function(e){
    e.preventDefault();
    let form = $(this);

    $.ajax({
        url: "/transaction-groupes/add/",
        method: "POST",
        data: form.serialize(),
        success: function(res){
            toastr.success("Transaction Groupe added!");
            $("#addModal").modal("hide");
            setTimeout(() => {
                let rows = $("#rowsPerPageSelect").val() || 15;
                window.location.href = window.location.pathname + "?page=" + res.last_page + "&rows=" + rows;
            }, 500);
            

            // Scroll to last page (assume server returns total pages)
            location.href = "?page=last&rows=" + $("#rowsPerPage").val();
        },
        error: function(){
            toastr.error("Something went wrong!");
        }
    });
});


// $("#addForm button[type='submit']").click(function(e){
//     e.preventDefault();  
//     $("#addModal").modal("hide");
//     setTimeout(function(){
//         toastr.success("Transaction Groupe added!");
//     }, 200);
//     location.href = "?page=last&rows=" + $("#rowsPerPage").val();
// });

// ================= EDIT MODAL =================
$(document).on("click", ".editBtn", function(){
    let id = $(this).data("id");

    $.get("/transaction-groupes/get/", {id:id}, function(res){
        $("#edit_id").val(res.id);
        $("#edit_name").val(res.tran_groupe_name);
        $("#edit_company").val(res.company);
        $("#edit_type").val(res.tran_groupe_type);

        $("#editModal").modal("show");
    });
});

// ================= UPDATE =================
$("#editForm").submit(function(e){
    e.preventDefault();
    let form = $(this);

    $.ajax({
        url: "/transaction-groupes/update/",
        method: "POST",
        data: form.serialize(),
        success: function(res){
            $("#editModal").modal("hide");
            toastr.success("Transaction Groupe updated!");

            // Update row in table without refresh
            let id = $("#edit_id").val();
            let row = $("#row"+id);
            row.find("td:nth-child(2)").text($("#edit_name").val());
            row.find("td:nth-child(3)").text($("#edit_company option:selected").text());
        },
        error: function(){
            toastr.error("Something went wrong!");
        }
    });
});

// ================= DELETE =================
$(document).on("click", ".deleteBtn", function(){
    let id = $(this).data("id");
    if(confirm("Are you sure to delete?")){
        $.post("/transaction-groupes/delete/", {
            id: id,
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
        }, function(res){
            toastr.success("Transaction Groupe deleted!");
            $("#row"+id).fadeOut(500, function(){ $(this).remove(); });
        });
    }
});

// ================= ROWS PER PAGE =================
$("#rowsPerPage").change(function(){
    let rows = $(this).val();
    location.href = "?rows=" + rows;
});

});
