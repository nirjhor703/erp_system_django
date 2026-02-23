$(document).ready(function () {

    $('#addMedicineModal').on('shown.bs.modal', function () {
        $("#productSearch").focus();
    });

    let products = [];
    let currentIndex = 0;
    let offset = 0;
    let query = "";
    let selectedProduct = null;

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
                    <td>${p.id}</td>
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

    selectedProduct = products[index]; // ✅ remove 'let'
    let pname = selectedProduct.name;

    // Duplicate check
    let duplicate = false;
    $("#selectedMedicineList tr").each(function () {
        let existingId = $(this).find("td:eq(1)").text().trim();
        if (existingId == selectedProduct.id) duplicate = true;
    });

    if (duplicate) {
        alert("❌ This product is already selected!");
        $("#productSearch").val("").focus();
        return;
    }

    // Fill fields
    $("#medicineListTableBody tr").removeClass("selected-row");
    $(this).addClass("selected-row");

    currentIndex = index;

    $("#tran_id").val(selectedProduct.id);
    $("#productSearch").val(selectedProduct.name);
    $("#price").val(selectedProduct.cp);
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
    function addToSelectedList(pid, pname, price, qty, total) {
        let row = `
            <tr>
                <td>${$("#selectedMedicineList tr").length + 1}</td>
                <td>${pid}</td>
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
        updateInvoiceSummary(); 
    });

    // Function to calculate bottom total
    function updateSelectedTotal() {
        let total = 0;

        $("#selectedMedicineList tr").each(function () {
            let qty = parseFloat($(this).find("td:eq(3) input").val()) || 0;
            let price = parseFloat($(this).find("td:eq(4)").text()) || 0;
            total += qty * price;
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
    if ($("#quantity").is(":focus")) return;

    if (currentIndex >= 0 && currentIndex < rows.length) {
        e.preventDefault();

        // Use top-level variable
        selectedProduct = products[currentIndex];
        if (!selectedProduct) return;

        let pname = selectedProduct.name;

        // Duplicate check
        let duplicate = false;
        $("#selectedMedicineList tr").each(function () {
            let existingId = $(this).find("td:eq(1)").text().trim(); // td 1 = product ID
            if (existingId == selectedProduct.id) duplicate = true;
        });


        if (duplicate) {
            alert("❌ This product is already selected!");
            return;
        }

        $("#productSearch").val(selectedProduct.name);
        $("#price").val(selectedProduct.cp);
        $("#tran_id").val(selectedProduct.id);
        $("#quantity").focus();
    }
}

    });

    // Mouse click handler
    // $(document).on("click", "#medicineListTableBody tr", function () {
    //     let index = $(this).data("index");
    //     if (index === undefined) return;

    //     let selectedProduct = products[index];
    //     let pname = selectedProduct.name;

    //     // 🔥 DUPLICATE CHECK
    //     let duplicate = false;
    //     $("#selectedMedicineList tr").each(function () {
    //         let existingId = $(this).find("td:eq(1)").text().trim(); // td 1 = product ID
    //         if (existingId == selectedProduct.id) duplicate = true; // use selectedProduct.id
    //     });



    //     if (duplicate) {
    //         alert("❌ This product is already selected!");
    //         // Clear product field and keep focus
    //         $("#productSearch").val("").focus();
    //         return; // stop execution
    //     }

    //     // Not duplicate → fill product
    //     $("#medicineListTableBody tr").removeClass("selected-row");
    //     $(this).addClass("selected-row");

    //     currentIndex = index;

    //     $("#tran_id").val(selectedProduct.id);
    //     $("#productSearch").val(selectedProduct.name);
    //     $("#price").val(selectedProduct.cp);
    //     $("#quantity").focus();
    // });

$("#quantity").on("keydown", function (e) {
    if (e.key === "Enter") {
        e.preventDefault();
        e.stopPropagation();

        if (!selectedProduct) return;

        let pid = selectedProduct.id;
        let pname = selectedProduct.name;

        // 🔥 IMPORTANT FIX
        let priceVal = $("#price").val().trim();

        // Only validate if price field is EMPTY
        if (priceVal === "") {
            alert("Please enter cost price for this product");
            $("#price").focus();
            return;
        }

        let price = parseFloat(priceVal);
        let qty = parseFloat($("#quantity").val());

        if (!qty || qty <= 0) {
            alert("Invalid quantity");
            return;
        }

        let total = qty * price;

        addToSelectedList(pid, pname, price, qty, total);

        $("#quantity").val("");
        $("#total").val("");
        $("#productSearch").val("").focus();

        selectedProduct = null;
    }
});
$("#addProductBtn").on("click", function () {

    if (!selectedProduct) return;

    let pid = selectedProduct.id;
    let pname = selectedProduct.name;

    let priceVal = $("#price").val().trim();

    

    let price = parseFloat(priceVal);
    let qty = parseFloat($("#quantity").val());

    if (!qty || qty <= 0) {
        alert("Invalid quantity");
        return;
    }

    let total = qty * price;

    addToSelectedList(pid, pname, price, qty, total);

    $("#quantity").val("");
    $("#total").val("");
    $("#productSearch").val("").focus();

    selectedProduct = null;
});



// When user presses Enter in the cost price field
$("#price").on("keydown", function (e) {
    if (e.key === "Enter") {
        e.preventDefault();
        e.stopPropagation();

        let priceVal = $(this).val().trim();

        if (priceVal === "" || parseFloat(priceVal) <= 0) {
            alert("Please enter a valid cost price");
            $(this).focus();
            return;
        }

        selectedProduct.cp = parseFloat(priceVal);

        $("#quantity").focus();
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

// delete_row.js
$(document).off("click", ".deleteRow").on("click", ".deleteRow", function () {
    let tranId = $(this).data("tran-id");
    if (!tranId) return;

    if (!confirm("Are you sure to delete this transaction?")) return;

    $.ajax({
        url: `/transaction/delete/${tranId}/`,
        type: "POST",
        data: { csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val() },
        success: function (res) {
            if (res.success) {
                // Remove the row from table immediately
                $(`#row-${tranId}`).remove();
                alert("Transaction deleted successfully!");
            } else {
                alert(res.error || "Delete failed!");
            }
        },
        error: function () {
            alert("Server error!");
        }
    });
});

