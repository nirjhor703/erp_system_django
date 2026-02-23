$(document).ready(function () {

$(document).on("click", ".verifyBtn", function () {
    let tranId  = $(this).data("tran-id");
    $("#verify_tran_id").val(tranId);
    $("#VerifyBtn").show();
    $("#verifyModalLabel").text("Verify Transaction");


    $.get(`/transaction-main/get/?id=${tranId}`, function(res) {
        if (!res.success) {
            alert("Transaction not found!");
            
            return;
        }

        let d = res.data;

        $("#verify_location").val(d.location || "");
        $("#verify_supplier").val(d.supplier || "");
        $("#verify_invoiceAmount").val(d.bill_amount || 0);
        $("#verify_discount").val(d.discount || 0);
        $("#verify_netAmount").val(d.net_amount || 0);
        $("#verify_advanced").val(d.payment || 0);
        $("#verify_balance").val(d.due || 0);
        $("#verify_date").val(d.tran_date.split("T")[0] || "");
        $("#verify_store").val(d.store_id || "");
        $("#verify_payment_method").val(d.tran_method || "");

        // medicines
        let html = "";
        if (d.details && d.details.length) {
            d.details.forEach((med, idx) => {
                html += `<tr>
                    <td>${idx + 1}</td>
                    <td>${med.tran_head_id || ""}</td>
                    <td>${med.name || ""}</td>
                    <td>${med.qty || 0}</td>
                    <td>${med.cp || 0}</td>
                    <td>${med.total || 0}</td>
                </tr>`;
            });
        } else {
            html = `<tr><td colspan="5">No medicines found</td></tr>`;
        }

        $("#verify_selectedMedicineList").html(html);
        new bootstrap.Modal(document.getElementById("verifyModal")).show();
    });
});




    // VERIFY BUTTON
$("#VerifyBtn").click(function () {

    let tran_id = $("#verify_tran_id").val();

    if (!tran_id) {
        alert("Transaction ID missing!");
        return;
    }

    $.ajax({
        url: "/transaction-temp/verify/",
        type: "POST",
        data: {
            tran_id: tran_id,
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
        },
        success: function (res) {
            if (res.success) {

                alert("Transaction verified!");
                $("#verifyModal").modal("hide");
                setTimeout(() => {
                    window.location.href = "?status=1&page=" + res.last_page;
                }, 800);
                

                // 🔥 Find row using tran_id
                let row = $(`#row-${tran_id}`);


                row.find(".action-cell").html(`
                    <span class="badge bg-success">Verified</span>
                    <button 
                        class="btn btn-sm btn-danger deleteRow verified"
                        data-main-id="${res.main_id}">
                        Delete
                    </button>
                `);

                row.addClass("table-success");

            } else {
                alert(res.message || "Verification failed!");
            }
        },
        error: function () {
            alert("Server error!");
        }
    });
});

$(document).on("click", ".showBtn", function () {

    let tranId = $(this).data("tran-id");
    $("#verify_tran_id").val(tranId);

    $.get(`/transaction-main/get/?id=${tranId}`, function(res) {
        if (!res.success) {
            alert("Transaction not found!");
            return;
        }

        let d = res.data;

        // fill fields (same as verify)
        $("#verify_location").val(d.location || "");
        $("#verify_supplier").val(d.supplier || "");
        $("#verify_invoiceAmount").val(d.bill_amount || 0);
        $("#verify_discount").val(d.discount || 0);
        $("#verify_netAmount").val(d.net_amount || 0);
        $("#verify_advanced").val(d.payment || 0);
        $("#verify_balance").val(d.due || 0);
        $("#verify_date").val(d.tran_date.split("T")[0] || "");
        $("#verify_store").val(d.store_id || "");
        $("#verify_payment_method").val(d.tran_method || "");

        // medicines table
        let html = "";
        if (d.details && d.details.length) {
            d.details.forEach((med, idx) => {
                html += `<tr>
                    <td>${idx + 1}</td>
                    <td>${med.tran_head_id || ""}</td>
                    <td>${med.name || ""}</td>
                    <td>${med.qty || 0}</td>
                    <td>${med.cp || 0}</td>
                    <td>${med.total || 0}</td>
                </tr>`;
            });
        } else {
            html = `<tr><td colspan="6">No medicines found</td></tr>`;
        }

        $("#verify_selectedMedicineList").html(html);

        // 🔥 SHOW MODE
        $("#VerifyBtn").hide();        // no verify
        $("#verifyModalLabel").text("Transaction Details");

        new bootstrap.Modal(document.getElementById("verifyModal")).show();
    });
});





});
