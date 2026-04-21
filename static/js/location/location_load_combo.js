function loadDivisionsCombo() {
    $.ajax({
        // url: '/pharmacy/get-divisions-combo/',
        // url: "{% url 'get_divisions_combo' %}",
        // url: DIVISION_COMBO_URL,
        url: window.APP_URLS.DIVISION_COMBO_URL,
        method: 'GET',
        dataType: 'json',
        success: function(response) {

            console.log("Division response:", response);

            let divisions = response.divisions_combo || [];
            // let $select = $('#location');
            let $select = $('.location-select');

            $select.empty(); // Clear existing options

            // ✅ Default option
            $select.append('<option value="">-- Select Location --</option>');

            if (divisions.length === 0) {
                $select.append('<option value="">No Divisions Found</option>');
                return;
            }

            $.each(divisions, function(index, d) {
                $select.append(
                    `<option value="${d.id}">${d.division}</option>`
                );
            });

            // ✅ Auto-select first subjects and trigger change
            $select.val(divisions[0].id).trigger('change');

        },
        error: function(xhr) {
            console.error(xhr.responseText);
            alert("Failed to load divisions");
        }
    });
};
    
$(document).ready(function () {
    loadDivisionsCombo();
});