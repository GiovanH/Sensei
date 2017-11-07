<html>
<head>
<link rel="stylesheet" type="text/css" href="/css/base.css">
</head>
<body>
<h1><?php   

  echo("PHP var dump")

?></h1>

<pre>
<?php

$arr = get_defined_vars();
print_r($arr);

$arr = get_defined_constants();
print_r($arr);

var_dump();

?>
</pre>

<a href='./..'>Back</a>
</body>
</html>