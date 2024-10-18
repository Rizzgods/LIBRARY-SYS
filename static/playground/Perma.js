document.getElementById('Perma').addEventListener('change', function() {
    if (this.value === '1') { // 'Yes' selected
        // Copy values from Current Address to Permanent Address
        document.getElementById('lot_p').value = document.getElementById('lot').value;
        document.getElementById('Strt_p').value = document.getElementById('Strt').value;
        document.getElementById('Barangay_p').value = document.getElementById('Barangay').value;
        document.getElementById('City_p').value = document.getElementById('City').value;
        document.getElementById('Reg_p').value = document.getElementById('Reg').value;
        document.getElementById('Zip_p').value = document.getElementById('Zip').value;
        
        // Disable and make readonly the input fields in the Permanent Address section
        document.getElementById('lot_p').disabled = true;
        document.getElementById('Strt_p').disabled = true;
        document.getElementById('Barangay_p').disabled = true;
        document.getElementById('City_p').disabled = true;
        document.getElementById('Reg_p').disabled = true;
        document.getElementById('Zip_p').disabled = true;
        
        document.getElementById('lot_p').readOnly = true;
        document.getElementById('Strt_p').readOnly = true;
        document.getElementById('Barangay_p').readOnly = true;
        document.getElementById('City_p').readOnly = true;
        document.getElementById('Reg_p').readOnly = true;
        document.getElementById('Zip_p').readOnly = true;
    } else { // 'No' selected
        // Enable the input fields in the Permanent Address section
        document.getElementById('lot_p').disabled = false;
        document.getElementById('Strt_p').disabled = false;
        document.getElementById('Barangay_p').disabled = false;
        document.getElementById('City_p').disabled = false;
        document.getElementById('Reg_p').disabled = false;
        document.getElementById('Zip_p').disabled = false;
        
        // Remove readonly attribute
        document.getElementById('lot_p').readOnly = false;
        document.getElementById('Strt_p').readOnly = false;
        document.getElementById('Barangay_p').readOnly = false;
        document.getElementById('City_p').readOnly = false;
        document.getElementById('Reg_p').readOnly = false;
        document.getElementById('Zip_p').readOnly = false;
    }
});