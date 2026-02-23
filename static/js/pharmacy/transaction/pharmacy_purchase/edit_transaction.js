$(document).ready(function () {

    // ================================
    // GLOBALS
    // ================================
    let editProducts = [];
    let editIndex = 0;
    let editOffset = 0;
    let editQuery = "";
    let editSelectedProduct = null;

    // ================================
    // OPEN EDIT MODAL
    // ================================
    $(document).on("click", ".editBtn", function () {
        let tranId = $(this).data("tran-id");
        if (!tranId) return;

        $.get(`/transaction-main/get/?id=${tranId}`, function (res) {
            if (!res.success) {
                alert("Transaction not found!");
                return;
            }

            let d = res.data;

            // Pre-fill main fields
            $("#edit_tran_id_main").val(tranId);
            $("#edit_location").val(d.location || "");
            $("#edit_store").val(d.store_id || "");
            $("#edit_date").val(d.tran_date?.split("T")[0] || "");
            $("#edit_supplier").val(d.supplier || "");
            $("#edit_payment_method").val(d.tran_method || "");
            $("#edit_invoiceAmount").val(d.bill_amount || 0);
            $("#edit_discount").val(d.discount || 0);
            $("#edit_netAmount").val(d.net_amount || 0);
            $("#edit_advanced").val(d.payment || 0);
            $("#edit_balance").val(d.due || 0);

            // Pre-fill selected products
            let html = "";
            (d.details || []).forEach((med, i) => {
            html += `
                <tr>
                    <td>${i + 1}</td>
                    <td>
                        ${med.tran_head_id}
                        <input type="hidden" class="med-pid" value="${med.tran_head_id}">
                    </td>
                    <td><input class="form-control med-name" value="${med.name}" readonly></td>
                    <td><input type="number" class="form-control med-qty" value="${med.qty}"></td>
                    <td><input type="number" class="form-control med-cp" value="${med.cp}"></td>
                    <td><input type="number" class="form-control med-total" value="${med.total}" readonly></td>
                    <td><button class="btn btn-danger btn-sm removeRow">Remove</button></td>
                </tr>`;
        });

            $("#edit_selectedMedicineList").html(html);

            // Load product list for search
            loadEditProducts();

            // Show modal
            new bootstrap.Modal(document.getElementById("editMedicineModal")).show();
        });
    });

    // ================================
    // MODAL SHOWN → FOCUS SEARCH
    // ================================
    $('#editMedicineModal').on('shown.bs.modal', function () {
        $("#edit_productSearch").focus();
    });

    // ===========================
    // VARIABLES
    // ===========================
    let products = [];
    let currentIndex = 0;
    let offset = 0;
    let query = "";
   

    // ===========================
    // LOAD PRODUCTS
    // ===========================
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

                renderEditTable();
                highlightRow();
            }
        });
    }

