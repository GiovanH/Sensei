$( document ).ready(function() {
	$('input.exclusive').change(function() {
		c = this;
		$.each($("input.exclusive[type|='text']"),function(a,b){ if(b != c){ b.value = ""; } })
	});
});
