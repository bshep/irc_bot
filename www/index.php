<?php
//phpinfo();
    error_reporting(E_ALL);
    ini_set("display_errors","On");
    ini_set('safe_mode_exec_dir', '/usr/bin/');
    print 'ExecDir: '.ini_get('safe_mode_exec_dir');

    chdir('..');
$out = array();
$ret = exec('git pull', $out);
print_r($out);
print 'RetVal:'.$ret;

?>
