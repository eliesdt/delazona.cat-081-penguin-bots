// document.getElementById("nav-logo").style.display = "none";
console.log(document.querySelectorAll('[tabindex="42"]')[1].innerText);

//create new big node
var node = document.createElement("div");

//create childs

//text
var text = document.createElement("div");
var textnode = document.createTextNode("Hem trobat aquest producte al teu barri!");
text.appendChild(textnode);
text.style.cssText = "color:white;margin-right:0.2em;width:70%;border: 0px solid lightgray;padding: 0.5em;background-color: white; border-radius: 1.2em; background: rgb(87,0,255);background: linear-gradient(130deg, rgba(87,0,255,1) 0%, rgba(237,0,255,1) 62%);";

//button
var button = document.createElement("div");
var buttontext = document.createTextNode("Veure");
button.appendChild(buttontext);
button.style.cssText = "width:20%;color:white; padding: 0.5em;border-radius: 1.2em; background: rgb(0,255,181);background: linear-gradient(169deg, rgba(0,255,181,1) 18%, rgba(0,212,255,1) 100%);";


//append childs to parent node
node.append(text);
node.append(button);
node.style.cssText = "display: flex;text-align: center;margin-bottom:1em"


//extract page node to insert
var column =  document.getElementById("centerCol");

//insert node in page
column.insertBefore(node, column.firstChild);