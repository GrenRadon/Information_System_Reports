// script.js
$(document).ready(function() {
    // Función para obtener y actualizar los datos de los huéspedes
    function updateGuestInfo() {
        $.post("/guest_info", function(data) {
            // Manejar la respuesta de la solicitud POST
            // Aquí puedes realizar cualquier acción que desees con los datos devueltos
            console.log(data);

            // Actualizar la tabla con los datos recibidos
            if (data.length > 0) {
                var tableBody = '';
                for (var i = data.length - 1; i >= 0; i--) {
                    var row = data[i];
                    // Actualiza los índices para que coincidan con los campos devueltos desde la función get_guest_info()
                    tableBody += '<tr>';
                    tableBody += '<td>' + row[0] + '</td>';  // ID
                    tableBody += '<td>' + row[1] + '</td>';  // Hostname
                    tableBody += '<td>' + row[2] + '</td>';  // IP
                    tableBody += '<td>' + row[3] + '</td>';  // Disk Usage
                    tableBody += '<td>' + row[4] + '</td>';  // RAM Usage
                    tableBody += '<td>' + row[5] + '</td>';  // CPU Usage
                    tableBody += '</tr>';
                }
                $('#guest-info-table tbody').html(tableBody);
            }
        });
    }

    // Actualizar los datos cada 3 segundos
    setInterval(updateGuestInfo, 3000);
});
