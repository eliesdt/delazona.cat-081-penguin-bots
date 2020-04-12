
//---------------- EXTRACT DATA -------------------------------------------
var category = "unknown category";
if(document.querySelectorAll('[tabindex="42"]')[1] != undefined){
    category = document.querySelectorAll('[tabindex="42"]')[1].innerText;
};
var product_name = document.getElementById("productTitle").innerText;
product_name = product_name.split("/").join("");
product_name = product_name.split("-").join("");
product_name = product_name.split("&").join("");
product_name = product_name.split("?").join("");

var cp;
chrome.storage.sync.get(['cp'], function(result) {
    cp = result.cp;
});

//---------------- REMOVE THE NODE -------------------------------------------
function remove_node(){
    if(document.getElementById("buyitlocal") != undefined){
        document.getElementById("buyitlocal").remove();
    };
};

//---------------- INSERT BUTTON IN THE HTML -------------------------------------------
function insert_html(url_redirect){

    remove_node();

    //create new big node
    var node = document.createElement("div");
    node.id="buyitlocal";

    //create childs

    //logo
    var logo = document.createElement("img");
    logo.src = "https://svgur.com/i/JzR.svg"; //white
    logo.style.cssText = "width:10em;margin-right:0.5em;margin-left:0.5em";

    //text
    var text = document.createElement("div");
    var textnode = document.createTextNode("Hem trobat aquest producte al teu barri!");
    text.appendChild(textnode);
    text.style.cssText = "text-align:left;color:white;margin-right:0.2em;width:40%;border: 0px solid lightgray;padding: 0.5em;";

    //button
    var button = document.createElement("a");
    var buttontext = document.createTextNode("Veure");
    button.appendChild(buttontext);
    button.setAttribute("href",url_redirect);
    button.setAttribute("target","_blank");
    button.style.cssText = "margin-right:0.5em;margin-top:0.8em;height:2.4em;border:0px;width:20%;color:#4285F4; padding: 0.4em;border-radius: .4rem;background-color:white";

    //append childs to parent node
    node.append(logo);
    node.append(text);
    node.append(button);
    node.style.cssText = "border-radius:0.4rem; display: flex;text-align: center;margin-bottom:1em;background-color:#4285F4"


    //extract page node to insert
    var column =  document.getElementById("centerCol");

    //insert node in page
    if(document.getElementById("buyitlocal") == undefined){
        column.insertBefore(node, column.firstChild);
    };

};

//---------------- INSERT LOADING -------------------------------------------
function insert_loading(){
    //create new big node
    var node = document.createElement("div");
    node.id="buyitlocal";

    //create childs

    //image
    var image = document.createElement("img");
    image.src = "https://svgur.com/i/K0A.svg"; //loading blue circles
    image.style.cssText = "width:3em";

    //logo
    var logo = document.createElement("img");
    logo.src = "https://svgur.com/i/Jz2.svg"; //blue
    logo.style.cssText = "width:10em;margin-right:0.5em";

    //text
    var text = document.createElement("div");
    var textnode = document.createTextNode("Buscant botigues a prop teu");
    text.appendChild(textnode);
    text.style.cssText = "color:#4285F4;margin-top:1.2em;margin-right:0.5em";

    //append childs to parent node
    node.append(logo);
    node.append(text);
    node.append(image);
    node.style.cssText = "display: flex;text-align: center;margin-bottom:1em;background-color:white"


    //extract page node to insert
    var column =  document.getElementById("centerCol");

    //insert node in page
    if(document.getElementById("buyitlocal") == undefined){
        column.insertBefore(node, column.firstChild);
    };

};



//---------------- MAKE REQUEST -------------------------------------------
var url = "https://delazona.herokuapp.com/request?product_name="+product_name+"&category="+category+"&cp="+cp;
//var url = "https://delazona.herokuapp.com/request?product_name=cereales";
// var url = "https://5ae6b60b.ngrok.io/request?product_name="+"cereales"+"&category="+"comida"+"&cp="+cp;

var req = new XMLHttpRequest();
req.open('GET', url, true);
req.onreadystatechange = function (aEvt) {
    // console.log(req);
    if (req.readyState == 4) {
        if (req.status == 200){
            var response_json = JSON.parse(req.responseText);
            if(response_json.response){
                insert_html(response_json.url);
            }else{
                remove_node();
            };

        }else{
            remove_node();
            // console.log(req.responseText);

        }
    }
};
var sent = false;
if(!sent){
    req.send(null);
    sent = true;
}
insert_loading();



 

