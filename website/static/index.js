function deleteFile(fileId,type) {
  var username = document.getElementById("username").value;
  fetch("/delete-file", {
    method: "POST",
    body: JSON.stringify({ fileId: fileId , type:type , username:username}),
  }).then((_res) => {
    window.location.href = "/";
  });
}



