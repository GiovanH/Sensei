<?php
$locale='en_US.UTF-8';
setlocale(LC_ALL,$locale);
putenv('LC_ALL='.$locale);
echo exec('locale charmap');
echo exec('LANG=en_US.utf8; locale charmap'); 
?>