// var btn = document.querySelector("body > button")
'use strict';

var params = document.querySelectorAll("label > input")

function solve() {
  var data = {};
  for (var i = 0; i < params.length; i++) {
    data[`${params[i].parentNode.textContent.trim()}`] = params[i].value;
  }

  data['equation_type'] = "implicit";

  $.ajax({
    type: 'POST',
    data: JSON.stringify(data),
    url: '/labs?lab_id=5',
    contentType: "application/json; charset=utf-8",
    dataType: 'json',
    success: function (data, textStatus) {
      // $('#progressBar').width(`${data.Progress}%`);
      if (data.IsFinished) {
        console.log(data.json());
        // clearInterval(intervalId);
        // window.location.reload();
      }
    }
  });


  // var req = new XMLHttpRequest();
  // req.open("POST", `${window.location.protocol}/labs?lab_id=5`);
  // req.setRequestHeader('Content-Type', 'application/json');
  // req.send(JSON.stringify(data));
  // req.onreadystatechange = function () {
  //   var resp = JSON.parse(req.responseText);

  //   new Chartist.Line(".chart", resp)
  // }
}

// btn.addEventListener("click", solve);

// var data = {
//   // A labels array that can contain any sort of values
//   labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
//   // Our series array that contains series objects or in this case series data arrays
//   series: [
//     [5, 2, 4, 2, 0]
//   ]
// };

// // Create a new line chart object where as first parameter we pass in a selector
// // that is resolving to our chart container element. The Second parameter
// // is the actual data object.
// new Chartist.Line('.chart', data);
