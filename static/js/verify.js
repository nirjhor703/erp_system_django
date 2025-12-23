// Dynamic click for verify buttons
$(document).on("click", ".verify-btn", function() {
    const tranId = $(this).data("tran-id");
    $("#verify_tran_id").val(tranId);

    // Fetch transaction data
    $.ajax({
        url: `/get-transaction/${tranId}/`,
        method: "GET",
        success: function(data) {
            // Fill modal form fields
            $("#location").val(data.location);
            $("#store").val(data.store_id);
            $("#date").val(data.tran_date.substring(0,10));
            $("#supplier").val(data.supplier);
            $("#productSearch").val(""); // you can pre-fill product if needed
            // You can also populate medicines table if needed
            $("#quantity").val(data.quantity);
            $("#unit").val(data.unit);
            $("#expiry").val(data.expiry_date);
            $("#price").val(data.cp);
            $("#mrp").val(data.mrp);
            $("#total").val(data.total);

            // Open modal
            $("#verifyModal").modal("show");
        },
        error: function() {
            alert("Failed to fetch transaction data");
        }
    });
});
