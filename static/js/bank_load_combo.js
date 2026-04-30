function loadBankCombo() {
    console.log("BANK URL:", window.APP_URLS.BANK_COMBO_URL);

    $.ajax({
        url: window.APP_URLS.BANK_COMBO_URL,
        method: 'GET',
        dataType: 'json',
        success: function(response) {

            console.log("Bank response:", response);

            let bank = response.bank_combo || [];
            let $select = $('.bank-select');

            $select.empty();
            $select.append('<option value="">-- Select Bank --</option>');

            if (bank.length === 0) {
                $select.append('<option value="">No Bank Found</option>');
                return;
            }

            $.each(bank, function(index, d) {
                $select.append(
                    `<option value="${d.id}">${d.name}</option>`
                );
            });
        },
        error: function(xhr) {
            console.log("Status:", xhr.status);
            console.log("Response:", xhr.responseText);
            alert("Failed to load bank");
        }
    });
}

$(document).ready(function () {
    loadBankCombo();
});