function renderEditTable() {
    let html = "";

    products.forEach((p, i) => {
        html += `
            <tr data-index="${i}">
                <td>${i + 1}</td>     <!-- Serial -->
                <td>${p.id}</td>      <!-- ID -->
                <td>${p.name}</td>
                <td>${p.manufacturer || ""}</td>
                <td>${p.form || ""}</td>
                <td>${p.quantity || 0}</td>
                <td>${p.cp || 0}</td>
                <td>${p.mrp || 0}</td>
            </tr>
        `;
    });

    $("#edit_medicineListTableBody").html(html);
}

    function highlightRow() {
        let rows = $("#edit_medicineListTableBody tr");
        rows.removeClass("selected-row");

        if (currentIndex >= 0 && currentIndex < rows.length) {
            let row = $(rows[currentIndex]);
            row.addClass("selected-row");
            row[0].scrollIntoView({ behavior: "smooth", block: "center" });
        }
    }

    // ===========================
    // PRODUCT SEARCH INPUT
    // ===========================
    $("#edit_productSearch").on("input", function () {
        query = $(this).val();
        offset = 0;
        loadProducts(query, offset);
    });

    // ===========================
    // SELECT PRODUCT BY CLICK
    // ===========================
    $(document).on("click", "#edit_medicineListTableBody tr", function () {
        let index = $(this).data("index");
        if (index === undefined) return;

        editSelectedProduct = products[index];
        currentIndex = index;

        // DUPLICATE CHECK
        let duplicate = false;
        $("#edit_selectedMedicineList tr").each(function () {
            let existingId = $(this).find("td:eq(1)").text().trim();
            if (existingId == editSelectedProduct.id) duplicate = true;
        });

        if (duplicate) {
            alert("❌ This product is already selected!");
            $("#edit_productSearch").val("").focus();
            return;
        }

        $("#edit_medicineListTableBody tr").removeClass("selected-row");
        $(this).addClass("selected-row");

        $("#edit_tran_id").val(editSelectedProduct.id);
        $("#edit_productSearch").val(editSelectedProduct.name);
        $("#edit_price").val(editSelectedProduct.cp);
        $("#edit_mrp").val(editSelectedProduct.mrp);
        $("#edit_quantity").focus();
    });

    // ===========================
    // SELECT PRODUCT BY KEYBOARD
    // ===========================
    $(document).on("keydown", function (e) {
        let rows = $("#edit_medicineListTableBody tr");
        if (rows.length === 0) return;

        if (e.key === "ArrowDown") {
            e.preventDefault();
            if (currentIndex < rows.length - 1) currentIndex++;
            else {
                offset += 5;
                loadProducts(query, offset, true);
                currentIndex++;
            }
            highlightRow();
        }

        if (e.key === "ArrowUp") {
            e.preventDefault();
            if (currentIndex > 0) currentIndex--;
            else if (offset > 0) {
                offset -= 5;
                loadProducts(query, offset);
                currentIndex = 4;
            }
            highlightRow();
        }

        if (e.key === "Enter") {
            if ($("#edit_quantity").is(":focus")) return;
            if (currentIndex >= 0 && currentIndex < rows.length) {
                e.preventDefault();
                editSelectedProduct = products[currentIndex];

                // DUPLICATE CHECK
                let duplicate = false;
                $("#edit_selectedMedicineList tr").each(function () {
                    let existingId = $(this).find("td:eq(1)").text().trim();
                    if (existingId == editSelectedProduct.id) duplicate = true;
                });

                if (duplicate) {
                    alert("❌ This product is already selected!");
                    $("#edit_productSearch").val("").focus();
                    return;
                }

                $("#edit_productSearch").val(editSelectedProduct.name);
                $("#edit_price").val(editSelectedProduct.cp);
                $("#edit_tran_id").val(editSelectedProduct.id);
                $("#edit_quantity").focus();
            }
        }
    });

    // ===========================
    // PRICE × QTY CALCULATION
    // ===========================
    $("#edit_quantity").on("input", function () {
        let quantity = parseFloat($(this).val()) || 0;
        let price = parseFloat($("#edit_price").val()) || 0;
        $("#edit_total").val((quantity * price).toFixed(2));
    });

    // ===========================
    // ADD PRODUCT TO SELECTED LIST
    // ===========================
    function addToSelectedList(pid, pname, price, qty, total) {
        let row = `
            <tr>
                <td>${$("#edit_selectedMedicineList tr").length + 1}</td>
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
        $("#edit_selectedMedicineList").append(row);

        // Clear input fields
        $("#edit_productSearch").val("");
        $("#edit_price").val("");
        $("#edit_quantity").val("");
        $("#edit_total").val("");

        updateInvoiceSummary();
    }

    $(document).on("click", "#edit_addProductBtn", function () {
        if (!editSelectedProduct) {
            alert("Select a product first!");
            return;
        }

        let pid = editSelectedProduct.id;
        let pname = editSelectedProduct.name;
        let price = parseFloat($("#edit_price").val()) || 0;
        let qty = parseFloat($("#edit_quantity").val()) || 0;
        let total = parseFloat($("#edit_total").val()) || 0;

        if (price <= 0 || qty <= 0) {
            alert("Invalid price or quantity!");
            return;
        }

        // DUPLICATE CHECK
        let duplicate = false;
        $("#edit_selectedMedicineList tr").each(function () {
            let existingId = $(this).find("td:eq(1)").text().trim();
            if (existingId == pid) duplicate = true;
        });

        if (duplicate) {
            alert("❌ This product is already selected!");
            return;
        }

        addToSelectedList(pid, pname, price, qty, total);
        editSelectedProduct = null;
    });

    // REMOVE ITEM
    $(document).on("click", ".remove-item", function () {
        $(this).closest("tr").remove();
        $("#edit_selectedMedicineList tr").each(function (i) {
            $(this).find("td:first").text(i + 1);
        });
        updateInvoiceSummary();
    });

    // ===========================
    // INVOICE CALCULATION
    // ===========================
    function updateInvoiceSummary() {
        let invoiceAmount = 0;
        $("#edit_selectedMedicineList tr").each(function () {
            let rowTotal = parseFloat($(this).find("td:eq(5)").text()) || 0;
            invoiceAmount += rowTotal;
        });

        let discountPercent = parseFloat($("#edit_discount").val()) || 0;
        let advance = parseFloat($("#edit_advanced").val()) || 0;

        let discountAmount = (invoiceAmount * discountPercent) / 100;
        let netAmount = invoiceAmount - discountAmount;
        if (netAmount < 0) netAmount = 0;

        let balance = netAmount - advance;
        if (balance < 0) balance = 0;

        $("#edit_invoiceAmount").val(invoiceAmount.toFixed(2));
        $("#edit_netAmount").val(netAmount.toFixed(2));
        $("#edit_balance").val(balance.toFixed(2));
    }

    $("#edit_discount, #edit_advanced").on("input keyup change", function () {
        updateInvoiceSummary();
    });

    // ===========================
    // AUTOLOAD EXISTING TRANSACTION
    // ===========================
    function loadTransaction(tran_id) {
        $.get(`/transaction/get/${tran_id}/`, function (res) {
            if (res.success) {
                const t = res.transaction;
                $("#edit_location").val(t.location);
                $("#edit_store").val(t.store_id);
                $("#edit_date").val(t.date);
                $("#edit_supplier").val(t.supplier);
                $("#edit_payment_method").val(t.tran_method);
                $("#edit_tran_id").val(t.tran_head);

                // Load products
                $("#edit_selectedMedicineList").html("");
                t.medicines.forEach((p, i) => {
                    addToSelectedList(p.tran_head_id, p.name, p.cp, p.qty, p.total);
                });

                $("#edit_discount").val(t.discount);
                $("#edit_advanced").val(t.payment);
                updateInvoiceSummary();
            } else {
                alert(res.message || "Failed to load transaction!");
            }
        });
    }

    // ===========================
    // UPDATE TRANSACTION
    // ===========================
    $("#UpdateBtn").on("click", function () {
        let store = $("#edit_store").val();
        let location = $("#edit_location").val().trim();
        let supplier = $("#edit_supplier").val().trim();
        let method = $("#edit_payment_method").val();
        let tran_head = $("#edit_tran_id").val();

        let invoice = parseFloat($("#edit_invoiceAmount").val()) || 0;
        let discount = parseFloat($("#edit_discount").val()) || 0;
        let net = parseFloat($("#edit_netAmount").val()) || 0;
        let advance = parseFloat($("#edit_advanced").val()) || 0;
        let balance = parseFloat($("#edit_balance").val()) || 0;

        let quantity = 0;
        $("#edit_selectedMedicineList tr").each(function () {
            let qty = parseFloat($(this).find("td:eq(3)").text()) || 0;
            quantity += qty;
        });

        // VALIDATION
        if (isNaN(quantity) || quantity <= 0) { alert("Please enter valid quantity"); return; }
        if (!store) { alert("Please select a store."); return; }
        if (!location) { alert("Please enter location."); $("#edit_location").focus(); return; }
        if (!supplier) { alert("Please enter supplier."); $("#edit_supplier").focus(); return; }
        if (!method) { alert("Please select payment method."); return; }
        if (invoice <= 0) { alert("Invoice amount must be greater than 0."); return; }
        if (discount < 0 || discount > 100) { alert("Discount must be between 0–100%"); return; }
        if (net <= 0) { alert("Net amount is invalid."); return; }
        if (advance < 0) { alert("Advance cannot be negative."); return; }
        if (balance < 0) { alert("Balance cannot be negative."); return; }

        // Prepare medicines array
        let medicines = [];
        $("#edit_selectedMedicineList tr").each(function () {
            let pid = $(this).find("td:eq(1)").text();
            let pname = $(this).find("td:eq(2)").text();
            let qty = parseFloat($(this).find("td:eq(3)").text()) || 0;
            let price = parseFloat($(this).find("td:eq(4)").text()) || 0;
            let total = parseFloat($(this).find("td:eq(5)").text()) || 0;
            medicines.push({ tran_head_id: pid, name: pname, qty: qty, cp: price, total: total });
        });

        const data = {
            store_id: store,
            location: location,
            supplier: supplier,
            tran_type: 1,
            tran_head: tran_head,
            tran_method: method,
            bill_amount: invoice,
            discount: discount,
            net_amount: net,
            payment: advance,
            due: balance,
            quantity: quantity,
            medicines: JSON.stringify(medicines),
            csrfmiddlewaretoken: "{{ csrf_token }}"
        };

        $.ajax({
            url: "/transaction/temp/update/",
            type: "POST",
            data: data,
            success: function(res){
                if(res.success){
                    alert("Transaction Updated!\nTran ID: " + res.tran_id);
                    $('#editMedicineModal').modal('hide');
                    setTimeout(() => { window.location.reload(); }, 800);
                } else {
                    alert(res.message || "Something went wrong!");
                }
            },
            error: function(xhr){
                console.error(xhr.responseText);
                alert("Something went wrong!");
            }
        });
    });

});


 
