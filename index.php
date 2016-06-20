<?php
$legitfile = fopen('legit.txt', 'r+');
$sybilfile = fopen('sybil.txt', 'r+');
$legit = fgets($legitfile);
$sybil = fgets($sybilfile);

if (isset($_GET['sybil'])) {
    fseek($sybilfile, 0);
    $sybil += 1;
    fputs($sybilfile, $sybil);
} else if (isset($_GET['legit'])) {
    fseek($legitfile, 0);
    $legit += 1;
    fputs($legitfile, $legit);
    fclose($legitfile);
}

echo "Legit: $legit";
echo "Sybil: $sybil";
?>
