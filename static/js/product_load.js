$(document).ready(function () {

    $('#addMedicineModal').on('shown.bs.modal', function () {
        $("#productSearch").focus();
    });

    let products = [];
    let currentIndex = -1;
    let offset = 0;
    let query = "";

    function loadProducts(q = "", newOffset = 0, append = false) {
        $.ajax({
            url: "/product-search/",
            method: "GET",
            data: { q: q, offset: newOffset },
            success: function (response) {
                let fetched = response.results || [];

                if (append) products = products.concat(fetched);
                else {
                    products = fetched;
                    offset = newOffset;
                    currentIndex = 0;
                }

                renderTable();
                highlightRow();
            }
        });
    }

    function renderTable() {
        let html = "";
        products.forEach((p, i) => {
            html += `
                <tr data-index="${i}">
                    <td>${i + 1}</td>
                    <td>${p.name}</td>
                    <td>${p.manufacturer}</td>
                    <td>${p.form}</td>
                    <td>${p.quantity}</td>
                    <td>${p.cp}</td>
                    <td>${p.mrp}</td>
                </tr>
            `;
        });
        $("#medicineListTableBody").html(html);
    }

    function highlightRow() {
        let rows = $("#medicineListTableBody tr");
        rows.removeClass("selected-row");

        if (currentIndex >= 0 && currentIndex < rows.length) {
            let row = $(rows[currentIndex]);
            row.addClass("selected-row");
            row[0].scrollIntoView({ behavior: "smooth", block: "center" });
        }
    }
    // Click on any row → fill product name and price
$(document).on("click", "#medicineListTableBody tr", function () {
    let index = $(this).data("index");
    if (index === undefined) return;

    // Get selected product from products array
    let selectedProduct = products[index];

    if (!selectedProduct) return;
        // Remove previous highlight
    $("#medicineListTableBody tr").removeClass("selected-row");

    // Highlight clicked row
    $(this).addClass("selected-row");

    // Set product name and price in input fields
    $("#productSearch").val(selectedProduct.name);
    $("#price").val(selectedProduct.cp);

    // Focus quantity field for quick entry
    $("#quantity").focus();
});


    $("#productSearch").on("input", function () {
        query = $(this).val();
        offset = 0;
        loadProducts(query, offset);
    });

    // PRICE × QTY calculation
    $("#quantity").on("input", function () {
        let quantity = parseFloat($(this).val()) || 0;
        let price = parseFloat($("#price").val()) || 0;
        let total = quantity * price;
        $("#total").val(total.toFixed(2));
    });

// ADD to selected list
function addToSelectedList(pname, price, qty, total) {

    let row = `
        <tr>
            <td>${$("#selectedMedicineList tr").length + 1}</td>
            <td>${pname}</td>
            <td>${qty}</td>
            <td>${price}</td>
            <td>${total}</td>
            <td>
                <button type="button" class="btn btn-sm btn-danger remove-item">Remove</button>
            </td>
        </tr>
    `;

    $("#selectedMedicineList").append(row);

    // Clear input fields
    $("#productSearch").val("");
    $("#price").val("");
    $("#quantity").val("");
    $("#total").val("");

    updateSelectedTotal();
    updateInvoiceSummary(); 
}

// Remove button functionality
$(document).on("click", ".remove-item", function () {
    $(this).closest("tr").remove();

    // Update SL numbers
    $("#selectedMedicineList tr").each(function (index) {
        $(this).find("td:first").text(index + 1);
    });

    // Update total
    updateSelectedTotal();
});

// Function to calculate bottom total
function updateSelectedTotal() {
    let total = 0;
    $("#selectedMedicineList tr").each(function () {
        let price = parseFloat($(this).find("td:eq(3)").text()) || 0;
        let qty = parseFloat($(this).find("td:eq(2)").text()) || 0;
        total += price * qty;
    });
    $("#bottomTotal").text(total.toFixed(2));
}

    // SINGLE KEYDOWN HANDLER → No duplicates
    $(document).on("keydown", function (e) {

        let rows = $("#medicineListTableBody tr");
        if (rows.length === 0) return;

        if (e.key === "ArrowDown") {
            e.preventDefault();
            if (currentIndex < rows.length - 1) {
                currentIndex++;
            } else {
                offset += 5;
                loadProducts(query, offset, true);
                currentIndex++;
            }
            highlightRow();
        }

        if (e.key === "ArrowUp") {
            e.preventDefault();
            if (currentIndex > 0) {
                currentIndex--;
            } else if (offset > 0) {
                offset -= 5;
                loadProducts(query, offset);
                currentIndex = 4;
            }
            highlightRow();
        }

        // ENTER → Select a product
if (e.key === "Enter") {

    // Quantity field e focus thakle skip
    if ($("#quantity").is(":focus")) return;

    if (currentIndex >= 0 && currentIndex < rows.length) {
        e.preventDefault();

        let selectedProduct = products[currentIndex];
        let pname = selectedProduct.name;

        // 🔥 DUPLICATE CHECK
        let duplicate = false;
        $("#selectedMedicineList tr").each(function () {
            let existingName = $(this).find("td:eq(1)").text().trim();
            if (existingName === pname) {
                duplicate = true;
            }
        });

        if (duplicate) {
            alert("❌ This product is already selected!");
            return; // stop executing
        }

        // If not duplicate → allow selection
        $("#productSearch").val(selectedProduct.name);
        $("#price").val(selectedProduct.cp);
        $("#quantity").focus();
    }
}

    });
    
    // Mouse click handler
$(document).on("click", "#medicineListTableBody tr", function () {
    let index = $(this).data("index");
    if (index === undefined) return;

    let selectedProduct = products[index];
    let pname = selectedProduct.name;

    // 🔥 DUPLICATE CHECK
    let duplicate = false;
    $("#selectedMedicineList tr").each(function () {
        let existingName = $(this).find("td:eq(1)").text().trim();
        if (existingName === pname) duplicate = true;
    });

    if (duplicate) {
        alert("❌ This product is already selected!");
        // Clear product field and keep focus
        $("#productSearch").val("").focus();
        return; // stop execution
    }

    // Not duplicate → fill product
    $("#medicineListTableBody tr").removeClass("selected-row");
    $(this).addClass("selected-row");

    currentIndex = index;

    $("#productSearch").val(selectedProduct.name);
    $("#price").val(selectedProduct.cp);
    $("#quantity").focus();
});

// Keyboard Enter handler
// $(document).on("keydown", function (e) {
//     let rows = $("#medicineListTableBody tr");
//     if (rows.length === 0) return;

//     // Arrow navigation...
//     if (e.key === "ArrowDown") { e.preventDefault(); currentIndex = Math.min(currentIndex + 1, rows.length - 1); highlightRow(); }
//     if (e.key === "ArrowUp") { e.preventDefault(); currentIndex = Math.max(currentIndex - 1, 0); highlightRow(); }

//     if (e.key === "Enter") {
//         if ($("#quantity").is(":focus")) return;

//         if (currentIndex >= 0 && currentIndex < rows.length) {
//             e.preventDefault();

//             let selectedProduct = products[currentIndex];
//             let pname = selectedProduct.name;

//             // 🔥 DUPLICATE CHECK
//             let duplicate = false;
//             $("#selectedMedicineList tr").each(function () {
//                 let existingName = $(this).find("td:eq(1)").text().trim();
//                 if (existingName === pname) duplicate = true;
//             });

//             if (duplicate) {
//                 alert("❌ This product is already selected!");
//                 // Clear product field and keep focus
//                 $("#productSearch").val("").focus();
//                 return;
//             }

//             $("#productSearch").val(selectedProduct.name);
//             $("#price").val(selectedProduct.cp);
//             $("#quantity").focus();
//         }
//     }
// });


    // ENTER in quantity field → Add item
$("#quantity").on("keydown", function (e) {
    if (e.key === "Enter") {
        e.preventDefault();
        e.stopPropagation();

        let pname = $("#productSearch").val().trim();
        let price = parseFloat($("#price").val()) || 0;
        let qty   = parseFloat($("#quantity").val()) || 0;
        let total = parseFloat($("#total").val()) || 0;

        $("#productSearch").focus();

        if(!pname || price <= 0 || qty <= 0 || total <= 0){
            alert("Please select a product and enter quantity correctly.");
            return;
        }

        addToSelectedList(pname, price, qty, total);
    }
});

function updateGrandTotal() {
    let total = 0;

    $("#selectedMedicineList tr").each(function () {
        let rowTotal = parseFloat($(this).find(".item-total").text()) || 0;
        total += rowTotal;
    });

    $("#grandTotal").text(total.toFixed(2));
}

$(document).on("click", ".deleteRow", function () {
    $(this).closest("tr").remove();
    updateGrandTotal();
    updateSelectedTotal();
    updateInvoiceSummary();
});
 $("#discount, #advanced").on("input", function () {
    updateInvoiceSummary();
});

    loadProducts();
});

