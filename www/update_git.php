<?php
    chdir('..');
    $out = array();
    exec('git pull', $out);
    print_r($out);
?>