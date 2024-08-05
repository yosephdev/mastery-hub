// Get the initially selected country value
let countrySelected = $('#id_country').val();
// If no country is selected, set the color for the placeholder
if (!countrySelected) {
    $('#id_country').css('color', '#aab7c4');
}
// Event handler for the change of the country selection
$('#id_country').change(function() {
    countrySelected = $(this).val();
    if (!countrySelected) {
        $(this).css('color', '#aab7c4');
    } else {
        $(this).css('color', '#000');
    }
});

