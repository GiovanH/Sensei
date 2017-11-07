<html>
<head>
	<title>test.php</title>
	<meta http-equiv="content-type" content="text/html; charset=UTF-8">
	<link rel="stylesheet" type="text/css" href="/css/base.css">
	<link rel="stylesheet" type="text/css" href="/css/console.css">
	<link rel="stylesheet" type="text/css" href="/css/senseiinputform.css">

	<script src="./js/jquery-3.2.1.min.js"></script>
	<script src="./js/exclusiveinput.js"></script>
</head>
<body>
<h1>Sensei shell v 0.01</h1>


<?php
function test_input($data) {
	$data = trim($data);
	$data = stripslashes($data);
	#$data = htmlentities($data);
	return $data;
}

function sensei_exec($command) {
	
	#Move into our working directory, remembering where we were before
	$workdir = getcwd();
	chdir('/home/pi/Sensei/');
	
	#Actually do the shell execution
	#SHOULD BE TESTED and ESCAPED ALREADY!!!
	$command = escapeshellcmd($command);
	
	echo "<div class='loading'><span>Loading results. Please wait. </span></div>";
	
	#echo "\n<script>console.log('Testing input for " . $command . "')</script>";
	$output = shell_exec("LANG='en_US.UTF8' python3 sensei.py " . $command);
	#clean up after ourselves
	
	echo "<script>$('.loading').hide();</script>";
	
	chdir($workdir);
	
	return $output;
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
	$isoutput = false;
	if (!empty($_POST["sensei_scoreteacher"])) {
		$isoutput = true;
		$command = "scoreteacher \"" . escapeshellcmd(test_input($_POST["sensei_scoreteacher"])) . "\"";
	} elseif (!empty($_POST["sensei_scoreteacherbyid"])) {
		$isoutput = true;
		$command = "scoreteacherbyid " . escapeshellcmd(test_input($_POST["sensei_scoreteacherbyid"]));
	} elseif (!empty($_POST["sensei_scoreclass"])) {
		$isoutput = true;
		$command = "scoreclass " . escapeshellcmd(test_input($_POST["sensei_scoreclass"]));
	} elseif (!empty($_POST["sensei_compare"])) {
		$isoutput = true;
		$command = "compare " . escapeshellcmd(test_input($_POST["sensei_compare"]));
	}
	if ($isoutput) {
		$gargs = " --quiet";
		$gargs = $gargs . ' --redownload';
		if (!empty($_POST["sensei_yearrange"])) { $gargs = $gargs . ' --yearrange ' . escapeshellcmd(test_input($_POST["sensei_yearrange"])); }
		if (!empty($_POST["sensei_classcodes"])) { $gargs = $gargs . ' --classcodes ' . escapeshellcmd(test_input($_POST["sensei_classcodes"])); }
		if (!empty($_POST["sensei_glob"])) { $gargs = $gargs . ' --glob ' . test_input($_POST["sensei_glob"]); }
		$output = sensei_exec($command . $gargs);
		echo "<span class='inputwrp'>Sensei input: <span class='inputstr'>" . $command . $gargs . "</span></span>";
		echo "<span class='outputheader'>Sensei Output: </span><pre class='senseiout'>" . $output . "</pre>";
	}
}

function makeinput($func, $class){
	return '<input type="text" class="' . $class . '" name="sensei_' . $func . '" value="' . htmlentities($_POST["sensei_" . $func]) . '">';
}

?>                   
<form method="post" id="sensei_input_form" action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]);?>">  
  
<span class="input_header">Command<span class="description">Pick only one!</span></span>
  <span class="input">Score teacher: <?php echo makeinput("scoreteacher","exclusive")?><span class="description">Insert a teacher's name (case sensitive!) for a detailed score.</span></span>
  <span class="input">Score teacher by id: <?php echo makeinput("scoreteacherbyid","exclusive")?><span class="description">Insert a teacher's Net ID (email address) for a detailed score.</span></span>
  <span class="input">Score class: <?php echo makeinput("scoreclass","exclusive")?><span class="description">Insert a class code to score all teachers of that class. </span></span>
  <span class="input">Compare teachers: <?php echo makeinput("compare","exclusive")?><span class="description">Insert teacher names, in quotes, seperated by spaces to compare. Example: "XXX YYY" "ZZZ AAA"</span></span>
  
  <span class="input_header">Utilities<span class="description">Optional</span></span>
  <span class="input">Year range: <?php echo makeinput("yearrange")?><span class="description">Year range. Very expensive. Format is XX YY, where XX is the first year, and YY is the last.</span></span>
  <span class="input">Class codes: <?php echo makeinput("classcodes")?><span class="description">Regenerate class codes. Space seperated.</span></span>
  <span class="input">File globs: <?php echo makeinput("glob")?><span class="description">Files to be considered. Structure is YYs/ZZZZZZ, where YY is a year, S is a semester code, and ZZZZZZ is a class code.</span></span>
  
  <input type="submit" name="submit" value="Submit">  
</form>

<!-- 
TODO:

Clean up error messages
Use HTML tables?
Display timeframe and class codes within python program
Formatting tidying

-->


<a href='./..'>Back</a>
</body>
</html>