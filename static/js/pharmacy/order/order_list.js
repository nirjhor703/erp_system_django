$(document).ready(function () {

    let orderList = [];
    let currentRequest = null;
    let offset = 0;
    let query = "";
    let isLoading = false;
    let limit = 50;

    function loadOrderList(q = "", newOffset = 0, append = false) {

        if (isLoading) return;

        if (currentRequest) {
            currentRequest.abort();
        }

        isLoading = true;

        currentRequest = $.ajax({
            url: "/order-list-load/",   // 🔥 NEW API
            method: "GET",
            data: { q: q, offset: newOffset },
            success: function (response) {

                let fetched = response.results || [];

                if (append) {
                    orderList = orderList.concat(fetched);
                } else {
                    orderList = fetched;
                    offset = newOffset;
                }

                renderTable();
                isLoading = false;
            }
        });
    }

    function renderTable() {
        let html = "";

        orderList.forEach((o, i) => {
            html += `
                <tr>
                    <td>${i + 1}</td>
                    <td>${o.tran_id}</td>
                    <td>${o.tran_date}</td>
                </tr>
            `;
        });

        $("#purchaseListTableBody").html(html);
    }

    // search
    $("#supplierSearch").on("input", function () {
        let value = $(this).val().trim();
        query = value;
        offset = 0;
        loadOrderList(query, offset, false);
    });

    loadOrderList();
});