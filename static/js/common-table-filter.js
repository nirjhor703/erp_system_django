$(document).on("keyup change", ".column-filter, .column-filter-select", function () {

    let filters = [];

    $('#searchInput').on('keyup change', function(e){
    // optional: trigger on Enter only
    if(e.key === "Enter" || e.type === "change"){
        let searchVal = $(this).val();
        let rows = $('#rowsPerPage').val(); // keep current rows per page
        window.location.href = '?search=' + encodeURIComponent(searchVal) + '&rows=' + rows;
    }
});

    $(".column-filter, .column-filter-select").each(function () {
        let col = $(this).data("col");
        let val = $(this).val().toLowerCase();
        filters.push({col, val});
    });

    $("tbody tr").each(function () {
        let row = $(this);
        let show = true;

        filters.forEach(f => {
            if (f.val !== "") {
                let cellText = row.find("td:eq(" + f.col + ")").text().toLowerCase();
                if (!cellText.includes(f.val)) {
                    show = false;
                }
            }
        });

        show ? row.show() : row.hide();
    });
});

// Clear Button
$(document).on("click", ".clearFilter", function () {
    $(".column-filter, .column-filter-select").val("");
    $("tbody tr").show();
});

$(document).ready(function() {

    function filterTable() {
        $(".filter-table").each(function () {
            let table = $(this);

            // 🔹 Generic global search input for this table
            // Try to find a .global-search input in the same container, fallback to first .global-search
            let searchInput = table.closest('div').find(".global-search").first();
            if (!searchInput.length) {
                searchInput = $(".global-search").first();
            }

            let globalVal = searchInput.val().toLowerCase();

            // Column filters
            let filters = [];
            table.find(".column-filter").each(function () {
                let col = $(this).data("col");
                let val = $(this).val().toLowerCase();
                filters.push({col, val});
            });

            // Rows loop
            table.find("tbody tr").each(function () {
                let row = $(this);
                let show = true;

                // Column-specific filters
                filters.forEach(f => {
                    if (f.val !== "") {
                        let cellText = row.find("td:eq(" + f.col + ")").text().toLowerCase();
                        if (!cellText.includes(f.val)) show = false;
                    }
                });

                // Global search (ignore last column)
                if (show && globalVal !== "") {
                    let rowText = "";
                    row.find("td").slice(0, -1).each(function() {
                        rowText += $(this).text().toLowerCase() + " ";
                    });
                    if (!rowText.includes(globalVal)) show = false;
                }

                show ? row.show() : row.hide();
            });
        });
    }

    // Trigger on column or global input
    $(document).on("keyup change", ".column-filter, .global-search", filterTable);

    // Clear button
    $(document).on("click", ".clearFilter", function () {
        $(".column-filter, .global-search").val("");
        $(".filter-table tbody tr").show();
    });

});


