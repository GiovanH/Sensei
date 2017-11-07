// Menu selection
function loaded_report(report){
	mapd = report.contentDocument;
	
	mapd.head.innerHTML += "<base target='_blank'>"
	mapd.head.innerHTML += '<link rel="stylesheet" href="./inner.css" type="text/css">'
	
	//Main taggifier code
	
	if (inIframe() == true) {
		mapd.getElementsByTagName("body")[0].innerHTML = 
		mapd.getElementsByTagName("body")[0].innerHTML.replace(/(\t*)(.+)( \| )(.*)( \| )(.+)/g,"<span class='page $6' >$1<a href='javascript:window.top.scrollnav(\"$2\")' title='$2: $6'>$4</a></span>");
	} else {	
		mapd.getElementsByTagName("body")[0].innerHTML = 
		mapd.getElementsByTagName("body")[0].innerHTML.replace(/(\t*)(.+)( \| )(.*)( \| )(.+)/g,"<span class='page $6' >$1<a href='http://www.mspaintadventures.com/index.php?s=6&p=$2' title='$2: $6'>$4</a></span>");
	}
	
	//Replace /t tabs with three non-breaking spaces
	mapd.getElementsByTagName("body")[0].innerHTML = 
	mapd.getElementsByTagName("body")[0].innerHTML.replace(/(\t)/g,"&nbsp;&nbsp;&nbsp;&nbsp");
	
	//Manual Colors
	colorMatrix = [["ROSE","#b536da"],["VRISKA","#005682"],["DAVESPRITE","#f2a400"],["ROXY","#ff6ff2"],["DAVE","#e00707"],["JADE","#4ac925"],["JOHN","#0715cd"],["JOKE","#1f9400"],["DIRK","#f2a400"],["KANAYA","#008141"],["TEREZI","#008282"]]
	
	$.each(colorMatrix, function( index, array ) {
		re = new RegExp("\\{" + array[0] + "\\}","g");
		mapd.getElementsByTagName("body")[0].innerHTML = 
		mapd.getElementsByTagName("body")[0].innerHTML.replace(re,"{" + array[1] + "}");
	});
	
	
	$.each(mapd.getElementsByClassName("page"), function( index, element ) {
		
		if (element.children[0].innerText.search(/(\{(.*)\}(.*))/) >= 0) {
			info = JSON.parse(element.children[0].innerHTML.replace(/(\{(.*)\}(.*))/g,'{"Color": "$2", "Page": "$3"}'))
			element.children[0].style.color = info["Color"]
			element.children[0].innerText = info["Page"]
		}
	});
	
	//Replace the entire PRE tag with a DIV for good measure
	mapd.getElementsByTagName("body")[0].innerHTML = mapd.getElementsByTagName("body")[0].innerHTML.replace("<pre","<div");
	mapd.getElementsByTagName("body")[0].innerHTML = mapd.getElementsByTagName("body")[0].innerHTML.replace("</pre>","</div>");
	
	//mapd.getElementsByTagName("body")[0].innerHTML = "<div>" + mapd.getElementsByTagName("body")[0].innerHTML + "</div>"
	
	//UNUSED: Comprehensive JSON page object
	pagematrix = {}
	$.each(mapd.getElementsByClassName("page"), function( index, element ) {
		pg = element.children[0].title.slice(0,6)
		pagematrix[pg] = {title: element.children[0].innerHTML}
	});
	
	//Function for setting the main progress bar value
	function mouseprogressbar(a){document.getElementById("progressbar").value = a}
	
	//Gives every page <a> a function to set the main progres bar to its own page #
	$.each(mapd.getElementsByTagName("a"), function( index, value ) { 
		value.onmouseover = function(){mouseprogressbar(mapd.getElementsByTagName("a")[index].title.slice(0,6)-1902)}
	})
	
	
	$.each(mapd.getElementsByClassName("doc"), function( index, value ) { 
		value.onmouseenter = function(){scratchstyle();}
		value.onmouseleave = function(){normstyle();}
	})
	
	$.each(mapd.getElementsByClassName("A6A6"), function( index, value ) { 
		value.onmouseenter = function(){A6A6();}
		value.onmouseleave = function(){normstyle();}
	})
	
	$.each(mapd.getElementsByClassName("SBAHJ"), function( index, value ) { 
		value.onmouseenter = function(){sbahj(this);}
		value.onmouseleave = function(){normstyle();}
	})
	
	$.each(mapd.getElementsByClassName("ZAP"), function( index, value ) { 
		value.onmouseenter = function(){ZAP();}
		value.onmouseleave = function(){normstyle();}
	})
	
	$.each(mapd.getElementsByClassName("COLLIDE"), function( index, value ) { 
		value.onmouseenter = function(){collide();}
		value.onmouseleave = function(){normstyle();}
	})
	
	$.each(mapd.getElementsByClassName("CASCADE"), function( index, value ) { 
		value.onmouseenter = function(){collide();}
		value.onmouseleave = function(){normstyle();}
	})
	//FILTERING BUTTONS
	/*var unique = function (list, x) {
		if (x != "" && list.indexOf(x) === -1) {
			list.push(x);
		}
		return list;
	};

	var trim = function (x) { return x.trim(); };

	var classes = [].reduce.call(mapd.getElementsByTagName('*'), function (acc, e) {
		return e.className.split(' ').map(trim).reduce(unique, acc);
	}, []); */
	
	//This mess of something will get an array of every class used.
	var classes = [].reduce.call(mapd.getElementsByTagName('*'), function (acc, e) {
	return e.className.split(' ').map(function (x) { return x.trim()}).reduce(function (list, x) {	if (x != "") {	list.push(x);	}	return list; }, acc);
	}, []);
	
	//Define classes to not be included in the filter box.
	ignoredclasses =
	[
	"page",
	"A5A1",
	"A5A2",
	"COLLIDE",
	"CASCADE",
	"Part",
	"Part1",
	"Part2",
	"Part3",
	"Part4"
	]
	
	//A function that sorts a repeating array by frequency
	function sortByFrequency(array) {
		var frequency = {};

		array.forEach(function(value) { frequency[value] = 0; });

		var uniques = array.filter(function(value) {
			return ++frequency[value] == 1;
		});

		return uniques.sort(function(a, b) {
			return frequency[b] - frequency[a];
		});
	}
	
	//Sort the dang array
	classes = sortByFrequency(classes);
	
	//A function that pulls human readable names in special circumstances
	filter = {
		"giofixthis":"TODO",
		"EOY":"END OF YEAR",
		"APPEAR":"FIRST APPEARANCE",
		"THE_END":"ENDING"
	}
	function hrclassname(classname){
		if (filter[classname] != undefined) {
			return filter[classname] 
		} else {
			return classname
		}
	}
	
	//Make checkbox elements
	$.each(classes.filter( function( el ) { return ignoredclasses.indexOf( el ) < 0;} ), function( index, element ) {

		document.getElementById("filterbox").innerHTML += '<label id="' + element + 'check"><input class="filtercheckbox" type="checkbox" checked title="' + element + '" onclick="toggleclass(this);">' + hrclassname(element) + ' (' + mapd.getElementsByClassName(element).length +  ')</label>'
		}
	)
	//document.getElementById("SECRETcheck").checked = false; toggleclass("secret")
	
	//Make the toggle-all button
	document.getElementById("filterbox").innerHTML += '<br /><button type="button" id="filterbutton" title="Click to toggle filters">Toggle All</button>'
	document.getElementById("filterbutton").onclick = function(){
		$.each(document.getElementsByClassName("filtercheckbox"), function( index, element ) {
			element.checked = !element.checked
			toggleclass(element);
			}
		)
	}

	//Tidy.
	console.log(mapd);
	mapd.getElementsByTagName("div")[0].style["white-space"] = ""
	map.height = mapd.getElementsByTagName('body')[0].innerHTML.split('\n').length * 18 + " px"
	map.style.display = "inherit"
	document.getElementById("loadingmsg").style.display = "none"
}
