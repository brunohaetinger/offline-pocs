# Swap columns 1 and 2 in a CSV file with 3 columns

## vim

> :%s/\(.*\),\(.*\),\(.*\)/\2,\1,\3/g

## shell/awk

> awk -F',' '{print $2 "," $1 "," $3}' file.csv'

-F',' → use , as delimiter

{print $2 "," $1 "," $3} → print column2, column1, column3
