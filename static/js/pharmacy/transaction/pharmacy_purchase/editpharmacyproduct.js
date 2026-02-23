// let editProducts = [];
    // let editCurrentIndex = -1;
    // let editOffset = 0;
    // let editQuery = "";

    // ===========================
    // OPEN MODAL & SETUP
    // ===========================
$(document).on("click", ".editBtn", function() {
    let tranId = $(this).data("tran-id");
    $("#edit_tran_id").val(tranId);

    $("#editModal").modal("show");

    $("#editModal").one("shown.bs.modal", function () {   // IMPORTANT
        loadEditProducts();
        fetchTransaction(tranId);
    });
});
    // ===========================
    // FETCH TRANSACTION DETAILS
    // ===========================
function fetchTransaction(tranId) {
    $.get(`/transaction/get/${tranId}/`, function(res) {
        if(!res.success) return alert("Transaction not found!");

        let d = res.data;

        // 🔹 Basic fields
        $("#edit_location").val(d.location);
        $("#edit_store").val(d.store_id);

        $("#edit_date").val(d.tran_date);

        $("#edit_payment_method").val(d.tran_method);
        $("#edit_discount").val(d.discount);
        $("#edit_advanced").val(d.payment);
        $("#edit_invoiceAmount").val(d.bill_amount);
        $("#edit_netAmount").val(d.net_amount);
        $("#edit_balance").val(d.due);

        // 🔹 Store
        if(d.store_id) $("#edit_store").val(d.store_id).trigger("change");

        // 🔹 Supplier (input field)
        $("#edit_supplier").val(d.supplier);

        // 🔹 Selected products
        $("#edit_selectedMedicineList").empty();
        if(d.details && d.details.length > 0){
            d.details.forEach((p, idx) => {
                let row = `
                    <tr data-id="${p.id}">
                        <td>${idx+1}</td>
                        <td>${p.name}</td>
                        <td>${p.qty}</td>
                        <td>${p.cp}</td>
                        <td>${p.total}</td>
                        <td><button type="button" class="btn btn-sm btn-danger remove-item">Remove</button></td>
                    </tr>
                `;
                $("#edit_selectedMedicineList").append(row);
            });
        }

        // 🔹 Update invoice summary
        updateEditInvoiceSummary();
    });
}









    // ===========================
    // LOAD SUPPLIERS
    // ===========================
function loadEditSuppliers(selectedName){
    $.get("/get-suppliers/", function(res){
        let html = '<option value="">Select Supplier</option>';
        res.suppliers.forEach(s => {
            html += `<option value="${s.id}" ${s.manufacturer_name == selectedName ? "selected" : ""}>${s.manufacturer_name}</option>`;
        });
        $("#edit_supplier").html(html);
    });
}




    // ===========================
    // LOAD PRODUCTS
    // ===========================
    function loadEditProducts(q = "", newOffset = 0, append = false) {
        $.ajax({
            url: "/product-search/",
            method: "GET",
            data: { q: q, offset: newOffset, limit: 50 },
            success: function(response) {
                let fetched = response.results || [];
                if (append) editProducts = editProducts.concat(fetched);
                else editProducts = fetched;

                editOffset = newOffset;
                if (!append) editCurrentIndex = 0;

                renderEditTable();
                highlightEditRow();
            }
        });
    }

function renderEditTable() {
    let html = "";
    editProducts.forEach((p, i) => {
        html += `
        <tr class="edit-row" data-index="${i}">
            <td>${p.name}</td>
            <td>${p.generic || ""}</td>
            <td>${p.manufacturer}</td>
            <td>${p.form}</td>
            <td>${p.quantity}</td>
            <td>${p.cp}</td>
            <td>${p.mrp}</td>
            <td><button type="button" class="btn btn-sm btn-success selectEditBtn">Select</button></td>
        </tr>`;
    });
    $("#edit_medicineListTableBody").html(html);
}