function updateInvoiceSummary() {
    let invoiceAmount = 0;

    // Sum row totals
    $("#selectedMedicineList tr").each(function () {
        let rowTotal = parseFloat($(this).find("td:eq(4)").text()) || 0;
        invoiceAmount += rowTotal;
    });

    let discountPercent = parseFloat($("#discount").val()) || 0;
    let advance = parseFloat($("#advanced").val()) || 0;

    // Calculate discount amount (percentage)
    let discountAmount = (invoiceAmount * discountPercent) / 100;

    // Net amount after discount
    let netAmount = invoiceAmount - discountAmount;
    if (netAmount < 0) netAmount = 0;

    // Balance after advance
    let balance = netAmount - advance;
    if (balance < 0) balance = 0;

    // Set values
    $("#invoiceAmount").val(invoiceAmount.toFixed(2));
    $("#netAmount").val(netAmount.toFixed(2));
    $("#balance").val(balance.toFixed(2));
}

$("#perPage").on("change", function(){
    let per_page = $(this).val();

    // Get current filters if you have search/status/date inputs
    let search = $("#searchInput").val() || "";
    let status = $("#statusFilter").val() || "";
    let start_date = $("#startDate").val() || "";
    let end_date = $("#endDate").val() || "";

    $.ajax({
        url: "/medicine/",
        type: "GET",
        data: {
            per_page: per_page,
            search: search,
            status: status,
            start_date: start_date,
            end_date: end_date,
        },
        dataType: "html",
        success: function(res){
            // Replace table body and pagination
            $("#medicineTable tbody").html($(res).find("#medicineTable tbody").html());
            $("#pagination").html($(res).find("#pagination").html());
        }
    });
});

