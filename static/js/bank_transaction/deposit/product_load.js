$(document).ready(function () {    
    $("#quantity").val(1).prop("readonly", true);
    $("#cp").val(0).prop("readonly", true);
    $("#mrp").val(0).prop("readonly", true);

    $("#total").prop("readonly", false);

    function setTodayDate() {
        const today = new Date();
        const localDate =
            today.getFullYear() + "-" +
            String(today.getMonth() + 1).padStart(2, "0") + "-" +
            String(today.getDate()).padStart(2, "0");

        document.getElementById("tranDate").value = localDate;

        if (document.getElementById("expiryDate")) {
            document.getElementById("expiryDate").value = localDate;
        }
    }

    setTodayDate();    

    let products = [];    
    let currentIndex = 0;
    let currentRequest = null;
    let offset = 0;
    let query = "";
    let isLoading = false;
    let limit = 50;
    let hasMore = true;

    function loadProducts(q = "", newOffset = 0, append = false) {

        if (isLoading) return;
        if (!hasMore && append) return;

        if (currentRequest) {
            currentRequest.abort();
        }

        isLoading = true;

        currentRequest = $.ajax({
            url: "/bank_tran/product-search/",
            method: "GET",
            data: { q: q, offset: newOffset },
            success: function (response) {

                let fetched = response.results || [];

                if (append) {
                    products = products.concat(fetched);
                } else {
                    products = fetched;
                    offset = newOffset;
                    
                    if (newOffset === 0) {
                        currentIndex = 0;
                    }
                }

                hasMore = fetched.length === limit;

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
                    <td>${p.category_name || ""}</td>
                    <td>${p.manufacturer || ""}</td>
                    <td>${p.form || ""}</td>
                    <td>${p.quantity || 0}</td>
                    <td>${p.cp || 0}</td>
                    <td>${p.mrp || 0}</td>
                    <td>${p.id}</td>
                </tr>
            `;
        });
        $("#paymentListTableBody").html(html);
        scrollToActiveRow();
    }

    function scrollToActiveRow() {
        let $activeRow = $("#paymentListTableBody tr.table-active");

        if ($activeRow.length) {
            $activeRow[0].scrollIntoView({
                block: "nearest"
            });
        }
    }    
  
    let typingTimer;
    let typingDelay = 300;

    $("#productSearch").on("input", function () {

        clearTimeout(typingTimer);

        let value = $(this).val().trim();

        typingTimer = setTimeout(function () {

            query = value;
            offset = 0;
            hasMore = true;

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
                if (hasMore && !isLoading) {
                    offset += limit;
                    loadProducts(query, offset, true);
                }
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


    $('#productSearch').on('keydown', function(e) {
        if (e.key === "Enter") {
            e.preventDefault();

            if (products.length === 0) return;

            let selectedProduct = products[currentIndex];
            if (!selectedProduct) return;

            $(this).val(selectedProduct.name);
            $("#productid").val(selectedProduct.id);
            $("#cp").val(selectedProduct.cp || 0);
            $("#mrp").val(selectedProduct.mrp || 0);

            setTimeout(function() {
                $("#total").focus().select();
            }, 0);
        }
    });

    $('#quantity').on('keydown', function(e) {
        if (e.key === "Enter") {
            e.preventDefault();
            setTimeout(function() {
                $("#addProductBtn").focus();
            }, 0);
        }
    });

    $('#total').on('keydown', function(e) {
        if (e.key === "Enter") {
            e.preventDefault();
            setTimeout(function() {
                $("#addProductBtn").focus();
            }, 0);
        }
    });

    $('#addProductBtn').on('keydown', function(e) {
        if (e.key === "Enter") {
            e.preventDefault();
            $(this).click();
        }
    });


    $("#addProductBtn").off("click").on("click", function () {

        let productId = $('#productid').val().trim();
        let name = $('#productSearch').val().trim();

        let qty = 1;
        let cp = 0;
        let mrp = Number($('#mrp').val().trim()) || 0;
        let expiry = $('#expiryDate').val().trim() || null;

        let total = parseFloat($('#total').val()) || 0;

        let bankId = $("#transaction_with").val();
        let bankName = $("#transaction_with option:selected").text().trim();

        let existingRow = $(this).data("editRow");

        if (!productId || !name) {
            alert("⚠️ Please select product name!");
            $('#productSearch').focus();
            return;
        }

        if (!bankId) {
            alert("⚠️ Please select bank!");
            $("#transaction_with").focus();
            return;
        }

        if (total <= 0) {
            alert("⚠️ Please enter valid amount!");
            $("#total").focus().select();
            return;
        }

        if (!existingRow) {
            let duplicate = false;

            $("#selectedPaymentListPayment tr").each(function () {
                if ($(this).data("product-id") == productId && $(this).data("bank-id") == bankId) {
                    duplicate = true;
                    return false;
                }
            });

            if (duplicate) {
                alert("❌ This product with selected bank is already selected!");
                $('#productSearch').focus().select();
                return;
            }
        }

        if (existingRow) {

            existingRow.attr("data-product-id", productId);
            existingRow.attr("data-bank-id", bankId);

            existingRow.find("td:eq(1)").text(name);
            existingRow.find("td:eq(2)").text(bankName);
            existingRow.find("td:eq(3)").text(total.toFixed(2));

            $(this).removeData("editRow");
            $("#addProductBtn").text("Add");

        } else {
            addToSelectedList(productId, name, bankId, bankName, qty, cp, mrp, expiry, total);
        }

        clearInputs();
        updateInvoiceSummary();

        setTimeout(function () {
            $('#productSearch').focus().select();
        }, 100);

    });


    function updateHighlight() {

        let rows = $("#paymentListTableBody tr");

        rows.removeClass("table-active");

        if (currentIndex >= 0 && currentIndex < rows.length) {

            let $row = rows.eq(currentIndex);

            $row.addClass("table-active");

            $row[0].scrollIntoView({
                block: "nearest"
            });
        }
    }

    $(document).on("click", "#paymentListTableBody tr", function () {

        $("#paymentListTableBody tr").removeClass("table-active");

        $(this).addClass("table-active");

        currentIndex = $(this).data("index");

        let selectedProduct = products[currentIndex];
        if (!selectedProduct) return;

        $("#productSearch").val(selectedProduct.name);
        $("#productid").val(selectedProduct.id);
        $("#cp").val(selectedProduct.cp || 0);
        $("#mrp").val(selectedProduct.mrp || 0);

        $("#total").focus().select();

    });


    $(document).on("keydown", "#paymentListTableBody tr", function (e) {

        if (e.key === "ArrowDown") {
            e.preventDefault();

            if (currentIndex < products.length - 1) {
                currentIndex++;
                updateHighlight();
                $("#paymentListTableBody tr").eq(currentIndex).focus();
            }

            if (
                currentIndex >= products.length - 5 &&
                !isLoading &&
                hasMore
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
                $("#paymentListTableBody tr").eq(currentIndex).focus();
            }
        }

    });

    $(".table-responsive").on("scroll", function () {

        let $this = $(this);

        if ($this.scrollTop() + $this.innerHeight() >= this.scrollHeight - 10) {

            if (hasMore && !isLoading) {
                offset += limit;
                loadProducts(query, offset, true);
            }
        }
    });


    $("#quantity").off("input");
    $("#cp").off("input");


    function addToSelectedList(productId, pname, bankId, bankName, qty, cp, mrp, expiry, total) {

        let row = `
            <tr 
                data-product-id="${productId}"
                data-bank-id="${bankId}"
                data-qty="${qty}"
                data-cp="${cp}"
                data-mrp="${mrp}"
                data-expiry="${expiry || ""}"
            >
                <td>${$("#selectedPaymentListPayment tr").length + 1}</td>
                <td>${pname}</td>
                <td>${bankName}</td>
                <td>${total.toFixed(2)}</td>
                <td>
                    <button type="button" class="btn btn-sm btn-primary edit-item">Edit</button>
                    <button type="button" class="btn btn-sm btn-danger remove-item">Remove</button>
                </td>
            </tr>
        `;

        $("#selectedPaymentListPayment").append(row);

        $("#productid").val("");
        $("#productSearch").val("");
        $("#cp").val("0");
        $("#mrp").val("0");
        $("#quantity").val("1");
        $("#total").val("");

        updateInvoiceSummary(); 
    }

    $(document).on("click", ".edit-item", function () {

        let row = $(this).closest("tr");

        let productId = row.data("product-id");
        let bankId = row.data("bank-id");

        let name = row.find("td:eq(1)").text();
        let amount = row.find("td:eq(3)").text();

        $("#productid").val(productId);
        $("#productSearch").val(name);
        $("#transaction_with").val(bankId);
        $("#total").val(amount);

        $("#addProductBtn").data("editRow", row);
        $("#addProductBtn").text("Update");

        $("#total").focus().select();
    });


    function clearInputs() {
        $("#productid").val("");
        $("#productSearch").val("");
        $("#cp").val("0");
        $("#mrp").val("0");
        $("#quantity").val("1");
        $("#total").val("");
        $("#expiryDate").val("");
        $("#addProductBtn").removeData("editRow").text("Add");
    }

    function updateSerial() {
        $("#selectedPaymentListPayment tr").each(function(index) {
            $(this).find("td:eq(0)").text(index + 1);
        });
    }

    $(document).on("click", ".remove-item", function () {

        let pname = $(this).closest("tr").find('td:eq(1)').text();

        if (confirm("Are you sure to remove:\n\n" + pname + " ?")) {
            $(this).closest("tr").remove();
        }

        $("#selectedPaymentListPayment tr").each(function (index) {
            $(this).find("td:first").text(index + 1);
        });

        $('#productSearch').focus();
        updateSerial();
        updateInvoiceSummary();
    });


    function updateInvoiceSummary() {
        let invoiceAmount = 0;

        $("#selectedPaymentListPayment tr").each(function () {
            let rowTotal = parseFloat($(this).find("td:eq(3)").text()) || 0;
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

        $("#selectedPaymentListPayment tr").each(function () {
            let rowTotal = parseFloat($(this).find("td:eq(3)").text()) || 0;
            total += rowTotal;
        });

        $("#grandTotal").text(total.toFixed(2));
    }

    $("#discount, #advanced").on("input", function () {
        updateInvoiceSummary();
    });


    function loadTransactionUsers() {
        $.ajax({
            url: window.APP_URLS.BANK_COMBO_URL,
            type: "GET",
            success: function (response) {

                let banks = response.bank_combo || [];
                let html = `<option value="">Select Bank</option>`;

                banks.forEach(item => {
                    html += `<option value="${item.id}">
                                ${item.name}
                             </option>`;
                });

                $("#transaction_with").html(html);
            },
            error: function (xhr) {
                console.log("Bank load error:", xhr.responseText);
                alert("Failed to load bank list");
            }
        });
    }

    loadTransactionUsers();
    loadProducts();

});
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

$('#saveAllBtn').on('click', function (e) {
    e.preventDefault();

    let paymentList = [];

    $('#selectedPaymentListPayment tr').each(function () {
        let row = $(this);

        let productId = row.data('product-id');
        let qty = parseFloat(row.data('qty')) || 1;
        let amount = parseFloat(row.find('td:eq(3)').text()) || 0;
        let mrp = parseFloat(row.data('mrp')) || 0;
        let expiry = row.data('expiry') || null;

        paymentList.push([
            productId,
            qty,
            amount,
            mrp,
            expiry,
            amount
        ]);
    });

    if (!paymentList.length) {
        alert("No products selected!");
        return;
    }

    let receive = parseFloat($('#advanced').val()) || 0;
    let net_amount = parseFloat($('#netAmount').val()) || 0;

    console.log("Receive:", receive, "Net:", net_amount);

    if (receive > net_amount) {
        alert("⚠️ Invalid Receive/Advance Amount! It cannot exceed Net Amount.");
        $('#advanced').focus().select();
        return;
    }    

    let payload = {
        store: parseInt($('.store-select').val()) || null,
        location: parseInt($('.location-select').val()) || null,

        tran_type_with: parseInt($('#transaction_with').val()) || null,
        tran_type: 4,
        tran_method: "payment",
        invoice: $('#paymentinvoice').val(),
        payment_method: $('#payment_method').val(),
        bill_amount: parseFloat($('#invoiceAmount').val()) || 0,
        discount: parseFloat($('#discount').val()) || 0,
        net_amount: parseFloat($('#netAmount').val()) || 0,
        receive: 0,
        payment: parseFloat($('#advanced').val()) || 0,
        due: parseFloat($('#balance').val()) || 0,
        tran_date: $('#tranDate').val(),
        products: paymentList        
    };
    
    $.ajax({
        url: "/bank_tran/deposit/save-deposit/",
        type: "POST",
        headers: { "X-CSRFToken": csrftoken },
        contentType: "application/json",
        data: JSON.stringify(payload),
        success: function (response) {
            alert("Saved Successfully!");
            $("#selectedPaymentListPayment").empty();
            $("#invoiceAmount").val("0");
            $("#discount").val("0");
            $("#netAmount").val("0");
            $("#advanced").val("0");
            $("#balance").val("0");
            $('#productSearch').focus();
            console.log(response);
        },
        error: function(xhr){
            console.error(xhr.status, xhr.responseText);
            alert("Save failed! Check console for error.");
        }
    });
});