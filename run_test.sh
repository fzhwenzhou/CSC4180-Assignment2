# Scanning with lex
for file in testcases/*
do
    echo "Comparing result for $file:"
    python3 src/lex.py $file > $(basename $file).lex.out
    python3 src/scanner.py $file > $(basename $file).scanner.out
    diff $(basename $file).lex.out $(basename $file).scanner.out
    if [ $? = 1 ]
    then
        echo "Difference found in two outputs! Exiting."
        exit 1
    fi
    echo "Test pass."
done

echo "All tests passed."
rm *.out