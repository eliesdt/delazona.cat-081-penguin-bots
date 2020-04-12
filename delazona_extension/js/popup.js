$( document ).ready(function() {
    chrome.storage.sync.get(['cp'], function(result) {
      if(result.cp != undefined){
        document.getElementById("cp-text").innerText = "Si vols canviar-lo pots tornar-lo a guardar:";
        document.getElementById("cp-number").innerText = result.cp;
      }
    });
});

document.getElementById("cp-submit").onclick = function(){
  var postcode = document.getElementById("cp-input").value;
  chrome.storage.sync.set({cp: postcode}, function() {
    document.getElementById("cp-text").innerText = "Codi postal guardat. Gràcies!"
    document.getElementById("cp").style.display = "block";
    document.getElementById("cp-number").innerText = postcode;
  });
}