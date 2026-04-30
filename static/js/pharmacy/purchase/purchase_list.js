$(document).ready(function () {

    // =========================
    // VARIABLES
    // =========================
    let purchaseList = [];
    let currentIndex = 0;
    let offset = 0;
    let limit = 50;
    let query = "";
    let hasMore = true;
    let isLoading = false;
    let currentRequest = null;

    // =========================
    // SET TODAY DATE
    // =========================
function setTodayDate() {

    console.log("🔥 setTodayDate CALLED");

    if ($("#start_date").val() || $("#end_date").val()) {
        return;
    }

    const today = new Date();
    const localDate =
        today.getFullYear() + "-" +
        String(today.getMonth() + 1).padStart(2, "0") + "-" +
        String(today.getDate()).padStart(2, "0");

    $("#start_date").val(localDate);
    $("#end_date").val(localDate);
}

    // =========================
    // LOAD DATA
    // =========================
    function loadPurchaseList(q = "", newOffset = 0, append = false) {

        if (isLoading) return;

        if (currentRequest) {
            currentRequest.abort();
        }

        isLoading = true;

        const start_date = $("#start_date").val();
        const end_date = $("#end_date").val();

        currentRequest = $.ajax({
            url: "/purchase-list-load/",
            method: "GET",
            data: {
                q: q,
                offset: newOffset,
                start_date: start_date,
                end_date: end_date
            },

            success: function (res) {

                const fetched = res.results || [];

                if (append) {
                    purchaseList = purchaseList.concat(fetched);
                } else {
                    purchaseList = fetched;
                    currentIndex = 0;
                }

                offset = newOffset;

                renderTable();

                hasMore = fetched.length === limit;

                isLoading = false;
            },

            error: function () {
                isLoading = false;
            }
        });
    }

    // =========================
    // RENDER
    // =========================
    function renderTable() {

        let html = "";

        purchaseList.forEach((p, i) => {
            html += `
                <tr data-index="${i}" class="${i === currentIndex ? 'table-active' : ''}">
                    <td>${i + 1}</td>
                    <td>${p.tran_id}</td>
                    <td>${p.tran_date}</td>
                    <td>${p.tran_type_with}</td>
                    <td>${p.tran_user}</td>
                    <td style="text-align:right;">${p.bill_total}</td>
                    <td style="text-align:right;">${p.discount}</td>
                    <td style="text-align:right;">${p.net_total}</td>
                    <td style="text-align:right;">${p.advance}</td>
                    
                    <td style="text-align:right;">${p.due_collection}</td>
                    <td style="text-align:right;">${p.due_discount}</td>
                    <td style="text-align:right;">${p.due}</td>
                    <td>
                    <button class="btn btn-sm btn-primary">Edit</button>
                    </td>
                </tr>
            `;
        });

        $("#purchaseListTableBody").html(html);
    }

    // =========================
    // INIT
    // =========================
    setTodayDate();
    loadPurchaseList("", 0, false);




    // =========================
    // FILTER BUTTON
    // =========================
    // $(document).on("click", "#filterBtn", function (e) {
//     e.preventDefault();

//     query = $("#supplierSearch").val().trim();

//     const start_date = $("#start_date").val();
//     const end_date = $("#end_date").val();

//     console.log("FILTER APPLY:", { query, start_date, end_date });

//     offset = 0;
//     currentIndex = 0;
//     hasMore = true;

//     loadPurchaseList(query, 0, false);
// });
// $("#filterBtn").on("click", function (e) {
//     e.preventDefault();

//     let start_date = $("#start_date").val();
//     let end_date = $("#end_date").val();
//     let query = $("#supplierSearch").val().trim();

//     //  CHECK IF DATE EXISTS
//     if (!start_date && !end_date) {
//     const today = new Date().toISOString().split("T")[0];
//     start_date = today;
//     end_date = today;

//     $("#start_date").val(today);
//     $("#end_date").val(today);

//     offset = 0;
//     currentIndex = 0;
//     hasMore = true;

//     loadPurchaseList(query, 0, false);
// }
    // =========================
    // DATE CHANGE AUTO FILTER
    // =========================
    $("#start_date, #end_date").on("change", function () {

        query = $("#supplierSearch").val().trim();

        offset = 0;
        currentIndex = 0;
        hasMore = true;

        loadPurchaseList(query, 0, false);
    });

    // =========================
    // SEARCH INPUT
    // =========================
    let typingTimer;

    $("#supplierSearch").on("input", function () {

        clearTimeout(typingTimer);

        typingTimer = setTimeout(() => {

            query = $(this).val().trim();

            offset = 0;
            currentIndex = 0;
            hasMore = true;

            loadPurchaseList(query, 0, false);

        }, 300);
    });

    // =========================
    // SCROLL PAGINATION
    // =========================
    $(".table-responsive").on("scroll", function () {

        if ($(this).scrollTop() + $(this).innerHeight() >= this.scrollHeight - 10) {

            if (hasMore && !isLoading) {
                offset += limit;
                loadPurchaseList(query, offset, true);
            }
        }
    });

    $("#printReportBtn").on("click", function () {

    let start_date = $("#start_date").val();
    let end_date = $("#end_date").val();
    let q = $("#supplierSearch").val().trim();

    let url = `/purchase/report/pdf/?q=${encodeURIComponent(q)}&start_date=${start_date}&end_date=${end_date}`;

    window.open(url, "_blank"); // direct download
});


});


