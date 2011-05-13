<html>
<head>
    <title>URL Log for #elweb</title>
</head>
</body>
<?php
    $db = new SQLite3('../dbs/urldb.db');
    
    $results = $db->query('SELECT * FROM urls WHERE spoken_where = \'#elweb\' ORDER BY count DESC');
    
    while($row = $results->fetchArray()) {
        print($row['spoken_by']." mentioned: <a href=\"".$row['url'].'">'.$row['url'].'</a> and was repated '.$row['count']." times<br>\n");
    }
?>
</body>
</html>