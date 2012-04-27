#!/bin/bash
#

echo "Minifying javascript"
for infile in $(find . -type f -name "*_uncompressed.js"); do
    output_file=$(echo $infile|sed -e 's:_uncompressed::')
    java -jar ~/Documents/devel/java/yuicompressor-2.4.7.jar --charset utf-8 --type js -o $output_file  $infile
    echo -e "\t$infile\t\t\t-> $output_file"
done
echo "Minifying CSS"
for infile in $(find . -type f -name "*_uncompressed.css"); do
    output_file=$(echo $infile|sed -e 's:_uncompressed::')
    java -jar ~/Documents/devel/java/yuicompressor-2.4.7.jar --charset utf-8 --type css -o $output_file  $infile
    echo -e "\t$output_file"
done