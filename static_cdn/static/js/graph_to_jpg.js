function downloadGraph(image, filename) {
    var downloadLink;
    // Download link
    downloadLink = document.createElement("a");
    // File name
    downloadLink.download = filename;
    // Create a link to the file
    downloadLink.href = image;
    // Hide download link
    downloadLink.style.display = "none";
    // Add the link to DOM
    document.body.appendChild(downloadLink);
    // Click download link
    downloadLink.click();
}
function exportImgToJpg(filename,element) {
    var url_base65 = $(element).parents(".card").find("canvas")[0].toDataURL("image/jpg");
    downloadGraph(url_base65, filename);
}
$(document).ready(function(){
  $(document).on('click','.download-graph',function(){
    var fname=$(this).attr('id')+".jpg"
    exportImgToJpg(fname,$(this))
  });
});
