// Frame code - V0.3
function loaded_report(map){
	mapd = map.contentDocument;
	
	mapd.head.innerHTML += "<base target='_blank'>"
	mapd.head.innerHTML += '<link rel="stylesheet" href="' + document.location.pathname + 'css/inner.css" type="text/css">'
	
	mapd.getElementsByTagName("body")[0].innerHTML = 
	mapd.getElementsByTagName("body")[0].innerHTML.replace(/(.*)\n/g,"<span class='page' >$1</span>");
	
	//Replace /t tabs with three non-breaking spaces
	mapd.getElementsByTagName("body")[0].innerHTML = 
	mapd.getElementsByTagName("body")[0].innerHTML.replace(/(\t)/g,"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp");
	
	//Replace the entire PRE tag with a DIV for good measure
	mapd.getElementsByTagName("body")[0].innerHTML = mapd.getElementsByTagName("body")[0].innerHTML.replace("<pre","<div");
	mapd.getElementsByTagName("body")[0].innerHTML = mapd.getElementsByTagName("body")[0].innerHTML.replace("</pre>","</div>");
	
	//Tidy.
	console.log(mapd);
	//mapd.getElementsByTagName("div")[0].style["white-space"] = ""
	map.height = (mapd.getElementsByTagName('span').length * 17.3) + " px"
	map.style.display = "inherit"
	// document.getElementById("loadingmsg").style.display = "none"
}
