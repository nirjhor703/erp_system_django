$(function(){

  // ================= ADD =================
$(function(){

    // ================= ADD PRODUCT =================
    $("#addProductForm").submit(function(e){
        e.preventDefault();
        let form = $(this);

        $.ajax({
            url: "/pharmacy-products/add/",  // backend URL
            method: "POST",
            data: form.serialize(),
            success: function(res){
                // Hide modal
                $("#addProductModal").modal("hide");

                // Show toaster after modal hide
                setTimeout(function(){
                    toastr.success("Pharmacy Product added!");
                }, 200);

                // Navigate to last page
                let rows = $("#rowsPerPage").val() || 15;
                location.href = "?page=" + res.last_page + "&rows=" + rows;

                // Clear form
                $("#addProductForm")[0].reset();
            },
            error: function(){
                toastr.error("Something went wrong!");
            }
        });
    });
    $(document).on("click", ".editBtn", function(){
    let id = $(this).data("id");
    
    // Ajax to fetch product data (or you already have data in row)
    let row = $("#row" + id);

    // Fill modal fields
    $("#edit_id").val(id);
    $("#edit_name").val(row.find("td:eq(2)").text());  // Product Name

    // Dropdowns: use value, not text
    let groupeVal = row.find("td:eq(1)").data("id");      // Assuming you stored id in data-id attribute
    let categoryVal = row.find("td:eq(3)").data("id");
    let manufacturerVal = row.find("td:eq(4)").data("id");
    let formVal = row.find("td:eq(5)").data("id");
    let unitVal = row.find("td:eq(6)").data("id");
    let companyVal = row.find("td:eq(10)").data("id");

    $("#editGroupe").val(groupeVal);
    $("#editCategory").val(categoryVal);
    $("#editManufacturer").val(manufacturerVal);
    $("#editForm").val(formVal);
    $("#editUnit").val(unitVal);
    $("#editCompany").val(companyVal);

    // Show modal
    $("#editProductModal").modal("show");
});

    // ================= EDIT PRODUCT =================
    $("#editProductForm").submit(function(e){
        e.preventDefault();
        let form = $(this);
        let id = $("#edit_id").val();

        $.ajax({
            url: "/pharmacy-products/edit/" + id + "/",
            method: "POST",
            data: form.serialize(),
            success: function(res){
                $("#editProductModal").modal("hide");
                toastr.success("Product updated!");

                // Update row in table
                let row = $("#row" + id);
                row.find("td:eq(1)").text($("#editGroupe option:selected").text());
                row.find("td:eq(2)").text($("#edit_name").val());
                row.find("td:eq(3)").text($("#editCategory option:selected").text() || '-');
                row.find("td:eq(4)").text($("#editManufacturer option:selected").text() || '-');
                row.find("td:eq(5)").text($("#editForm option:selected").text() || '-');
                row.find("td:eq(6)").text($("#editUnit option:selected").text() || '-');
                row.find("td:eq(10)").text($("#editCompany option:selected").text());
            },
            error: function(){
                toastr.error("Something went wrong!");
            }
        });
    });

    // ================= DELETE PRODUCT =================
    $(document).on("click", ".deleteBtn", function(){
        if(!confirm("Are you sure you want to delete this product?")) return;

        let id = $(this).data("id");
        $.ajax({
            url: "/pharmacy-products/delete/" + id + "/",
            method: "POST",
            data: {"csrfmiddlewaretoken": $("input[name='csrfmiddlewaretoken']").val()},
            success: function(res){
                if(res.success){
                    $("#row" + id).remove();
                    toastr.success("Product deleted!");

                    // Recalculate SL
                    $("#pharmacyProductTable tbody tr").each(function(index){
                        $(this).find("td:first").text(index + 1);
                    });
                }
            },
            error: function(){
                toastr.error("Something went wrong!");
            }
        });
    });

    // Optional: Filter table or search input logic
    $(".column-filter").on("keyup", function(){
        let col = $(this).data("col");
        let val = $(this).val().toLowerCase();
        $("#pharmacyProductTable tbody tr").filter(function(){
            $(this).toggle($(this).find("td").eq(col).text().toLowerCase().indexOf(val) > -1)
        });
    });

});


  // ================= EDIT =================
  $(document).on("click", ".editBtn", function(){
      let id = $(this).data("id");

      // Get row data (or AJAX fetch if needed)
      let row = $("#row"+id);
      $("#edit_product_id").val(id);
      $("#edit_product_name").val(row.find("td:eq(2)").text());
      $("#edit_groupe").val($("td:eq(1)", row).text() ? row.find("td:eq(1)").data("id") : "");
      $("#edit_category").val($("td:eq(3)", row).text() ? row.find("td:eq(3)").data("id") : "");
      $("#edit_manufacturer").val($("td:eq(4)", row).text() ? row.find("td:eq(4)").data("id") : "");
      $("#edit_form").val($("td:eq(5)", row).text() ? row.find("td:eq(5)").data("id") : "");
      $("#edit_unit").val($("td:eq(6)", row).text() ? row.find("td:eq(6)").data("id") : "");
      $("#edit_company").val($("td:eq(10)", row).text() ? row.find("td:eq(10)").data("id") : "");

      $("#editProductModal").modal("show");
  });

  $("#editProductForm").submit(function(e){
      e.preventDefault();
      let form = $(this);
      let id = $("#edit_product_id").val();

      $.ajax({
          url: "/pharmacy-products/edit/"+id+"/",
          method: "POST",
          data: form.serialize(),
          success: function(res){
              $("#editProductModal").modal("hide");
              setTimeout(function(){
                  toastr.success("Pharmacy Product updated!");
              }, 200);

              // Update row
              let row = $("#row"+id);
              row.find("td:eq(1)").text($("#edit_groupe option:selected").text());
              row.find("td:eq(2)").text($("#edit_product_name").val());
              row.find("td:eq(3)").text($("#edit_category option:selected").text() || '-');
              row.find("td:eq(4)").text($("#edit_manufacturer option:selected").text() || '-');
              row.find("td:eq(5)").text($("#edit_form option:selected").text() || '-');
              row.find("td:eq(6)").text($("#edit_unit option:selected").text() || '-');
              row.find("td:eq(10)").text($("#edit_company option:selected").text());
          },
          error: function(){
              toastr.error("Something went wrong!");
          }
      });
  });

  // ================= DELETE =================
  $(document).on("click", ".deleteBtn", function(){
      let id = $(this).data("id");
      if(!confirm("Are you sure you want to delete this product?")) return;

      $.ajax({
          url: "/pharmacy-products/delete/"+id+"/",
          method: "POST",
          data: {csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']").val()},
          success: function(res){
              $("#row"+id).remove();
              toastr.success("Pharmacy Product deleted!");

              // Recalculate SL
              $("#pharmacyProductTable tbody tr").each(function(index){
                  $(this).find("td:first").text(index + 1);
              });
          },
          error: function(){
              toastr.error("Something went wrong!");
          }
      });
  });

});
