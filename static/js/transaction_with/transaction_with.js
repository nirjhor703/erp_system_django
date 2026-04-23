$(document).ready(function () {

    function updateMethodNote(selectId, noteId) {
        let value = $(selectId).val();
        let noteText = "";

        if (value === "Receive") {
            noteText = "Note: As CLIENT";
        } else if (value === "Payment") {
            noteText = "Note: As SUPPLIER";
        } else if (value === "Both") {
            noteText = "Note: As CLIENT & SUPPLIER";
        }

        if (noteText !== "") {
            $(noteId).text(noteText).show();
        } else {
            $(noteId).text("").hide();
        }
    }

    // Add modal method change
    $("#add_tran_method").change(function () {
        updateMethodNote("#add_tran_method", "#add_method_note");
    });

    // Edit modal method change
    $("#edit_method").change(function () {
        updateMethodNote("#edit_method", "#edit_method_note");
    });

    // ADD
    $("#addForm").submit(function (e) {
        e.preventDefault();

        $.post("/transaction-with/store/", $(this).serialize(), function (response) {
            if (response.success) {
                toastr.success("Transaction With Added");
                $("#addModal").modal("hide");
                location.reload();
            } else {
                toastr.error(response.message || "Something went wrong");
            }
        }).fail(function () {
            toastr.error("Failed to add transaction with");
        });
    });

    // FETCH
    $(".editBtn").click(function () {
        let id = $(this).data("id");

        $.get("/transaction-with/fetch/", { id: id }, function (res) {
            if (res.success === false) {
                toastr.error(res.message || "Data not found");
                return;
            }

            $("#edit_id").val(res.id);
            $("#edit_name").val(res.tran_with_name);
            $("#edit_tran_type").val(res.tran_type);
            $("#edit_method").val(res.tran_method);

            updateMethodNote("#edit_method", "#edit_method_note");

            $("#editModal").modal("show");
        }).fail(function () {
            toastr.error("Failed to fetch data");
        });
    });

    // UPDATE
    $("#editForm").submit(function (e) {
        e.preventDefault();

        $.post("/transaction-with/update/", $(this).serialize(), function (response) {
            if (response.success) {
                toastr.success("Transaction With Updated");
                $("#editModal").modal("hide");
                location.reload();
            } else {
                toastr.error(response.message || "Something went wrong");
            }
        }).fail(function () {
            toastr.error("Failed to update transaction with");
        });
    });

    // DELETE
    $(".deleteBtn").click(function () {
        let id = $(this).data("id");

        if (confirm("Delete this transaction with?")) {
            $.post("/transaction-with/delete/", {
                id: id,
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").first().val()
            }, function (response) {
                if (response.success) {
                    toastr.warning("Transaction With Deleted");
                    $("#row" + id).fadeOut();
                } else {
                    toastr.error(response.message || "Something went wrong");
                }
            }).fail(function () {
                toastr.error("Failed to delete transaction with");
            });
        }
    });

});