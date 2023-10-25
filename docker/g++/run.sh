#!/bin/bash
std="c++20"
result="{\n"
error=$(g++ code.cpp --std="$std" -o program 2>&1)
if [ $? -eq 0 ]; then
    result+="\"status\":\"processing\",\n"
    result+="\"test_case\":{\n"
    for input in "./input"/*; do
        if [ -f "$input" ]; then
            result+="\"$(basename $input)\":{\n"
            output=$(timeout 2 ./program < "$input")
            if [ $? -eq 0 ]; then
                result+="\"status\":\"processing\",\n"
            elif [ $? -eq 124 ]; then
                result+="\"status\":\"tle\"\n,"
            else 
                result+="\"status\":\"runtime error\",\n"
            fi
            result+="\"output\":\"$output\"\n},\n"
        fi
    done
    result=${result%,*}
    result+="\n}"
else 
    result+="\"status\":\"compilation error\",\n"
    result+="\"output\":\"$error\""
fi
result+="\n}"
echo -e "$result" 
