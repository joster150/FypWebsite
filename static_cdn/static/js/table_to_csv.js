function downloadCSV(csv, filename) {
    var csvFile;
    var downloadLink;
    // CSV file
    csvFile = new Blob([csv], {type: "text/csv"});
    // Download link
    downloadLink = document.createElement("a");
    // File name
    downloadLink.download = filename;
    // Create a link to the file
    downloadLink.href = window.URL.createObjectURL(csvFile);
    // Hide download link
    downloadLink.style.display = "none";
    // Add the link to DOM
    document.body.appendChild(downloadLink);
    // Click download link
    downloadLink.click();
}
function exportTableToCSV(filename,element) {
    var csv = [];
    //console.log(element)
    var rows = $(element).parents(".col-12").find("tr.include-down");
    //console.log(rows)
    for (var i = 0; i < rows.length; i++) {
        var row = [], cols = $(rows[i]).find(".include-down");
        for (var j = 0; j < cols.length; j++)
            row.push(cols[j].innerText);
        csv.push(row.join(","));
    }
    //console.log(csv)
    // Download CSV file
    downloadCSV(csv.join("\n"), filename);
}
$(document).ready(function(){
  $(document).on('click','.download-table',function(){
    var fname=$(this).attr('id')+".csv"
    exportTableToCSV(fname,$(this))
  });
});
