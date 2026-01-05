$(document).ready(function () {
  // Use event delegation to handle dynamically created file inputs
  $(document).on("change", "#profiles", function (e) {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();

      reader.onload = function (e) {
        // ONLY update the <img> preview
        // DO NOT touch or replace the file input!
        $("#preview-img").attr("src", e.target.result).show();
        // Optional: Add nice green border when photo is selected
        $("#preview-img")
          .removeClass("border-gray-300")
          .addClass("border-green-500");
      };

      reader.readAsDataURL(file);
    }
  });

 
});

