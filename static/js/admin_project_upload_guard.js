(function () {
  // Vercel serverless payload limits can break large multipart uploads.
  var MAX_BYTES = 4 * 1024 * 1024; // 4MB practical guard

  function toMB(bytes) {
    return (bytes / (1024 * 1024)).toFixed(2);
  }

  function validateFiles(event) {
    var inputs = document.querySelectorAll('input[type="file"]');
    for (var i = 0; i < inputs.length; i += 1) {
      var input = inputs[i];
      if (!input.files || !input.files.length) {
        continue;
      }

      for (var j = 0; j < input.files.length; j += 1) {
        var file = input.files[j];
        if (file.size > MAX_BYTES) {
          alert(
            'File "' + file.name + '" is ' + toMB(file.size) + 'MB. '\
            + 'Please upload files under 4MB when using Django admin on Vercel.'
          );
          event.preventDefault();
          return false;
        }
      }
    }

    return true;
  }

  document.addEventListener('DOMContentLoaded', function () {
    var form = document.querySelector('form#project_form') || document.querySelector('form[enctype="multipart/form-data"]');
    if (!form) {
      return;
    }

    form.addEventListener('submit', validateFiles);
  });
})();