// $(document).off("click", ".deleteRow.unverified").on("click", ".deleteRow.unverified", function () {
//     let tranId = $(this).data("tran-id");
//     if (!tranId) return;

//     if (!confirm("Are you sure to delete this transaction?")) return;

//     $.ajax({
//         url: `/transaction/delete/${tranId}/`,
//         type: "POST",
//         data: { csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val() },
//         success: function (res) {
//             if (res.success) {
//                 // Remove the row from table immediately
//                 $(`#row-${tranId}`).remove();
//                 alert("Transaction deleted successfully!");
//             } else {
//                 alert(res.error || "Delete failed!");
//             }
//         },
//         error: function () {
//             alert("Server error!");
//         }
//     });
// });

//     // 🔹 DELETE VERIFIED
//     $(document).off("click", ".deleteRow.verified").on("click", ".deleteRow.verified", function () {
//         let main_id = $(this).data("main-id");
//         if (!main_id) return;

//         if (!confirm("Are you sure to delete this verified transaction?")) return;

//         $.ajax({
//             url: `/transaction-main/delete/${main_id}/`,
//             type: "POST",
//             data: { csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val() },
//             success: function (res) {
//                 if (res.success) {
//                     setTimeout(() => {
//                     window.location.href = "?page=" + res.last_page;
//                 }, 800);
//                     $(`#row-${main_id}`).remove();
//                     alert("Verified transaction deleted!");
//                 } else {
//                     alert(res.error || "Delete failed!");
//                 }
//             },
//             error: function () {
//                 alert("Server error!");
//             }
//         });
//     });















function updateInvoiceSummary() {
    let invoiceAmount = 0;

    $("#selectedMedicineList tr").each(function () {
        let rowTotal = parseFloat($(this).find("td:eq(5)").text()) || 0;
        invoiceAmount += rowTotal;
    });

    let discountPercent = parseFloat($("#discount").val()) || 0;
    let advance = parseFloat($("#advanced").val()) || 0;

    let discountAmount = (invoiceAmount * discountPercent) / 100;
    let netAmount = invoiceAmount - discountAmount;
    if (netAmount < 0) netAmount = 0;

    let balance = netAmount - advance;
    if (balance < 0) balance = 0;

    $("#invoiceAmount").val(invoiceAmount.toFixed(2));
    $("#netAmount").val(netAmount.toFixed(2));
    $("#balance").val(balance.toFixed(2));
}

// 🔥 DISCOUNT change হলে auto recalc
$("#discount").on("input keyup change", function () {
    updateInvoiceSummary();
});

// 🔥 ADVANCE change হলে auto recalc
$("#advanced").on("input keyup change", function () {
    updateInvoiceSummary();
});


$("#perPage").on("change", function () {
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
        success: function (res) {
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
});
