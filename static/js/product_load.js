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

    // Update total (optional, if you have bottom total)
    updateSelectedTotal();
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
        $("#price").val(selectedProduct.mrp);
        $("#quantity").focus();
    }
}

    });

    // ENTER in quantity field → Add item
$("#quantity").on("keydown", function (e) {
    if (e.key === "Enter") {
        e.preventDefault();
        e.stopPropagation();   // VERY IMPORTANT

        let pname = $("#productSearch").val();
        let price = $("#price").val();
        let qty = $("#quantity").val();
        let total = $("#total").val();
        $("#productSearch").focus();

        if (pname && price && qty && total) {
            addToSelectedList(pname, price, qty, total);
        }
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
});


    loadProducts();
});