function loadSuppliers(selectedId = null) {
    $.get("/get_suppliers/", function (res) {
        let options = `<option value="">Select Supplier</option>`;

        res.suppliers.forEach(s => {
            options += `
                <option value="${s.id}" ${s.id == selectedId ? "selected" : ""}>
                    ${s.name}
                </option>
            `;
        });

        $("#supplier").html(options);
    });
}

// function openEditModal(tran_id){
//     $.get("/transaction/get/"+tran_id, function(res){

//         if(!res.success){ alert(res.message); return; }

//         let m = res.main;

//         $("#edit_tran_id").val(m.tran_id);
//         $("#edit_supplier").val(m.supplier);
//         $("#edit_store").val(m.store_id);
//         $("#edit_payment_method").val(m.tran_method);
//         $("#edit_invoiceAmount").val(m.bill_amount);
//         $("#edit_discount").val(m.discount);
//         $("#edit_netAmount").val(m.net_amount);
//         $("#edit_advanced").val(m.payment);
//         $("#edit_balance").val(m.due);

//         $("#edit_selectedMedicineList").html("");

//         let sl = 1;
//         res.products.forEach(p=>{
//             $("#edit_selectedMedicineList").append(`
//                 <tr>
//                     <td>${sl++}</td>
//                     <td>${p.name}</td>
//                     <td>${p.qty}</td>
//                     <td>${p.price}</td>
//                     <td>${p.total}</td>
//                     <td></td>
//                 </tr>
//             `);
//         });

//         $("#verifyModal").modal("show");
//     });
// }