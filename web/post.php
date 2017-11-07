#!/usr/local/bin/php
<?php

echo 'This is not a public page. This page is for internal use.';

if ($_POST["clear"]) {
	$_POST["clear"] = "Flies cleared at " . date("D M j G:i:s T Y") . " with reason " . $_POST["clear"];
	echo array_map('unlink', glob("../posttxt/*.txt"));
}

foreach($_POST as $key => $item){
	file_put_contents ("../posttxt/" . $key . ".txt", $item);
}

foreach(glob("../posttxt/*.txt") as $key => $item){
	$rss = $rss . '<item>
    <title>' . $item . '</title>
    <link>https://'  . $_SERVER['SERVER_NAME'] . "/~seth.giovanetti/cgi-bin/" . $item . '</link>
    <description>' . file_get_contents($item) . '</description>
</item>';
}

$rss = '
<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">

<channel>
  <title>Postserv</title>
    <link>' . $_SERVER['SERVER_NAME'] . '~/seth.giovanetti/</link>
  <description>Lipsum</description>
'  .
$rss
. '</channel></rss>';

file_put_contents ("../dynamic.rss", $rss);

echo var_dump(glob("../posttxt/*.txt"));
?>