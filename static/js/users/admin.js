$(document).ready(function() {

    // ================= CSRF HELPER =================
    function csrfToken() {
        return $('input[name="csrfmiddlewaretoken"]').val() || $("meta[name='csrf-token']").attr("content");
    }

    // ================= ADD ADMIN =================
    $("#addSaveBtn").off("click").on("click", function() {
        let name = $("#addName").val().trim();
        let email = $("#addEmail").val().trim();
        let phone = $("#addPhone").val().trim();
        let store = $("#addStore").val();
        let password = $("#addPassword").val();
        let confirmPassword = $("#addConfirmPassword").val();
        let image = $("#addImage")[0].files[0];

        if (!name || !email || !phone || !store || !password || !confirmPassword) {
            alert("All required fields must be filled");
            return;
        }

        if (password !== confirmPassword) {
            alert("Passwords do not match");
            return;
        }

        let formData = new FormData();
        formData.append("name", name);
        formData.append("email", email);
        formData.append("phone", phone);
        formData.append("store_id", store);
        formData.append("password", password);
        formData.append("confirm_password", confirmPassword);
        if (image) formData.append("image", image);
        formData.append("csrfmiddlewaretoken", csrfToken());

        $.ajax({
            url: "/users/admin/create/",
            type: "POST",
            data: formData,
            contentType: false,
            processData: false,
            success: function(res) {
                if (res.success) {
                    let imgTag = res.image ? `<img src="${res.image}" style="height:40px;">` : "No Image";
                    $("#adminTableBody").append(`
                        <tr data-id="${res.id}">
                            <td>${$("#adminTableBody tr").length + 1}</td>
                            <td class="ad-user-id">${res.user_id}</td>
                            <td class="ad-name">${res.name}</td>
                            <td class="ad-email">${res.email}</td>
                            <td class="ad-phone">${res.phone}</td>
                            <td class="ad-image">${imgTag}</td>
                            <td class="ad-status">${res.status == 1 ? "Active" : "Inactive"}</td>
                            <td class="ad-store">${res.store_name || res.store_id}</td>
                            <td>
                                <button class="btn btn-sm btn-info edit-btn" data-bs-toggle="modal" data-bs-target="#editModal">Edit</button>
                                <button class="btn btn-sm btn-danger delete-btn">Delete</button>
                            </td>
                        </tr>
                    `);
                    $("#addModal").modal('hide');
                    $("#addName, #addEmail, #addPhone, #addPassword, #addConfirmPassword").val("");
                    $("#addStore").val("");
                    $("#addImage").val(null);
                } else {
                    alert(res.message || "Failed to create admin");
                }
            },
            error: function() {
                alert("AJAX error: Could not create admin");
            }
        });
    });

    // ================= EDIT MODAL =================
    $(document).off("click", ".edit-btn").on("click", ".edit-btn", function() {
        let row = $(this).closest("tr");
        let id = row.data("id");
        let name = row.find(".ad-name").text();
        let email = row.find(".ad-email").text();
        let phone = row.find(".ad-phone").text();
        let store = row.find(".ad-store").text();

        $("#editId").val(id);
        $("#editName").val(name);
        $("#editEmail").val(email);
        $("#editPhone").val(phone);
        $("#editStore").val(store);
        $("#editPassword, #editConfirmPassword").val("");
        $("#editImage").val(null);
    });

    // ================= UPDATE ADMIN =================
    $("#editSaveBtn").off("click").on("click", function() {
        let id = $("#editId").val();
        let name = $("#editName").val().trim();
        let email = $("#editEmail").val().trim();
        let phone = $("#editPhone").val().trim();
        let store = $("#editStore").val();
        let password = $("#editPassword").val();
        let confirmPassword = $("#editConfirmPassword").val();
        let image = $("#editImage")[0].files[0];

        if (!name || !email || !phone || !store) {
            alert("Name, Email, Phone and Store are required");
            return;
        }

        if (password && password !== confirmPassword) {
            alert("Passwords do not match");
            return;
        }

        let formData = new FormData();
        formData.append("name", name);
        formData.append("email", email);
        formData.append("phone", phone);
        formData.append("store_id", store);
        if (password) formData.append("password", password);
        if (confirmPassword) formData.append("confirm_password", confirmPassword);
        if (image) formData.append("image", image);
        formData.append("csrfmiddlewaretoken", csrfToken());

        $.ajax({
            url: `/users/admin/update/${id}/`,
            type: "POST",
            data: formData,
            contentType: false,
            processData: false,
            success: function(res) {
                if (res.success) {
                    let row = $(`tr[data-id='${id}']`);
                    row.find(".ad-name").text(res.name);
                    row.find(".ad-email").text(res.email);
                    row.find(".ad-phone").text(res.phone);
                    row.find(".ad-store").text(res.store_name || res.store_id);
                    row.find(".ad-status").text(res.status == 1 ? "Active" : "Inactive");
                    row.find(".ad-image").html(res.image ? `<img src="${res.image}" style="height:40px;">` : "No Image");
                    $("#editModal").modal('hide');
                } else {
                    alert(res.message || "Update failed");
                }
            },
            error: function() {
                alert("AJAX error: Could not update admin");
            }
        });
    });

    // ================= DELETE ADMIN =================
    $(document).off("click", ".delete-btn").on("click", ".delete-btn", function() {
        if (!confirm("Are you sure you want to delete this admin?")) return;

        let row = $(this).closest("tr");
        let id = row.data("id");

        $.post(`/users/admin/delete/${id}/`, {
            csrfmiddlewaretoken: csrfToken()
        }, function(res) {
            if (res.success) {
                row.remove();
                // Recalculate SL
                $("#adminTableBody tr").each(function(index) {
                    $(this).find("td:first").text(index + 1);
                });
            } else {
                alert(res.message || "Delete failed");
            }
        }).fail(function() {
            alert("AJAX error: Could not delete admin");
        });
    });

});
