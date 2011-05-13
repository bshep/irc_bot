<html>
<head>
    <title>URL Log for #elweb</title>
</head>
</body>
<?php
    $db = new SQLite3('../dbs/urldb.db');
    
    $results = $db->query('SELECT * FROM urls WHERE spoken_where = \'#elweb\' ORDER BY count DESC');
    
    while($row = $results->fetchArray()) {
        print("URL: ".$row['url'].' spoken by '.$row['spoken_by'].' and repated '.$row['count']."<br>\n");
    }
?>
</body>
</html>