function highlightEditRow() {
    let rows = $("#edit_medicineListTableBody tr");
    rows.removeClass("selected-row");

    if (editCurrentIndex >= 0 && editCurrentIndex < rows.length) {
        let row = $(rows[editCurrentIndex]);
        row.addClass("selected-row");
        row[0].scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
}

    // ===========================
    // PRODUCT SEARCH
    // ===========================
    $("#edit_productSearch").on("input", function() {
        editQuery = $(this).val();
        editOffset = 0;
        loadEditProducts(editQuery, editOffset);
    });

    // ===========================
    // KEYBOARD NAVIGATION
    // ===========================
$(document).on("keydown", "#editModal", function(e){

    if(!$("#editModal").is(":visible")) return;

    let rows=$("#edit_medicineListTableBody tr");
    if(!rows.length) return;

    if(e.key==="ArrowDown"){
        e.preventDefault();
        editCurrentIndex=Math.min(editCurrentIndex+1,rows.length-1);
        highlightEditRow();
    }

    if(e.key==="ArrowUp"){
        e.preventDefault();
        editCurrentIndex=Math.max(editCurrentIndex-1,0);
        highlightEditRow();
    }

    // ENTER → select OR add
    if(e.key==="Enter"){
        e.preventDefault();

        // Step–1 : Select product
        if(!$("#edit_quantity").is(":focus")){
            let p=editProducts[editCurrentIndex];
            if(!p) return;
            $("#edit_productSearch").val(p.name);
            $("#edit_price").val(p.cp);
            $("#edit_quantity").focus();
            return;
        }

        // Step–2 : Add into selected list
        let qty=parseFloat($("#edit_quantity").val());
        let price=parseFloat($("#edit_price").val());
        if(!qty||!price) return;

        let total=qty*price;
        let pname=$("#edit_productSearch").val();

        let row=`
        <tr>
            <td>${$("#edit_selectedMedicineList tr").length+1}</td>
            <td>${pname}</td>
            <td>${qty}</td>
            <td>${price}</td>
            <td>${total.toFixed(2)}</td>
            <td><button class="btn btn-sm btn-danger remove-item">Remove</button></td>
        </tr>`;

        $("#edit_selectedMedicineList").append(row);

        $("#edit_productSearch,#edit_price,#edit_quantity,#edit_total").val("");
    }
});



    // ===========================
    // CLICK ROW
    // ===========================
    $(document).on("click", "#edit_medicineListTableBody tr", function() {
        let index = $(this).data("index");
        editCurrentIndex = index;
        highlightEditRow();
        selectEditProduct(editProducts[index]);
    });

    function selectEditProduct(product) {
        $("#edit_productSearch").val(product.name);
        $("#edit_price").val(product.cp);
        $("#edit_quantity").focus();
    }

    // ===========================
    // ADD TO SELECTED LIST
    // ===========================
$("#edit_quantity").on("keydown", function (e) {
    if (e.key === "Enter") {
        e.preventDefault();
        e.stopPropagation(); // VERY IMPORTANT to prevent conflicts

        // Get values directly from inputs
        let pname = $("#edit_productSearch").val().trim();
        let price = parseFloat($("#edit_price").val()) || 0;
        let qty   = parseFloat($("#edit_quantity").val()) || 0;
        let total = parseFloat($("#edit_total").val()) || 0;
        let unit  = $("#edit_unit").val() || "";

        $("#edit_productSearch").focus();

        if(!pname || price <= 0 || qty <= 0 || total <= 0){
            alert("Please select a product and enter quantity correctly.");
            return;
        }

        addToEditSelectedList(pname, price, qty, total, unit);
    }
});



    $("#edit_quantity,#edit_price").on("input",function(){
    let q=parseFloat($("#edit_quantity").val())||0;
    let p=parseFloat($("#edit_price").val())||0;
    $("#edit_total").val((q*p).toFixed(2));
});

function addToEditSelectedList(pname, price, qty, total, unit, productId="") {
    let row = `
        <tr data-id="${productId}">
            <td>${$("#edit_selectedMedicineList tr").length + 1}</td>
            <td>${pname}</td>
            <td>${qty}</td>
            <td>${price}</td>
            <td>${total.toFixed(2)}</td>
            <td>
                <button type="button" class="btn btn-sm btn-danger remove-item">Remove</button>
            </td>
        </tr>
    `;
    $("#edit_selectedMedicineList").append(row);

    $("#edit_productSearch,#edit_price,#edit_quantity,#edit_total").val("");
    $("#edit_unit").val("PCS");

    updateEditInvoiceSummary();
}



    // ===========================
    // REMOVE ITEM
    // ===========================
    $(document).on("click", ".remove-item", function() {
        $(this).closest("tr").remove();
        updateEditInvoiceSummary();
    });

    // ===========================
    // INVOICE SUMMARY UPDATE
    // ===========================
function updateEditInvoiceSummary() {
    let invoiceAmount = 0;
    $("#edit_selectedMedicineList tr").each(function() {
        let total = parseFloat($(this).find("td:eq(4)").text()) || 0;
        invoiceAmount += total;
    });

    let discount = parseFloat($("#edit_discount").val()) || 0;
    let advance = parseFloat($("#edit_advanced").val()) || 0;

    let discountAmount = (invoiceAmount * discount) / 100;
    let netAmount = invoiceAmount - discountAmount;
    if(netAmount < 0) netAmount = 0;

    let balance = netAmount - advance;
    if(balance < 0) balance = 0;

    $("#edit_invoiceAmount").val(invoiceAmount.toFixed(2));
    $("#edit_netAmount").val(netAmount.toFixed(2));
    $("#edit_balance").val(balance.toFixed(2));
}

