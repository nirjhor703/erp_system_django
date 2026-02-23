$(function(){

    // ================= ADD =================
    $("#addForm").on("submit", function(e){
        e.preventDefault();
        let form = $(this);

        $.ajax({
            url: "/tranhead_add/",
            method: "POST",
            data: form.serialize(),
            success: function(res){
                if(res.status === "success"){

                    // Hide modal
                    $("#addModal").modal("hide");

                    // Show toaster after hide animation
                    setTimeout(()=> toastr.success("Transaction Head added!"), 200);

                    // Optional: clear form
                    form[0].reset();

                    // --- Fetch last page with new row ---
                    let currentUrl = new URL(window.location.href);
                    currentUrl.searchParams.set('page', 'last'); // custom logic in backend may be needed
                    window.location.href = currentUrl.href;

                } else {
                    toastr.error("Something went wrong!");
                }
            },
            error: function(err){
                console.log(err);
                toastr.error("Server Error!");
            }
        });
    });

    // ================= EDIT =================
    $(".editBtn").click(function(){
        let id = $(this).data("id");

        $.get("/tranhead_edit/" + id + "/", function(res){
            // Fill modal
            $("#edit_id").val(res.id);
            $("#edit_tran_head_name").val(res.tran_head_name);
            $("#edit_groupe").val(res.groupe_id);
            $("#edit_category").val(res.category_id);
            $("#edit_manufacturer").val(res.manufacturer_id);
            $("#edit_form").val(res.form_id);
            $("#edit_unit").val(res.unit_id);
            $("#edit_mrp").val(res.mrp);
            $("#edit_company").val(res.company_id);
            $("#edit_editable").val(res.editable);

            $("#editModal").modal("show");
        });
    });

$(document).on("submit", "#editForm", function(e){
    e.preventDefault();

    let id = $("#edit_id").val();

    $.ajax({
        url: "/tranhead_edit/" + id + "/",
        type: "POST",
        data: $(this).serialize(),
        success: function(res){
            if(res.status === "success"){
                toastr.success("Transaction Head Updated!");
                $("#editModal").modal("hide");
                setTimeout(() => location.reload(), 500);
            } else {
                toastr.error("Update Failed!");
            }
        },
        error: function(){
            toastr.error("Something went wrong!");
        }
    });
});


    // ================= DELETE =================
    $(".deleteBtn").click(function(){
        if(!confirm("Delete this Transaction Head?")) return;

        let id = $(this).data("id");

        $.post("/tranhead_delete/" + id + "/", {
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
        }, function(res){
            if(res.status === "success"){
                toastr.warning("Deleted!");
                $("#row" + id).fadeOut();
            } else {
                toastr.error("Delete Failed!");
            }
        });
    });

});
