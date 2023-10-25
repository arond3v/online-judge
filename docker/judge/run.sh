result="{\n"
for input in "./input"/*; do
    output=$(timeout 2 ./run  $input "./output/$(basename $input)")
    if [ $? -eq 0 ]; then
        result+="$(basename $input):$output,\n"
    elif [ $? -eq 124 ]; then
        result+="$(basename $input):tle,\n"
    else 
        resutl+="$(basename $input):error,\n"
    fi
done
result=${result%,*}
result+="\n}"
echo -e $result