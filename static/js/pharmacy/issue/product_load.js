$(document).ready(function () {

    // $('#addMedicineModal').on('shown.bs.modal', function () {
    //     $("#productSearch").focus();
    // });

    let products = [];    
    let currentIndex = 0;
    let currentRequest = null;
    let offset = 0;
    let query = "";
    let isLoading = false;
    let limit = 50;
    let isPOMode = false;

    function loadProducts(q = "", newOffset = 0, append = false) {

        if (isLoading) return;

        // 🛑 Abort previous request
        if (currentRequest) {
            currentRequest.abort();
        }

        isLoading = true;
        // currentIndex = 0;

        currentRequest = $.ajax({
            url: "/product-search/",
            method: "GET",
            data: { q: q, offset: newOffset },
            success: function (response) {

                let fetched = response.results || [];

                if (append) {
                    products = products.concat(fetched);
                } else {
                    products = fetched;
                    offset = newOffset;
                    
                    // ✅ Reset ONLY if this is new search
                    if (newOffset === 0) {
                        currentIndex = 0;
                    }
                }

                renderTable();
                isLoading = false;
                $('#productSearch').focus();
            },
            error: function (xhr, status) {
                if (status !== "abort") {
                    console.error("AJAX Error:", status);
                }
                isLoading = false;
            }
        });
    }    

    function renderTable() {
        let html = "";
        products.forEach((p, i) => {  
            html += `
                <tr data-index="${i}"
                    tabindex="0"
                    class="${i === currentIndex ? 'table-active' : ''}">
                    <td>${i + 1}</td>
                    <td>${p.name}</td>
                    <td>${p.category_name}</td>
                    <td>${p.manufacturer}</td>
                    <td>${p.form}</td>
                    <td>${p.quantity}</td>
                    <td>${p.cp}</td>
                    <td>${p.mrp}</td>
                    <td>${p.id}</td>
                </tr>
            `;
        });
        $("#medicineListTableBody").html(html);
        scrollToActiveRow();
    }

    
    function scrollToActiveRow() {
        let $activeRow = $("#medicineListTableBody tr.table-active");

        if ($activeRow.length) {
            $activeRow[0].scrollIntoView({
                block: "nearest"
            });
        }
    }    
  
    let typingTimer;
    let typingDelay = 300; // 300ms delay
    $("#productSearch").on("input", function () {

        clearTimeout(typingTimer);

        let value = $(this).val().trim();

        typingTimer = setTimeout(function () {

            query = value;
            offset = 0;

            loadProducts(query, offset, false);

        }, typingDelay);

    });


    $(document).on("keydown", function (e) {

        if (products.length === 0) return;

        if (e.key === "ArrowDown") {
            e.preventDefault();

            if (currentIndex < products.length - 1) {
                currentIndex++;
                updateHighlight();
            }

            if (currentIndex >= products.length - 5) {
                offset += limit;
                loadProducts(query, offset, true);
            }
        }

        if (e.key === "ArrowUp") {
            e.preventDefault();

            if (currentIndex > 0) {
                currentIndex--;
                updateHighlight();
            }
        }

    });

 
    // $(document).on("keydown", function (e) {

    //     if (e.key !== "Enter") return;

    //     if ($('#productSearch, #quantity, #addProductBtn').is(':focus')) return;

    //     // If products not loaded → do nothing
    //     if (products.length === 0) return;

    //     // If Enter pressed inside search AND no row selected yet
    //     if ($("#productSearch").is(":focus") && currentIndex === 0) {
    //         // Allow selection of first row
    //         e.preventDefault();
    //     }

    //     // If a valid row is selected
    //     if (currentIndex >= 0 && currentIndex < products.length) {

    //         e.preventDefault();

    //         let selectedProduct = products[currentIndex];
    //         if (!selectedProduct) return;

    //         $("#productSearch").val(selectedProduct.name);
    //         $("#productid").val(selectedProduct.id);
    //         $("#cp").val(selectedProduct.cp);
    //         $("#mrp").val(selectedProduct.mrp);
    //         // Focus quantity AFTER current event loop
    //         setTimeout(function() {
    //             $("#quantity").focus().select();
    //         }, 0);
    //     }
    // });    

    // When Enter pressed in #productSearch
    $('#productSearch').on('keydown', function(e) {
        if (e.key === "Enter") {
            e.preventDefault();

            if (products.length === 0) return;

            let selectedProduct = products[currentIndex];
            if (!selectedProduct) return;

            $(this).val(selectedProduct.name);
            $("#productid").val(selectedProduct.id);
            $("#cp").val(selectedProduct.cp);
            $("#mrp").val(selectedProduct.mrp);

            // Focus quantity after current event
            setTimeout(function() {
                $("#quantity").focus().select();
            }, 0);
        }
    });

    // When Enter pressed in #quantity → focus Add button
    $('#quantity').on('keydown', function(e) {
        if (e.key === "Enter") {
            e.preventDefault();
            setTimeout(function() {
                $("#addProductBtn").focus();
            }, 0);
        }
    });

    // When Enter pressed on Add button → trigger click
    $('#addProductBtn').on('keydown', function(e) {
        if (e.key === "Enter") {
            e.preventDefault();
            $(this).click();
        }
    });

    

$("#addProductBtn").off("click").on("click", function () {

    let productId = $('#productid').val().trim();
    let name = $('#productSearch').val().trim();
    let qty = Number($('#quantity').val().trim());
    let cp = Number($('#cp').val().trim());
    let mrp = Number($('#mrp').val().trim());

    let total = qty * cp;

    let existingRow = $(this).data("editRow");

    // VALIDATION
    if (!name) {
        alert("⚠️ Please enter product name!");
        return;
    }

    if (isNaN(qty) || qty <= 0) {
        alert("⚠️ Invalid quantity!");
        return;
    }

    if (isNaN(cp) || cp <= 0) {
        alert("⚠️ Invalid CP!");
        return;
    }

    if (isNaN(mrp) || mrp <= 0) {
        alert("⚠️ Invalid MRP!");
        return;
    }

    // ✏️ EDIT MODE
    if (existingRow) {

        existingRow.find("td:eq(1)").text(name);
        existingRow.find("td:eq(2)").text(qty);
        existingRow.find("td:eq(3)").text(cp);
        existingRow.find(".mrp-col").text(mrp);
        existingRow.find(".row-total").text(total.toFixed(2));

        $(this).removeData("editRow");

    } else {

        // ➕ ADD MODE
        addToSelectedList(
            name,
            cp,
            mrp,
            qty,
            total,
            productId,
            null,
            null
        );
    }

    // clear
    $("#productSearch").val("");
    $("#cp").val("");
    $("#mrp").val("");
    $("#quantity").val("");

    updateSelectedTotal();
    updateInvoiceSummary();

    $('#productSearch').focus();
});

    

    function updateHighlight() {

        let rows = $("#medicineListTableBody tr");

        rows.removeClass("table-active");

        if (currentIndex >= 0 && currentIndex < rows.length) {

            let $row = rows.eq(currentIndex);

            $row.addClass("table-active");

            $row[0].scrollIntoView({
                block: "nearest"
            });
        }
    }

    $(document).on("click", "#medicineListTableBody tr", function () {

        // Remove previous highlight
        $("#medicineListTableBody tr").removeClass("table-active");

        // Highlight clicked row
        $(this).addClass("table-active");

        // Optional: update currentIndex
        currentIndex = $(this).data("index");

    });


    $(document).on("keydown", "#medicineListTableBody tr", function (e) {

        if (e.key === "ArrowDown") {
            e.preventDefault();

            // Move highlight down
            if (currentIndex < products.length - 1) {
                currentIndex++;
                updateHighlight();
                $("#medicineListTableBody tr").eq(currentIndex).focus();
            }

            // 🔥 Load more when reaching last 5 rows
            if (
                currentIndex >= products.length - 5 &&
                !isLoading
            ) {
                offset += limit;
                loadProducts(query, offset, true);
            }
        }

        if (e.key === "ArrowUp") {
            e.preventDefault();

            if (currentIndex > 0) {
                currentIndex--;
                updateHighlight();
                $("#medicineListTableBody tr").eq(currentIndex).focus();
            }
        }

    });

    $(".table-responsive").on("scroll", function () {

        let $this = $(this);

        if ($this.scrollTop() + $this.innerHeight() >= this.scrollHeight - 10) {

            offset += limit;

            loadProducts(query, offset, true);
        }
    });


    //========================================================


    // PRICE × QTY calculation
    $("#quantity").on("input", function () {
        let quantity = parseFloat($(this).val()) || 0;
        let cp = parseFloat($("#cp").val()) || 0;
        let total = quantity * cp;
        $("#total").val(total.toFixed(2));
    });

    $("#cp").on("input", function () {
        let cp = parseFloat($(this).val()) || 0;
        let quantity = parseFloat($("#quantity").val()) || 0;
        let total = quantity * cp;
        $("#total").val(total.toFixed(2));
    });

    // ADD to selected list
function addToSelectedList(pname, cp, mrp, qty, total, productId = null, unitId = null, expiry = null) {
    let row = `
        <tr data-product-id="${productId}" data-unit-id="${unitId}" data-expiry="${expiry}"> 
            <td>${$("#selectedMedicineList tr").length + 1}</td>
            <td>${pname}</td>
            <td>${qty}</td>
            <td>${cp}</td>
            <td class="mrp-col" style="display:none;">${mrp}</td>
            <td style="display:none;">${expiry}</td>
            <td>${total}</td>
            <td>
                <button type="button" class="btn btn-sm btn-primary edit-item">Edit</button>
                <button type="button" class="btn btn-sm btn-danger remove-item">Remove</button>
            </td>
        </tr>
    `;
    $("#selectedMedicineList").append(row);

    // Clear input fields
    $("#productSearch").val("");
    $("#cp").val("");
    $("#mrp").val("");
    $("#quantity").val("");
    $("#total").val("");

    updateSelectedTotal();
    updateInvoiceSummary(); 
}

    // Remove button functionality
    $(document).on("click", ".remove-item", function () {
        // let pname = $(this).closest("tr").find('td:eq(1)').text();

        if (confirm("Are you sure to remove:\n\n" + $(this).closest("tr").find('td:eq(1)').text() + " ?")) {
            $(this).closest("tr").remove();
        }
        // Update SL numbers
        $("#selectedMedicineList tr").each(function (index) {
            $(this).find("td:first").text(index + 1);
        });

        // Update total
        updateSelectedTotal();
    });

    // Function to calculate bottom total
    // function updateSelectedTotal() {
    //     let total = 0;
    //     $("#selectedMedicineList tr").each(function () {
    //         let cp = parseFloat($(this).find("td:eq(3)").text()) || 0;
    //         let qty = parseFloat($(this).find("td:eq(2)").text()) || 0;
    //         total += cp * qty;
    //     });
    //     $("#bottomTotal").text(total.toFixed(2));
    // }
    function updateSelectedTotal() {
        let total = 0;
        $("#selectedMedicineList tr").each(function () {
            let rowTotal = parseFloat($(this).find("td:eq(6)").text()) || 0; // total column
            total += rowTotal;
        });
        $("#bottomTotal").text(total.toFixed(2));
    }

    // function updateInvoiceSummary() {
    //     let invoiceAmount = 0;

    //     // Sum row totals
    //     $("#selectedMedicineList tr").each(function () {
    //     let rowTotal = parseFloat($(this).find("td:eq(5)").text()) || 0;
    //     invoiceAmount += rowTotal;
    // });

    //     let discountPercent = parseFloat($("#discount").val()) || 0;
    //     let advance = parseFloat($("#advanced").val()) || 0;

    //     // Calculate discount amount (percentage)
    //     let discountAmount = (invoiceAmount * discountPercent) / 100;

    //     // Net amount after discount
    //     let netAmount = invoiceAmount - discountAmount;
    //     if (netAmount < 0) netAmount = 0;

    //     // Balance after advance
    //     let balance = netAmount - advance;
    //     if (balance < 0) balance = 0;

    //     // Set values
    //     $("#invoiceAmount").val(invoiceAmount.toFixed(2));
    //     $("#netAmount").val(netAmount.toFixed(2));
    //     $("#balance").val(balance.toFixed(2));
    // }
    function updateInvoiceSummary() {
    let invoiceAmount = 0;

    // Sum row totals (total column td:eq(6))
    $("#selectedMedicineList tr").each(function () {
        let rowTotal = parseFloat($(this).find("td:eq(6)").text()) || 0;
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

    function updateGrandTotal() {
        let total = 0;

        $("#selectedMedicineList tr").each(function () {
            let rowTotal = parseFloat($(this).find(".item-total").text()) || 0;
            total += rowTotal;
        });

        $("#grandTotal").text(total.toFixed(2));
    }

    // $(document).on("click", ".deleteRow", function () {
    //     alert("Are you sure to remove");
    //     $(this).closest("tr").remove();
    //     updateGrandTotal();
    //     updateSelectedTotal();
    //     updateInvoiceSummary();
    // });

    $("#discount, #advanced").on("input", function () {
        updateInvoiceSummary();
    });

    loadProducts();
});
// get CSRF from cookie
// get CSRF from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
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

$('#saveAllBtnIssue').on('click', function (e) {
    e.preventDefault();

    let purchaseList = [];

    // selected medicines table
    $('#selectedMedicineList tr').each(function () {
        let row = $(this);
        let tranHeadId = row.data('product-id'); // make sure this exists
        if (!tranHeadId) {
            // fallback: try to find it from hidden input or alert
            alert("⚠️ Missing product ID for: " + row.find('td:eq(1)').text());
            return false; // stop saving
        }

        purchaseList.push([
            parseInt(tranHeadId),                          // tran_head_id
            parseFloat(row.find('td:eq(2)').text()) || 0,  // quantity
            parseFloat(row.find('td:eq(3)').text()) || 0,  // cp
            parseFloat(row.find('.mrp-col').text()) || 0,   //mrp
            parseFloat(row.find('td:eq(6)').text()) || 0,  // total amount
            row.data('unit-id') ?? null,      // ✅ FIX HERE
            row.data('expiry') ?? null                   // expiry
        ]);
    });

    if (!purchaseList.length) {
        alert("❌ No products selected!");
        return;
    }

    let payload = {
        store: parseInt($('.store-select').val()) || null,
        location: parseInt($('.location-select').val()) || null,
        supplier: parseInt($('.supplier-select').val()) || null,
        invoice: $('#purchaseinvoice').val(),
        payment_method: $('#payment_method').val(),
        bill_amount: parseFloat($('#invoiceAmount').val()) || 0,
        discount: parseFloat($('#discount').val()) || 0,
        net_amount: parseFloat($('#netAmount').val()) || 0,
        receive: parseFloat($('#advanced').val()) || 0,
        due: parseFloat($('#balance').val()) || 0,
        tran_date: $('#date').val(),
        products: purchaseList
    };

    $.ajax({
        url: "/pharmacy/save-issue/",
        type: "POST",
        headers: { "X-CSRFToken": csrftoken },
        contentType: "application/json",
        data: JSON.stringify(payload),
        success: function (response) {
            alert("✅ Saved Successfully!");
            window.location.href = "/pharmacy/issue-invoice/" + response.tran_id + "/";
            $("#selectedMedicineList").empty();   // clear table
            $('#productSearch').focus();
            console.log(response);
        },
        error: function(xhr){
            console.error(xhr.status, xhr.responseText);
            alert("❌ Save failed! Check console for error.");
        }
    });
});
$(document).ready(function () {

    // ================= MODE SWITCH =================
    $('input[name="mode"]').on('change', function () {

        let mode = $(this).val();

        if (mode === "manual") {
            $("#manualIssueSection").show();
            $("#poSection").hide();
        } else {
            $("#manualIssueSection").hide();
            $("#poSection").show();

            loadPOList(); // 🔥 VERY IMPORTANT
        }

    });

    // ================= LOAD PO LIST =================
function loadPOList() {

    $.ajax({
        url: "/search-po/",
        type: "GET",
        success: function (res) {

            console.log("PO RESPONSE:", res); // 🔥 check browser console

            let html = "";

            (res.results || []).forEach(po => {
                html += `
                    <tr class="po-row" data-id="${po.tran_id}">
                        <td>${po.tran_id}</td>
                        <td>${po.date}</td>
                        <td>${po.client_name}</td>
                        <td>${po.total}</td>
                    </tr>
                `;
            });

            $("#poList").html(html || "<tr><td colspan='3'>No PO found</td></tr>");
        }
    });
}

loadPOList();

    // ================= SEARCH =================
    $("#poSearch").on("input", function () {
        loadPOList($(this).val().trim());
    });

    // ================= CLICK PO =================
$(document).on("click", ".po-row", function () {

    let poId = $(this).data("id");

    $.ajax({
        url: "/get-po-details/",
        type: "GET",
        data: { id: poId },

        success: function (res) {
            isPOMode = true;   // 🔥 MUST be FIRST

            $("#poSection").hide();
            $("#manualIssueSection").show();

    console.log(res);

    $("#poSection").hide();
    $("#manualIssueSection").show();
    $('input[value="manual"]').prop("checked", true);

    // ===== HEADER FILL =====
    $('#purchaseinvoice').val(res.invoice || "");
    $('#payment_method').val(res.payment_method || "cash");
    $('#date').val(res.date ? res.date.split("T")[0] : "");

    // ===== CLEAR TABLE =====
    $("#selectedMedicineList").empty();

    // ===== LOAD PRODUCTS =====
 res.products.forEach((p, i) => {

    let total = (p.qty * p.cp).toFixed(2);

    let row = `
        <tr data-product-id="${p.id}">
            <td>${i + 1}</td>
            <td>${p.name}</td>

            <td class="po-qty" contenteditable="true">${p.qty}</td>

            <td>${p.cp}</td>

            <td class="mrp-col" style="display:none;">${p.mrp}</td>
            <td style="display:none;"></td>

            <td class="row-total">${total}</td>

            <td>
                <button type="button" class="btn btn-sm btn-primary edit-item">Edit</button>
                <button class="btn btn-danger btn-sm remove-item">Remove</button>
            </td>
        </tr>
    `;

    $("#selectedMedicineList").append(row);
});

    updateSelectedTotal();
    updateTotals();
}
    });
});

$(document).on("click", ".edit-item", function () {

    let row = $(this).closest("tr");

    let name = row.find("td:eq(1)").text();
    let qty = row.find("td:eq(2)").text();
    let cp = row.find("td:eq(3)").text();
    let mrp = row.find(".mrp-col").text();

    $("#productSearch").val(name);
    $("#quantity").val(qty);
    $("#cp").val(cp);
    $("#mrp").val(mrp);

    $("#addProductBtn").data("editRow", row);
});

    // ================= QTY EDIT =================
    $(document).on("input", ".po-qty", function () {

    let row = $(this).closest("tr");

    let qty = parseFloat($(this).text().trim()) || 0;
    let cp = parseFloat(row.find("td:eq(3)").text()) || 0;

    let total = qty * cp;

    row.find(".row-total").text(total.toFixed(2));

    updateSelectedTotal();
    updateTotals();
});
$(document).on("click", ".remove-item", function () {
    $(this).closest("tr").remove();
    updateSelectedTotal();
     updateTotals();
});

function updateSelectedTotal() {

    let total = 0;

    $("#selectedMedicineList tr").each(function () {
        let rowTotal = parseFloat($(this).find(".row-total").text()) || 0;
        total += rowTotal;
    });

    $("#bottomTotal").text(total.toFixed(2));
}
    function updateTotals() {
        if (!isPOMode) return;

        let invoiceAmount = 0;

        $("#selectedMedicineList tr").each(function () {
            let rowTotal = parseFloat($(this).find(".row-total").text()) || 0;
            invoiceAmount += rowTotal;
        });

        let discount = parseFloat($("#discount").val()) || 0;
        let advance = parseFloat($("#advanced").val()) || 0;

        let discountAmount = (invoiceAmount * discount) / 100;
        let net = invoiceAmount - discountAmount;
        let balance = net - advance;

        $("#invoiceAmount").val(invoiceAmount.toFixed(2));
        $("#netAmount").val(net.toFixed(2));
        $("#balance").val(balance.toFixed(2));
    }

    $("#discount, #advanced").on("input", updateTotals);

    // ================= INIT LOAD =================
    loadPOList();

});



